#!/usr/bin/env python3

from lcd import LCD
import select
import commands
import time
from datetime import datetime
import evdev
import signal
import subprocess
import termios
import sys
import tty
import json
import os
from dataclasses import asdict
from pathlib import Path

#testing
import block
import fees

class RawTerminal:
    def __init__(self, fd=sys.stdin.fileno()):
        self.fd = fd
        self.original_attrs = termios.tcgetattr(self.fd)

    def __enter__(self):
        tty.setraw(self.fd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.original_attrs)
        # Flush any leftover keystrokes
        termios.tcflush(self.fd, termios.TCIFLUSH)


def ask(lcd, question, clue, default="n", timeout=30):
    response = lcd.input(question, clue, timeout)
    if not response:
        return default
    if response.startswith(clue):
        response = response[len(clue):]
    return response.strip()

def first_boot():
    pass

def second_boot():
    pass
    
def check_interactive(lcd, config, SCRIPT_ROOT):
    lcd.line1 = "any key to setup"
    lcd.center(0, lcd.splash0, lcd.line1)
    
    print("btcmon.service has switched console to tty8 to prevent setup input from executing in interactive tty1 terminal")
    print("use 'sudo systemctl stop btcmon.service' to disble")
    print("see lcd screen for setup")

    if check_initial_keypress(config.wait_config):
        def handle_sigint(signum, frame):
            print("\nCaught Ctrl-C (SIGINT), exiting interactive mode")
            raise KeyboardInterrupt()

        # Setup Ctrl-C handler
        signal.signal(signal.SIGINT, handle_sigint)

        try:
            # Enter raw mode (suppress shell input echo)
            with RawTerminal():
                interactive(lcd, config, SCRIPT_ROOT)
        except KeyboardInterrupt:
            pass
        finally:
            # Restore default Ctrl-C handler
            signal.signal(signal.SIGINT, signal.default_int_handler)
            print("Exited interactive mode.")
    print("btcmon.service has switched console to tty1")
    subprocess.run(["chvt", "1"])

def update_helper(lcd, SCRIPT_ROOT):
    step = f"update btc-mon"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
    
        # if success ask if want to throw error, to restart service without creds
        # Include UI to set specific version, that runs (also no creds needed)
        #   ln -sfn 0.0.7/main.py current
        #   issues if owned by sadtank? maybe chown?
        # Set systemctl if error, rollback to previous version.
    
        lcd.output(0, step, "updating...")
        success, status = commands.update_btcmon(SCRIPT_ROOT)
        lcd.output(2, step, status)
        if not success:
            lcd.output(2, step, "(!) exiting")
            raise Exception("issue with update.")
        return 
    


def interactive(lcd, config, SCRIPT_ROOT):
    return_to_setup = True
    while return_to_setup:
        step = "show/edit setup"
        question = f"{step}?"
        expected_answer = "s/e/N: "
        default = "n"
        answer_edit = ["e", "edit"]
        answer_show = ["s", "show"]

        response = ask(lcd, question, expected_answer, default)
        if response.lower() in answer_show:
            show_ip_helper(lcd)
            ping_helper(lcd)
            check_timezone(lcd, config)
            show_json_file(lcd, config, SCRIPT_ROOT, "config")
            #show_json_file(lcd, config, SCRIPT_ROOT, "version")
            show_version_helper(lcd, config, SCRIPT_ROOT)
        elif response.lower() in answer_edit:
            setup_wifi(lcd)
            ssh_helper(lcd)
            config = edit_config_interactively(lcd, config, "config")
            write_config(lcd, config, SCRIPT_ROOT, "config")
            set_timezone_helper(lcd, config)
            ntp_helper(lcd)
            update_helper(lcd, SCRIPT_ROOT)
            #edit config file?
            

        step = "re-enter setup"
        question = f"{step}?"
        expected_answer = "y/N: "
        default = "n"
        answer_check = ["y", "yes"]

        response = ask(lcd, question, expected_answer, default)
        if response.lower() not in answer_check:
            return_to_setup = False          
    
    lcd.center(0, lcd.splash0, "exiting setup")
    

def set_timezone_helper(lcd, config):
    step = f"set os timezone"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        lcd.output(0, step, config.timezone)
        lcd.scroll_text(1, config.timezone)
        lcd.output(0, step, "setting...")
        success, status = commands.change_os_timezone(config)
        try:
            lcd.output(0, step, status)
            lcd.scroll_text(2, status)
        except Exception as e:
            lcd.output(2, step, "(!) unk tz error")
            print(f"unexpected tz return: {e}")
        
