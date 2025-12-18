#!/usr/bin/env python3

import requests

class FeeStats:
    def __init__(self):
        self.fastest = "?"
        self.half_hour = "?"
        self.hour = "?"
        self.economy = "?"
        self.request_error_count = 0

    def update(self):
        try:
            fees = requests.get("https://mempool.space/api/v1/fees/recommended").json()
            self.fastest = fees.get("fastestFee", "?")
            self.half_hour = fees.get("halfHourFee", "?")
            self.hour = fees.get("hourFee", "?")
            self.economy = fees.get("economyFee", "?")
            self.request_error_count = 0
            self.success = True
        except Exception as e:
            self.success = False
            self.request_error_count += 1
            print(f"Error fetching fees: {e}")


def main():
    pass


if __name__ == "__main__":
    main()
