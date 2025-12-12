# BTC-Monitor
A Bitcoin clock and price monitor script.

Isn't this just a [blockclock](https://store.coinkite.com/store/blockclock)? Nope. This is FOSS. 

Here's the features:
* Works with all raspberry pi SBCs with wifi
* Screen 1: 12 or 24 hr time and date
* Screen 1: Price in USD (kraken)
* Screen 1: Trend up/down (^/v) compared to 24hr Volume-Weighted Average Price (VWAP)
* Screen 2: Block height and age in minutes
* Screen 2: Sat/vB rates
* New block alert splash
* Built in error detection and troubleshooting


## Want a pre-built setup?

I'll configure one for you.

1. Contact me @sadtank:matrix.org. (Allow a few days for my initial response).
2. You buy the Raspberry Pi, Waveshare LCD, and SD card yourself.
3. Ship them to me.
4. I configure, test, and send back.
5. You pay shipping and send me label images; donation is optional.

I cannot guarantee hardware, software, or support. But I do try to help whenever I can.

Pre-built benefits:
* With just a usb keyboard, you can easily put it on your wifi (and setup SSH).
* Just works. Avoid installation, os and hardware config headaches.
  * Avoid installation, os and hardware config headaches.
  * Official and verified raspberry pi OS
  * Runs on boot, retries on error
  * Automatic BTC-MON updates
  * OS optimized to minimize SD card writes (extends SD life)
  * Firewall configured
  * Removed unnecessary services
  * Telemetry disabled
* I configure for dedicated use, but you can overlay other stuff later.


## Self install
It's all you.

# Waveshare LCD1602

This project is designed for use with the Waveshare LCD1602 I2C display.

**Important:** This repository does **not** include the Waveshare LCD driver. Waveshare may reserve all rights to their software, even though their drivers are freely and publicly available with no posted license (at this time).

If self-installing, purchase the display and download the official `LCD1602.py` driver script from Waveshare. Place this script in same folder as `main.py`, ensuring it has execute permissions.

Official driver link:
https://www.waveshare.com/wiki/LCD1602_I2C_Module