def edit_config_interactively(lcd, config, file):
    """
    Edit the configuration interactively via LCD input, and keep the config as a Config object.
    """
    step = f"edit {file}"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    # Ask if the user wants to edit the config
    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        lcd.output(2, "null values will", "be ignored")
        # Iterate through each attribute of the config (using __dict__ to access class attributes)
        for key, current_value in config.__dict__.items():
            # Display key and current value, allowing interactive editing
            new_val = lcd.input(f"{key}: ", str(current_value), timeout=30)
            # If no new value is provided (None or empty), retain the current value
            if new_val is None or new_val.strip() == "":
                continue  # Keep the current value
            else:
                # Update the attribute in the config object directly
                # We assume that the new value can be safely cast to the original type of the attribute
                try:
                    # Try casting the value back to the original type of the attribute
                    original_type = type(current_value)
                    updated_value = original_type(new_val.strip())
                    setattr(config, key, updated_value)  # Update the config object with the new value
                except ValueError as e:
                    # Handle the case where casting fails (i.e., invalid input)
                    lcd.output(2, f"Invalid input for {key}. Keeping previous value.")
                    continue

        # Return the updated config object (still a Config instance)
        return config
    else:
        return config  # Return the original config if no changes were made


import json

def config_to_dict(config):
    """
    Convert the Config object to a dictionary without changing data types (e.g., int remains int).
    """
    config_dict = {}
    
    # Iterate through the config object attributes and store them in a dictionary
    for key, value in config.__dict__.items():
        config_dict[key] = value
    
    return config_dict

def write_config(lcd, config, SCRIPT_ROOT, file):
    """
    Write the updated configuration (Config object) back to a JSON file, preserving data types.
    """
    step = f"write {file}"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    # Ask if the user wants to save the config
    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        # Full file path to save the configuration
        FILE_PATH = os.path.join(SCRIPT_ROOT, f"{file}.json")
        
        try:
            # Convert the config object to a dictionary while preserving the types
            config_dict = config_to_dict(config)
            
            # Write the config data back to the file in JSON format
            with open(FILE_PATH, "w") as f:
                json.dump(config_dict, f, indent=4)

            lcd.output(1, step, "save successful")
            
            lcd.output(0, step, "reload config...")
            try:
                # Reload the config from the JSON file (assuming commands.load_config handles deserialization)
                config = commands.load_config(FILE_PATH)
                lcd.output(1, step, "reloaded")
                return config
            except Exception as e:
                lcd.output(1, step, "reload failed")
                print(f"Error reloading config: {e}")
        
        except Exception as e:
            lcd.output(1, step, "save failed")
            print(f"Error writing config: {e}")


def show_version_helper(lcd, config, SCRIPT_ROOT):
    step = "show version"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        # Suppose we want the directory of the config file itself
        folder_name = SCRIPT_ROOT.name

        lcd.output(2, "version", folder_name)
        lcd.output(2, "author", "sadtank")
        lcd.output(2, "license", "MIT")
    

def show_json_file(lcd, config, SCRIPT_ROOT, file):
    step = f"show {file}"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        FILE_PATH = os.path.join(SCRIPT_ROOT, f"{file}.json")

        with open(FILE_PATH, 'r') as f:
            data = json.load(f)

        for key, value in data.items():
            lcd.output(0, str(key), str(value))
            lcd.scroll_text(3, str(value))
            
def ntp_helper(lcd):
    step = "ntp connect"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        lcd.output(0, step, "connecting...")
        success, status = commands.chrony_ready(30)
        try:
            lcd.output(2, step, status)
        except:
            lcd.output(2, step, "(!) exiting")
            raise "ntp could didn't return a response, exiting."
        return 


def ssh_helper(lcd):
    step = "toggle ssh"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        response = ask(lcd, "on=1 off=0:", "", 1)
        try:
            flippedResponse = "1" if response == "0" else "0" #raspi-config uses 1 for off, 0 for on... I refuse  to ask users to use 1 for off... because that's stupid. so xor it is.
            lcd.output(2, step, "setting...")
            success, status = commands.toggle_ssh(int(flippedResponse))
            lcd.output(2, step, status)
        except:
            lcd.output(2, step, "(!) try 1 or 0")

