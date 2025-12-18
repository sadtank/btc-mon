# BTC-Monitor
A Bitcoin clock and price monitor script.

Sure, the [Blockclock](https://store.coinkite.com/store/blockclock) is sleek... But if you want FOSS you can afford... Something customizable and a bit cyberpunk... then btc-mon is for you.

<img width="345" alt="btcmon1" src="https://github.com/user-attachments/assets/4121025c-9da5-4195-bef0-c20a9c783d44" />
<img width="345" height="380" alt="btcmon2" src="https://github.com/user-attachments/assets/5c666da6-5f46-44c3-8bc1-b8df9b6145f2" />

## Features:
* Works with all raspberry pi SBCs with built-in wifi
* Screen 1: 12 or 24 hr time and date
* Screen 1: Price in USD (kraken) and trend (^/v) compared to 24hr Volume-Weighted Average Price (VWAP)
* Screen 2: Block height and age in minutes
* Screen 2: Sat/vB mempool rates (high, medium, low priority)
* New block alert splash

DIY or pre-built options below.

## Pre-built setup
**I got this.**

1. Happy to help. contact me @sadtank:matrix.org. (Allow a few days for my initial response).
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


## Self install
**You got this.**

Single-use raspi:
1. Image using official raspberry [pi imager](https://www.raspberrypi.com/software/).
   * Recommend setting wifi and user `btcmon`.
   * Use the raspberry pi imager! Many imaging utilities do not explicitly write buffer to SD cards before ejecting media. Some versions of pi imager introduce bugs, so consider downgrading imager versions if you run into issues.
3. Connect the SD and peripherals, using [Waveshare](https://www.waveshare.com/wiki/LCD1602_I2C_Module) pinout (or look at image above).
4. Boot and `sudo raspi-config` to set keyboard layout, wifi country code, and wifi.
5. Install git with `sudo apt-get update && sudo apt-get install git -y` (No upgrade? That's right. More stable.)
6. Use `git clone --depth 1 https://github.com/sadtank/btc-mon.git`
7. Run setup from highest version folder, e.g., `sudo ./btc-mon/0.1.0/setup/bootstrap-ansible.sh`. Allow the playbook to finish completely.
   * _You are responsible for knowing what these scripts will do on your system._
8. Whenever the raspi boots, or when the btcmon.service starts, you can enter setup using just a usb keyboard and the LCD display.
9. (optional) If gifting the system, you can now remove the cached wifi creds and shutdown. Your recipient can simply connect a keyboard, boot, and configure using only the LCD display!
10. (optional) [send sats](#donations) for thanks!

Multi-use raspi:
If you're running other stuff on the pi already, the ansible bootstrap script may bork your existing install.
1. Eyeball the ansible playbook for dependencies and necessary config (e.g., I2C... AI is good at this.).
2. Modify and enable the unif file from the ansible playbook. Unit file executes the location of the `current` version symlink.
3. (optional) [send sats](#donations) for thanks!

While this setup is for raspi, the display manufacturer ([Waveshare](https://www.waveshare.com/wiki/LCD1602_I2C_Module)) does support Arduino and Jetson Nano. If all Waveshare scripts expose the same calls simply swap `LCD1602.py`. This _should_ work, if the device is configured properly. Your mileage may vary.


## Parts list
Easy mode: buy a [raspi kit](https://amzn.to/4s3M5dz) and a [Waveshare LCD](https://amzn.to/3XYQX61). 

At a minimum you need:
* [Waveshare LCD1602](https://amzn.to/495ZeKB)
** PH2.O 4PIN wire (connects LCD to pi, typically included with LCD)
* Raspi SBC [zero 2 WH](https://amzn.to/3L5Pgke) or even a [zero (1) WH](https://amzn.to/48LBPz5) will work fine:
  * capable of running Raspberry Pi OS
  * with onboard wifi
  * the "h" stands for pre-soldered header (e.g., Pi Zero 2 WH)
* [Quality SD card](https://amzn.to/3XYRzsl) (8gb+ if headless, 16gb+ if desktop, _reputable brands only_)
* [Stable 5V 3A power supply](https://amzn.to/4p45qsn)
* [Micro USB cable](https://amzn.to/4s690oC), consider how long you want the cable to be.
* Wall mount:
  * [Finish nails](https://amzn.to/3MHO7jo) through the mount holes
  * [3M Command Stripps](https://amzn.to/3MHOLgO) cut to size (keep the tab). (no residue, usually doesn't damage surfaces)
  * [3M Duel Lock](https://amzn.to/4apJfsW) to mount and adjust after (no residue left but may damage wall surfaces)
* Consider crafting a [case](https://www.thingiverse.com/thing:5952644)


## Config
*  `time_format`: str display clock in `24` or `12` hour increments. Note, there is no AM/PM indicator. (If unsure touch grass.)
*  `wait_scr_chg`: int seconds before switching screens, default `6`.
*  `wait_meta`: int seconds before checking [mempool.space](https://mempool.space/api/blocks/tip/hash), default `10`. (see api rate limits before reducing.)
*  `wait_price`: int seconds before checking [api.kraken](https://api.kraken.com/0/public/Ticker?pair=XBTUSD), default `60`. (see api rate limits before reducing.)
*  `block_splash`: int as bool to show silent alert when new block detected. `1` or `0`, default `1`.
*  `wait_config`: int seconds for interactive mode window on script start, default `3`.
*  `timezone`: str `auto` will detect from [ip-api.com](http://ip-api.com/json). (see api rate limits before reducing). To statically assign, enter a string from `timedatectl list-timezones`.
*  `api_failures`: int to restart service after N consecutive api failures, default `20`.


## Troubleshooting tips
* AI is your friend.
* Need more support? Send it to me for _pre-built setup_.
* _Should I update btc-mon from the interactive LCD menu?_ - Update will clobber everything in the folder with the current repo. You can rollback by pointing the symlink (`current`) at whichever version of main.py you want to run.
* _Ansible ran without errors but btc-mon isn't running on the screen_
  * Likely some issue with the unit file or systemctl... Did you use the suggested user (`btcmon`)? Did you change/modify the symlink to the current version? You'll need to dig through the logs to figure it out. Check the btcmon.service status and journalctl. 
* _Clean image buggered after 1-3 boots_
  * It's likely you have a cheap/bad card. Some cards pass checks but still fail. Try again using a known good card. Never had a problem with [these SD cards](https://amzn.to/3XYRzsl).
  * Try without updating eprom...
  * Try on a different version of pi os.
* _Other OS issues (e.g., getting on wifi)_
  * Try using pi imager v1.8.5 and trixie 64 bit headless.
  * In custom image settings show password, and verify.
  * Raspi may need a 2.4 network, check the docs, ensure you're broadcasting wap on 2.4.
* _Can't enter interactive mode to setup_
  * You can't enter interactive mode via SSH. This is because tty1 always receives input from connected keyboards, even without a monitor. To shield tty1 from keyboard input (which could execute commands) the script switches to a non-interactive tty when expecting any key for setup. This is a design trade-off, optimizing for the ability to configure with just usb keyboard and LCD, rather than requiring ssh or a monitor.


## Donations
bc1q0kztxyxlwr4aauhe3qhvwqsyy2aumxrk3mtqu0

<img width="166" height="165" alt="btc-wallet-qr" src="https://github.com/user-attachments/assets/01f79bfd-cc62-4e2d-920b-5310d661d14b" />
