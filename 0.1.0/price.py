#!/usr/bin/env python3

import requests
import json
import os

CACHE_FILE = Path("/run/kraken_price_cache.json")
run_dir.mkdir(parents=True, exist_ok=True)

class PriceFetcher:
    def __init__(self):
        self.price = 0.0
        self.trend = "-"
        self.last_price = None
        self.request_error_count = 1

    def update(self):
        url = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            raw = resp.json()
            self.request_error_count = 0
            with open(CACHE_FILE, "w") as f:
                json.dump(raw, f)
            self.success = True
        except Exception:
            self.success = False
            self.request_error_count += 1
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "r") as f:
                    raw = json.load(f)
            else:
                print("Failed to fetch Kraken price and no cache available.")
                return

        try:
            data = raw["result"]["XXBTZUSD"]
            vwap = float(data["p"][1])
            ask = float(data["a"][0])
            bid = float(data["b"][0])
            avg = (ask + bid) / 2
            self.trend = "^" if avg > vwap else "v"
            self.price = vwap
        except KeyError:
            print("Error parsing Kraken API response")