def show_ip_helper(lcd):
    #show ip
    step = "wlan0 ip"
    question = f"Show {step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        ip = commands.get_ip_address("wlan0")
        if ip:
            lcd.output(5, step, ip)
        else:
            lcd.output(3, step, "none set")

def ping_helper(lcd):
    step = "ping 1.1.1.1"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        lcd.output(0, step, "pinging...")
        successes, failures = commands.ping_host("1.1.1.1", 4)
        lcd.output(2, step, f"{successes}/4 succeeded")
        print(f"Success: {successes}, Failures: {failures}")

def setup_wifi(lcd):
    step = "setup wifi"
    stepMain = step
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]

    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        ssid = ask(lcd, "enter ssid:", "")
        if ssid is None:
            lcd.output(3, "timed out", "or no input")
            raise RuntimeError("Timed out or no input.")
        else:
            psk = ask(lcd, "psk:", "")
            if psk is None:
                lcd.output(3, "timed out", "or no input")
                raise RuntimeError("Timed out or no input.")
            else:
                response = ask(lcd, "hidden ssid", expected_answer, default)
                if response.lower() in answer_check:
                    hidden = "1"
                else:
                    hidden = "0"
                    
                step = "country code"
                question = f"{step}?"
                expected_answer = "y/N: "
                default = "n"
                answer_check = ["y", "yes"]
                countryCode = ask(lcd, question, "")
                if countryCode is None:
                    lcd.output(3, "timed out", "or not input")
                    raise RuntimeError("Timed out or no input.")
                else:
                    lcd.output(0, step, f"setting {countryCode.upper()}...")
                    success = commands.set_wifi_country(countryCode.upper())
                    if success:
                        lcd.output(0, step, f"set to {countryCode.upper()}")
                    else:
                        lcd.output(1, step, "(!) fail")
                        #raise RuntimeError("failed to set country code")
                    lcd.output(1, stepMain, "connecting...")  
                    success = commands.set_wifi_credentials(ssid, psk, hidden=int(hidden), plain=1)
                    if success:
                        lcd.output(1, stepMain, "connected!")
                    else:
                        lcd.output(1, stepMain, "(!) fail")
                        #raise RuntimeError("failed to connect to wifi")

def check_timezone(lcd, config):
    step = "check timezone"
    question = f"{step}?"
    expected_answer = "y/N: "
    default = "n"
    answer_check = ["y", "yes"]
    
    response = ask(lcd, question, expected_answer, default)
    if response.lower() in answer_check:
        os_timezone = commands.get_os_timezone()
        lcd.output(0, "os tz:", os_timezone)
        lcd.scroll_text(3, os_timezone)
        lcd.output(0, "config tz:", config.timezone)
        lcd.scroll_text(3, config.timezone)
        lcd.output(1, "auto tz:", "checking...")
        success, response = commands.get_timezone()
        if success:
            lcd.output(0, "auto tz:", response['timezone'])
            lcd.scroll_text(3, response['timezone'])
        else:
            lcd.output(4, "auto tz::", response)
        

def check_initial_keypress(timeout=5):
    devices = []
    for path in evdev.list_devices():
        try:
            device = evdev.InputDevice(path)
            devices.append(device)
        except Exception:
            continue  # skip devices we can't open

    if not devices:
        time.sleep(timeout)
        return False

    start_time = time.time()
    while time.time() - start_time < timeout:
        timeout_left = timeout - (time.time() - start_time)
        r, _, _ = select.select(devices, [], [], timeout_left)
        for device in r:
            try:
                for event in device.read():
                    if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                        key_event = evdev.ecodes.KEY.get(event.code, event.code)
                        print(f"Key pressed: {key_event}")
                        return True
            except BlockingIOError:
                continue
    return False
    
  
def screen_1_handler(lcd, config, price_now):
    info = "L24"
    time_fmt = "%I:%M" if config.time_format == 12 else "%H:%M"
    time_now = datetime.now().strftime(time_fmt)
    date_now = datetime.now().strftime("%m-%d-%Y")

    line0 = lcd.justify2(time_now, date_now)
    line1 = lcd.justify2(f"${price_now.price:.2f}{price_now.trend}", info)
    
    lcd.output(0,line0, line1)
        
