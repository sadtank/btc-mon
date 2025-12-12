#!/usr/bin/env python3

import requests
import time
import block
import fees

class BlockMetadata:
    def __init__(self):
        self.hash = None
        self.timestamp = 0
        self.height = 0
        self.new_block = False
        self.request_error_count = 0
        self.epoch_now = int(time.time())

    def update(self):
        try:
            new_hash = requests.get("https://mempool.space/api/blocks/tip/hash", timeout=5).text.strip()
            if new_hash != self.hash:
                self.new_block = True

                metadata = requests.get(f"https://mempool.space/api/block/{new_hash}", timeout=5).json()
                self.hash = metadata.get("id", self.hash)
                self.timestamp = metadata.get("timestamp", 0)
                self.height = metadata.get("height", 0)
                self.epoch_now = int(time.time())
                self.min_ago = max(0, round((time.time() - self.timestamp) / 60))
                self.success = True
            else:
                self.epoch_now = int(time.time())
                self.min_ago = max(0, round((time.time() - self.timestamp) / 60))
                self.success = True
                self.new_block = False
                
            self.request_error_count = 0
            
        except Exception as e:
            self.success = False
            self.request_error_count += 1
            print(f"Error fetching block metadata: {e}")
            self.new_block = False
        return self

def main():
    pass


if __name__ == "__main__":
    main()
