# BTC-Monitor
A Bitcoin clock and price monitor script.

[Blockclock](https://store.coinkite.com/store/blockclock) is pretty cool... But if you want something FOSS that you can afford... something that actually shows a BTC-USD conversion... something more cyberpunk... something that you can customize... btc-mon is for you.

<img width="460" height="380" alt="btcmon1" src="https://github.com/user-attachments/assets/4121025c-9da5-4195-bef0-c20a9c783d44" />
<img caption="test" width="460" height="380" alt="btcmon2" src="https://github.com/user-attachments/assets/5c666da6-5f46-44c3-8bc1-b8df9b6145f2" />

## Features:
* Works with all raspberry pi SBCs with wifi
* Screen 1: 12 or 24 hr time and date
* Screen 1: Price in USD (kraken) and trend (^/v) compared to 24hr Volume-Weighted Average Price (VWAP)
* Screen 2: Block height and age in minutes
* Screen 2: Sat/vB mempool rates (high, medium, low priority)
* New block alert splash


## Self install
**You got this.**


1. Image using official raspberry pi imager. Recommend setting wifi and user `btcmon`. Trixie headless 64 and 32 should work fine. (Use the raspberry pi imager! Many imaging utilities do not explicitly write buffer to SD cards before ejecting media. Some versions of pi imager introduce bugs, so consider downgrading imager versions if you run into issues.)
2. Use `sudo raspi-config` to set wifi country code, keyboard layout, and wifi.
3. Install git with `sudo apt-get update && sudo apt-get install git -y`
4. Use `git clone --depth 1 https://github.com/sadtank/btc-mon.git`
5. Run setup from highest version folder, e.g., `sudo ./btc-mon/0.0.7/setup/bootstrap-ansible.sh`. Allow the playbook to finish completely.
   * _You are responsible for knowing what these scripts will do on your system._
6. Whenever the raspi boots, or when the btcmon.service starts, you can enter setup using just a usb keyboard and the LCD display.
7. (optional) If gifting the system, you can now remove the cached wifi creds and shutdown. Your recipient can simply power on with a keyboard plugged in, and perform all necessary configuration using only the LCD display!
8. (optional) [send sats](#donations) for thanks!


## Pre-built setup
**I got this.** Happpy to help.

1. Contact me @sadtank:matrix.org. (Allow a few days for my initial response).
2. I answer questions.
3. You buy hardware and ship SD card to me. (recommend sending all hardware for full testing/troubleshooting.)
4. You pay return shipping and send me the info/label.
5. I configure, test, and ship per the return label.
6. (optional) [send sats](#donations) for thanks!

I cannot guarantee service, hardware, software, or support. But I help whenever I can.

Pre-built benefits:
* Setup with just a usb keyboard and the LCD! (This makes it giftable too...)
* Just works:
  * Btc-mon runs on boot
  * Avoid installation, os, and hardware headaches.
  * Official and verified raspberry pi os distro
  * OS optimized to minimize SD card writes (extends SD life)
  * Firewall configured
  * Unnecessary services removed
  * Telemetry disabled
  * Updates disabled (prioritizes stability)


# Minimum Parts
Easy mode: buy a [raspi kit](https://www.amazon.com/s?k=canakit) and a [Waveshare LCD](https://www.amazon.com/dp/B0DY7QTDXG). 

At a minimum you need:
* Waveshare LCD1602
* PH2.O 4PIN wire (connects LCD to pi, typically included with LCD purchase)
* Raspi SBC:
  * capable of running Raspberry Pi OS
  * with onboard wifi
  * pre-soldered GPIO pins (preferred)
* Quality SD card (5GB or more, _reputable brands only_)
* _Stable_ 5V 3A power supply
* Micro USB cable


# Troubleshooting tips
* _Should I update btc-mon from the interactive LCD menu?_ - Update will clobber everything in the folder with the current repo. You can rollback by pointing the symlink ("current") at whichever version of main.py you want to run.
* _Ansible ran without errors but btc-mon isn't running on the screen_
  * Likely some issue with the unit file or systemctl... Did you use the suggested user (btcmon)? Did you change/modify the symlink to the current version? You'll need to dig through the logs to figure it out. Check the btcmon.service status and journalctl. 
* _Clean image buggered after 1-3 boots_
  * It's likely you have a cheap/bad card. Some cards pass checks but still fail. Try again using a known good card. Never had a problem with [these SD cards](https://www.amazon.com/dp/B073K14CVB).
  * Try without updating eprom...
  * Try on a different version of pi os.
* _Can't enter interactive mode to setup_
  * You can't enter interactive mode via SSH. Why? Headless always has tty1 receiving input from keyboard. This means configuring keystrokes from hitting tty1 (and possibly running commands without knowing). To shield tty1 from keyboard input the script switches to non-interactive tty when expecting any key for setup. This was a design trade-off, optimizing for the ability to configure with just usb keyboard and LCD, rather than ssh.
* AI is your friend.
* Need more support? Send it to me for _pre-built setup_.


# Donations
bc1q0kztxyxlwr4aauhe3qhvwqsyy2aumxrk3mtqu0

<img width="166" height="165" alt="btc-wallet-qr" src="https://github.com/user-attachments/assets/01f79bfd-cc62-4e2d-920b-5310d661d14b" />
