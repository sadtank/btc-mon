#!/usr/bin/env python3

import os
import time
import json
from lcd import LCD
#from settings import Settings
#from command_flow import CommandFlow
import ui
import block
import fees
import price
import commands
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_ROOT.parent / "config.json"


def main():

    #objects
    block_now = block.BlockMetadata()
    fees_now = fees.FeeStats()
    price_now = price.PriceFetcher()
    lcd = LCD()
    config = commands.load_config(CONFIG_FILE)
    
    #ui.keyborad_layout_handler(lcd)
    
    lcd.center(2, "stay humble", "stack sats")
    lcd.splash0 = "BTC  MON"
    lcd.line1 = ""
    lcd.center(0, lcd.splash0, lcd.line1)
    
    #ui.first_boot_handler(lcd, config)
    #ui.second_boot_handler(lcd, config)
    
    
    
    ui.check_interactive(lcd, config, SCRIPT_ROOT)
    

    lcd.center(0, lcd.splash0, "getting ip")
    if not commands.get_ip_address():
        if not commands.try_all_networks():        
            lcd.center(2, lcd.splash0, "no ip, plz setup")
            raise RuntimeError("no ip, plz setup, exiting")
    
    success, count = commands.ping_host()
    if not success:
        lcd.center(2, lcd.splash0, "ping! offline?")
        raise RuntimeError("ping! offline?")
    
    lcd.center(0, lcd.splash0, "getting ntp")
    success, status = commands.systemd_timesyncd_ready()
    if not success:
        lcd.center(0, lcd.splash0, status)
        raise RuntimeError("ntp failed after timeout")

    lcd.center(0, lcd.splash0, "getting block")
    block_now.update()
        #check for error count in block_now.request_error_count
    lcd.center(0, lcd.splash0, "getting fees")
    fees_now.update()
    lcd.center(0, lcd.splash0, "getting price")
    price_now.update()


    epoch_now = int(time.time())
    epoch_flip = int(time.time())
    last_meta_epoch = epoch_now
    last_price_epoch = epoch_now
    use_Screen = 0
    apiWasCalled = 0
    while True:
        epoch_now = int(time.time())

        if epoch_now - last_meta_epoch >= config.wait_meta:
            block_now.update()
            fees_now.update()
            last_meta_epoch = epoch_now
            apiWasCalled = 1
            if block_now.new_block:
                lcd.output(2, "+--NEW  BLOCK--+", "|______________|")
                block_now.new_block = False
        
        if epoch_now - last_price_epoch >= config.wait_price:
            price_now.update()
            last_price_epoch = epoch_now
            apiWasCalled = 1
        
        #if time to flipp
        if epoch_now >= epoch_flip:
            use_Screen = (use_Screen + 1) %2 #where %n is the number of screens
            epoch_flip = int(time.time()) + config.wait_scr_chg 
        
        match use_Screen:
            case 0:
                ui.screen_1_handler(lcd, config, price_now)         
            case 1:
                ui.screen_2_handler(lcd, block_now, fees_now)
            case _:
                lcd.center(0, "screen case err", "exiting")
                raise RuntimeError("screen case err")
            
        if apiWasCalled:
            #print (f"{block_now.request_error_count}, {fees_now.request_error_count}, {price_now.request_error_count}")
            failures = sum([block_now.request_error_count, fees_now.request_error_count, price_now.request_error_count])
            if ( failures >= config.api_failures):
                lcd.center(2, f"API failures: {failures}", "exiting")
                raise RuntimeError(f"too many API failures: {failures}")
        apiWasCalled = 0
        #check decimal on price
        
        time.sleep(1)
        #time.sleep(config.wait_scr_chg)
    
    
    # echo()
    #ui.first_boot()
    #ui.second_boot()
    #ui.main_splash()
    
    
    
    lcd.clear()
    lcd.close()


if __name__ == "__main__":
    main()
