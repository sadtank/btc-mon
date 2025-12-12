#!/usr/bin/env python3

import socket
import os
import fcntl
import struct
import subprocess
import time
import requests
from dataclasses import dataclass
import json

def get_ip_address(ifname='wlan0'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        iface_bytes = ifname.encode('utf-8')
        packed_iface = struct.pack('256s', iface_bytes[:15])
        ip = fcntl.ioctl(s.fileno(), 0x8915, packed_iface)[20:24]
        return socket.inet_ntoa(ip)
    except OSError:
        return None  # Interface not found or no IP assigned
        
def ping_host(host="1.1.1.1", count=4):
    try:
        # Run the ping command
        result = subprocess.run(
            ["ping", "-c", str(count), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check if the command ran at all
        if result.returncode not in (0, 1):  # 1 = some packets lost
            return False, count

        # Parse the output for stats
        for line in result.stdout.splitlines():
            if "packets transmitted" in line:
                # Example: "4 packets transmitted, 4 received, 0% packet loss, time 8ms"
                parts = line.split(",")
                sent = int(parts[0].split()[0])
                received = int(parts[1].split()[0])
                failed = sent - received
                return received, failed

        # Fallback in case expected line not found
        return False, count

    except Exception as e:
        print(f"Error pinging host: {e}")
        return False, count

def get_os_timezone():
    result = subprocess.run(
        ["timedatectl", "show", "--property=Timezone", "--value"],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()

def change_os_timezone(config):
    if config.timezone == "auto" or config.timezone == "" or config.timezone == None:
        try:
            success, status = get_timezone()
            tz_data = status
            timezone = tz_data.get('timezone', 'unknown')
        except:
            return success, status
            
        #if succeeded, continue
        try:
            success, status = set_timezone(timezone)
            return success, status
        except Exception as e:
            return success, status
    else:
        try:
            success, status = set_timezone(config.timezone)
            return success, status
        except Exception as e:
            return False, e

def set_wifi_credentials(ssid, passphrase, hidden=0, plain=1):
    """
    Use raspi-config to set Wi-Fi SSID and passphrase.
    """
    cmd = [
        "sudo",
        "raspi-config",
        "nonint",
        "do_wifi_ssid_passphrase",
        ssid,
        passphrase,
        str(hidden),
        str(plain)
    ]

    try:
        subprocess.run(cmd, check=True)
        #time.sleep(3)
        return True
    except subprocess.CalledProcessError as e:
        return False
        
def set_wifi_country(country_code):
    """
    Set the Wi-Fi country code using raspi-config.

    :param country_code: 2-letter country code, e.g., "US", "GB", "DE"
    :return: True on success, False on failure
    """
    try:
        result = subprocess.run(
            ["sudo", "raspi-config", "nonint", "do_wifi_country", country_code],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        return False
        
        
def toggle_ssh(enable: int):
    """
    Enable or disable SSH using raspi-config nonint.
    :param enable: 0 to enable SSH, 1 to disable SSH
    """
    if enable not in (0, 1):
        #raise ValueError("Invalid value. Use 0 to enable SSH, 1 to disable SSH.")
        status = "(!) try 0 or 1"
        return False, status

    try:
        subprocess.run(["sudo", "raspi-config", "nonint", "do_ssh", str(enable)],
                       check=True)
        status = 'enabled' if enable == 0 else 'disabled'
        #time.sleep(1)
        return True, status
    except subprocess.CalledProcessError as e:
        #lcdout("ssh",f"fail: {e}")
        #time.sleep(1)
        #raise RuntimeError(f"Failed to toggle SSH: {e}")
        status = "(!) toggle fail"
        return False, status


import subprocess
import time

def systemd_timesyncd_ready(timeout=15, poll_interval=1):
    """
    Wait up to `timeout` seconds for systemd-timesyncd to report synchronization.
    Returns (True, "connected") if synced,
            (False, "timeout") if not synced within timeout,
            (False, "error") if timedatectl fails or returns unexpected output.
    """
    for i in range(timeout):
        try:
            # Run timedatectl to check NTP synchronization status
            result = subprocess.check_output(
                ["timedatectl", "show", "--property", "NTPSynchronized", "--value"],
                text=True
            ).strip()

            # Check if NTP synchronization is confirmed
            if result == "yes":
                return True, "ntp: connected"
        
        except subprocess.CalledProcessError:
            # timedatectl command ran but returned a nonzero exit code
            return False, "ntp: unk error"
        except FileNotFoundError:
            # timedatectl is not found on the system
            return False, "ntp: missing?"

        # Optional: Log or display progress (if you want)
        # print(f"Waiting for NTP sync: {i + 1}/{timeout}...")
        
        time.sleep(poll_interval)

    return False, "ntp: timeout"
    

def get_timezone():
    try:
        url = f'http://ip-api.com/json'
        response = requests.get(url)
        data = response.json()

        return True, data
    except Exception as e:
        status = "(!) ipp-api.com"
        print(f"error: {e}")
        return False, status
        

def set_timezone(timezone):
    try:
        subprocess.run(["sudo", "timedatectl", "set-timezone", timezone])
        status = f"set: {timezone}"
        return True, status
    except:
        status = "(!) set zone"
        return False, status
        
        
@dataclass
class Config:
    time_format: str
    wait_scr_chg: int
    wait_meta: int
    wait_price: int
    block_splash: int
    wait_config: int
    timezone: str
    api_failures: int
    vers_loc: str
    
def create_default_config(path: str):
    default_config = {
        "time_format": 24,
        "wait_scr_chg": 6,
        "wait_meta": 10,
        "wait_price": 60,
        "block_splash": 1,
        "wait_config": 3,
        "timezone": "auto",
        "api_failures": 20,
        "vers_loc": "current"
    }
    with open(path, "w") as f:
        json.dump(default_config, f, indent=4)
    return default_config    

def load_config(path: str) -> Config:
    if not os.path.exists(path):
        lcd.center(2,"missing", "config file")
        lcd.center(2,"creating file", "using defaults")
        config_data = create_default_config(path)
        #raise RuntimeError("Config file created. Please restart the program.")
    with open(path) as f:
        data = json.load(f)
    return Config(**data)
    
    
def try_all_networks():
    # Get all wired + Wi-Fi connections
    conns = subprocess.check_output(
        ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"], text=True
    ).splitlines()
    
    relevant = [c.split(":")[0] for c in conns if c.split(":")[1] in ("wifi", "ethernet")]
    
    # Trigger connection attempts
    for name in relevant:
        subprocess.run(["nmcli", "connection", "up", name], check=False)
    
    # Poll for success/failure of all attempts
    while True:
        active = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,TYPE,STATE", "connection", "show", "--active"], text=True
        ).splitlines()

        # Only consider ethernet or wifi
        relevant_active = [
            line for line in active if line.split(":")[1] in ("ethernet", "wifi")
        ]

        if any("activated" in line for line in relevant_active):
            return True  # success
        if all("deactivated" in line for line in relevant_active):
            return False  # all attempts failed
        
        time.sleep(0.1)  # lightweight polling
        
        
def update_btcmon(SCRIPT_ROOT):
    repo_path = SCRIPT_ROOT.parent
    repo_url = "https://github.com/user/btc-mon"
    commands = [
        ["git", "init"],
        ["git", "remote", "remove", "origin"],
        ["git", "remote", "add", "origin", repo_url],
        ["git", "fetch", "origin"],
        ["git", "reset", "--hard", f"origin/{branch}"],
        ["git", "clean", "-fdx"]
    ]
    for cmd in commands:
        # ignore errors for removing origin if it doesn't exist
        try:
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            if "remove" in cmd and "origin" in cmd:
                # safe to ignore
                continue
            status = "update failed"
            return False, status

    status = "update success"
    return True, status


    try:
        subprocess.run(["sudo", "timedatectl", "set-timezone", timezone])
        status = f"set: {timezone}"
        return True, status
    except:
        status = "(!) set zone"
        return False, status