def screen_2_handler(lcd, block_now, fees_now):
    line0 = lcd.justify2(str(block_now.height), f"{str(block_now.min_ago)} min")


    line1helper = f"{fees_now.fastest} {fees_now.half_hour} {fees_now.hour}"

    line1_0 = lcd.justify2("sat/vB", f"H{fees_now.fastest} M{fees_now.half_hour} L{fees_now.hour}")
    line1_1 = lcd.justify2("sat/vB", f"{fees_now.fastest} {fees_now.half_hour} {fees_now.hour}")
    line1_2 = lcd.justify2("s/vB", f"{fees_now.fastest} {fees_now.half_hour} {fees_now.hour}")
    # line1_3 = lcd.justify2("vB", f"{fees_now.fastest} {fees_now.half_hour} {fees_now.hour}")
    line1_3 = lcd.justify3(f"H{fees_now.fastest}", f"M{fees_now.half_hour}", f"L{fees_now.hour}")
    line1_4 = lcd.justify3(str(fees_now.fastest), str(fees_now.half_hour), str(fees_now.hour))

    # Get longest fit
    options = [line1_0, line1_1, line1_2, line1_3, line1_4]
    line1 = max((s for s in options if len(s) <= 16), key=len, default=line1_4)
    
    lcd.output(0,line0, line1)

''' opting instead for auto restart on the system.
def screen_3_handler(lcd, block_now, fees_now, price_now):
    line0 = lcd.justify2("api failures:")
    text = "block:{block_now.request_error_count} fees:{fees_now.request_error_count} price:{price_now.request_error_count}"
    lcd.output(0, step, text)
    lcd.scroll_text(2, text)
'''

'''
def keyborad_layout_handler(lcd):
    keyboard_dict = {
        "us (English - US)",
        "uk (English - UK)",
        "us-intl (English - US International)",
        "ca (English - Canada)",
        "au (English - Australia)",
        "ie (English - Ireland)",
        "nz (English - New Zealand)",
        "dvorak (US Dvorak)",
        "colemak (US Colemak)"
    }
    slected = lcd.select_from_dict(lcd, keyboard_dict, timeout=900)
    lcd.output(5, selected, "")
'''

    
def first_boot_handler(lcd, config):
    welcome_dict = {
        "first boot setup": "just a minute",
    }
    for key, value in welcome_dict.items():
        lcd.center(2, key, value)

def second_boot_handler(lcd, config):
    welcome_dict = {
        "whew! all done!": "",
        "let's get setup!": "",
        "grab a usb": "keyboard",
        "anything wired": "or via dongle."
    }
    for key, value in welcome_dict.items():
        lcd.center(3, key, value)
    
    step = "keyboard ready"
    question = f"{step}?"
    expected_answer = "y & enter: "
    default = "n"
    answer_check = ["y", "yes"]
    
    response = ask(lcd, question, expected_answer, default, timeout=900)
    if response.lower() in answer_check:
        welcome_dict = {
            "there you are!": "ok!",
            "i need to be": "configured.",
            "config can be": "with a keyboard.",
            "this next part": "is critical..."
        }
        for key, value in welcome_dict.items():
            lcd.center(4, key, value)
        
        step = "got pen/paper"
        question = f"{step}?"
        expected_answer = "y/N: "
        default = "n"
        answer_check = ["y", "yes"]
    
        response = ask(lcd, question, expected_answer, default, timeout=900)
        if response.lower() in answer_check:
            welcome_dict = {
            "write down...": "",
            "1: wifi": "",
            "2: timezone": "",
            "3: ntp": ""
            }
            for key, value in welcome_dict.items():
                lcd.center(5, key, value)
            repeat = True
            while repeat:
                step = "repeat that"
                question = f"{step}?"
                expected_answer = "Y/n: "
                default = "y"
                answer_check = ["n", "no"]
            
                response = ask(lcd, question, expected_answer, default, timeout=900)
                if response.lower() in answer_check:
                    repeat = False
            
            welcome_dict = {
            "you're going to": "enter config",
            "then edit those": "settings.",
            "it's easy.": "deep breath...",
            "i believe": "in you"
            }
            for key, value in welcome_dict.items():
                lcd.center(4, key, value)
        else:
            lcd.center(3, "drat. come back", "with pen/paper.")
            raise "no pen/paper. exiting"
    else:
        lcd.center(3, "drat. keyboard", "not detected.")
        raise "no keyboard, hit 15 min timeout. exiting"
    
            
            
if __name__ == "__main__":
    block_now = block.BlockMetadata()
    fees_now = fees.FeeStats()
    
    
    main()
    block_now.update()
    fees_now.update()
    
    screen_2_handler(block_now, fees_now)
