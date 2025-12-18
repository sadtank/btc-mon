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


## Want a pre-built setup?

I'll configure one for you. Donation is optional. BTC preferred.

1. Contact me @sadtank:matrix.org. (Allow a few days for my initial response).
2. I can recommend hardware, you buy.
3. Ship them to me. (SD card at minimum, recommend sending all hardware.)
4. I configure, test, and send back.
5. You pay return shipping and send me labels.

I cannot guarantee hardware, software, or support. But I try to help whenever I can.

Pre-built benefits:
* With just a usb keyboard, you can easily put it on your wifi (and setup SSH). This makes it giftable.
* Just works.
  * Avoid installation, os and hardware config headaches.
  * Official and verified raspberry pi OS
  * Runs on boot, retries on error
  * OS optimized to minimize SD card writes (extends SD life)
  * Firewall configured
  * Removed unnecessary services
  * Telemetry disabled
  * I configure for dedicated use, but you can overlay other stuff later.


## Self install
It's all you.


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
* USB keyboard for setup (possibly a converter)


# Donations
bc1q0kztxyxlwr4aauhe3qhvwqsyy2aumxrk3mtqu0


