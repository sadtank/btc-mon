#!/usr/bin/env python3

import sys
import termios
import tty
import select
import time
from pathlib import Path
# Get path to the parent folder: /path/to/mainfolder
PARENT_DIR = Path(__file__).resolve().parent.parent
# Add parent folder to Python search path
sys.path.insert(0, str(PARENT_DIR))
# Now Python will look in mainfolder/ for imports
import LCD1602

class LCD:
    def __init__(self, cols=16, rows=2):
        self.cols = cols
        self.rows = rows
        self.lcd = LCD1602.LCD1602(cols, rows)
        self.line0 = ""
        self.line1 = ""

    def clear(self):
        self.lcd.clear()

    def _print_line(self, line_num, text, clear=True):
        self.lcd.setCursor(0, line_num)
        if clear:
            self.lcd.printout(" " * self.cols)
            self.lcd.setCursor(0, line_num)
        self.lcd.printout(text[:self.cols])

    def output(self, sleep_time=0, line0="", line1="", clear_line0=True, clear_line1=True):
        self._print_line(0, line0, clear_line0)
        self._print_line(1, line1, clear_line1)
        time.sleep(int(sleep_time))

    def center(self, sleep_time=0, line0="", line1="", clear_line0=True, clear_line1=True):
        self._print_line(0, self._center_16(line0), clear_line0)
        self._print_line(1, self._center_16(line1), clear_line1)
        time.sleep(int(sleep_time))
        #self.output(sleep_time, self._center_16(line0), self._center_16(line1))

    def justify2(self, left, right):
        return self._justify2_16(left, right)

    def justify3(self, w1, w2, w3):
        return self._justify3_16(w1, w2, w3)

    def close(self):
        del self.lcd

    # --- lcd_input method ---
    def input(self, prompt_line0, initial_text="", timeout=None):
        """
        Let the user type, outputing keystrokes on the 2-line 16-char LCD.
        - prompt_line0: text to display on LCD line 0
        - initial_text: starting buffer (string)
        - timeout: optional overall timeout in seconds (None = wait indefinitely)
        Returns the final string when Enter pressed, or None on timeout/EOF.
        """
        def render_buf(buf):
            s = buf[-self.cols:]  # output last 16 chars
            return s.ljust(self.cols)

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        buf = initial_text or ""

        start = time.time()
        try:
            tty.setraw(fd)
            self.output(0, prompt_line0[:self.cols], render_buf(buf))
            while True:
                if timeout is not None:
                    elapsed = time.time() - start
                    if elapsed >= timeout:
                        return None
                    sel_timeout = max(0, timeout - elapsed)
                else:
                    sel_timeout = None

                rlist, _, _ = select.select([sys.stdin], [], [], sel_timeout)
                if not rlist:
                    return None

                ch = sys.stdin.read(1)
                if ch == "\x03":
                    raise KeyboardInterrupt
                if ch in ("\r", "\n"):
                    self.output(0, prompt_line0[:self.cols], render_buf(buf))
                    print()
                    return buf
                if ch in ("\x7f", "\b"):
                    if buf:
                        buf = buf[:-1]
                        self.output(0, prompt_line0[:self.cols], render_buf(buf))
                    continue
                if ord(ch) < 32:
                    continue

                buf += ch
                self.output(0, prompt_line0[:self.cols], render_buf(buf))
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            #clear any key presses so they don't go to terminal
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
    
    def select_from_dict(lcd, options_dict, timeout):
        """
        Scrollable UI to choose an option from a dictionary.
        Arrow Up/Down scrolls, Enter selects. Returns the selected key.
        """
        options = list(options_dict.items())
        index = 0

        def render():
            key, value = options[index]
            lcd.center(0, key, value)

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            render()
            start = time.time()

            while True:
                if timeout is not None:
                    elapsed = time.time() - start
                    if elapsed >= timeout:
                        return None
                    sel_timeout = max(0, timeout - elapsed)
                else:
                    sel_timeout = None

                rlist, _, _ = select.select([fd], [], [], sel_timeout)
                if not rlist:
                    return None

                ch = sys.stdin.read(1)
                if ch == "\x1b":  # possible arrow key (starts with ESC)
                    next1 = sys.stdin.read(1)
                    next2 = sys.stdin.read(1)
                    if next1 == "[":
                        if next2 == "A":  # Up
                            index = (index - 1) % len(options)
                            render()
                        elif next2 == "B":  # Down
                            index = (index + 1) % len(options)
                            render()
                elif ch in ("\r", "\n"):
                    return options[index][0]
                elif ch == "\x03":
                    raise KeyboardInterrupt
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            termios.tcflush(fd, termios.TCIFLUSH)

    # ---- Private formatting helpers ----
    def _center_16(self, text):
        if len(text) >= self.cols:
            return text[:self.cols]
        padding = self.cols - len(text)
        left = (padding + 1) // 2
        right = padding - left
        return " " * left + text + " " * right

    def _justify2_16(self, left, right):
        space_count = self.cols - len(left) - len(right)
        if space_count < 1:
            return f"{left}{right}"
        return f"{left}{' ' * space_count}{right}"

    def _justify3_16(self, w1, w2, w3):
        total_word_len = len(w1) + len(w2) + len(w3)
        total_spaces = self.cols - total_word_len
        if total_spaces < 2:
            return f"{w1}{w2}{w3}"
        gap1 = total_spaces // 2
        gap2 = total_spaces - gap1
        return f"{w1}{' ' * gap1}{w2}{' ' * gap2}{w3}"

    def scroll_text(self, delay_after_scroll=2, text="(null str)", line_num=1, delay=0.2):
        """
        Scrolls text horizontally on the specified LCD line, and adds an additional delay
        after the scrolling is done.
        
        :param delay_after_scroll: The delay in seconds after the scrolling is finished.
        :param text: The text to display, which will scroll if it exceeds the screen width.
        :param line_num: The line (0 or 1) to display the text.
        :param delay: The delay in seconds between each scroll movement.
        """
        # If text length is greater than the display width, scroll it.
        if len(text) > self.cols:
            time.sleep(1) #pause so first char won't blow by
            # Repeat the scrolling by moving the starting position across the text
            for i in range(len(text) - self.cols + 1):
                # Display a substring of 'cols' characters starting from index i
                self._print_line(line_num, text[i:i + self.cols], clear=False)
                time.sleep(delay)
        else:
            # If text fits within the LCD width, display it normally
            self._print_line(line_num, text, clear=True)
        
        # After scrolling, wait for the specified delay (in seconds)
        time.sleep(delay_after_scroll)



def main():
    #from lcd import LCD

    lcd = LCD()

    lcd.center(1,"centered", "stuff")
    # or:
    lcd.output(1,"left:", "stuff")

    
    # clears line0 and line1
    lcd.output(1,"no clear........", "")
    # keep line0, clear line1
    lcd.output(1,"", "................", clear_line0=False)  
    # overwrite without clearing either line
    lcd.output(1,"Keep this", "No clear", clear_line0=False, clear_line1=False)  
    
    # For justified line creation:
    line0 = lcd.justify2("10:25", "2025-10-14")
    line1 = lcd.justify3("L400", "M850", "H83")
    lcd.output(1,line0, line1)
    
    #lcd.input
    user_input = lcd.input("Enter name:")
    lcd.output(1,"You typed:", user_input)
    
    # If you want to clear & release:
    lcd.close()

if __name__ == "__main__":
    main()

