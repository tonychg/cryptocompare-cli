#!/usr/bin/python3.5
# coding: utf-8

"""

    Author  : github/TonyChG
    Purpose : Fetch data from cryptocompare.com API
    Usage   : ./crypto

"""

import cryptocompare
import curses
from datetime import datetime, timedelta
from time import sleep

KEY_BACKSPACE=127
KEY_RETURN=10

def get_spin_sign(tick):
    SPINNER=['←', '↖', '↑', '↗', '→', '↘', '↓', '↙']
    return SPINNER[tick % len(SPINNER)]

def is_ascii(s):
    return s >= 33 and s < 127

class Coin:
    def __init__(self, symbol, curr='EUR', data=None):
        self.symbol = symbol
        self.curr = curr
        self.data = data
        self.value = None
        self.last_value = None
        self.last_udpdate = None

    @staticmethod
    def fetch_all():
        return cryptocompare.get_coin_list(format=False)

    def fetch_value(self, curr):
        self.curr = curr
        if self.value:
            self.last_value = self.value
        self.value = cryptocompare.get_price(self.symbol, curr=self.curr)
        if self.value:
            self.value = float(self.value[self.symbol][self.curr])
            self.last_udpdate = datetime.now()

    def format_value(self):
        value = str(self.value)
        if self.last_value and self.value - self.last_value:
            if self.last_value < self.value:
                sign = '+'
            else:
                sign = ''
            value += ' ({}{:.1f})'.format(sign, self.value - self.last_value)
        return "{} {}".format(value, self.curr)

    def format_timedelta(self):
        formated_time = "Refresh "
        time = datetime.now() - self.last_udpdate
        if time.seconds / 60 >= 1:
            minutes = int(time.seconds / 60)
            seconds = int(time.seconds % 60)
            formated_time += "{} min".format(str(minutes))
            formated_time += " {} sec".format(str(seconds))
        else:
            formated_time += "{} sec".format(str(time.seconds))
        return formated_time

class Window:
    def __init__(self, stdscr):
        self.title = "Cryptocompare.com API CLI by TonyChG"
        self.menu = [
            { "key": "F1 >", "action": "EUR" },
            { "key": "F2 >", "action": "Get list" },
            { "key": "F3 >", "action": "Clear" },
            { "key": "F4 >", "action": "Quit" },
            { "key": "F5 >", "action": "Refresh" },
        ]

        self.keybindings = {
            curses.KEY_F1: self.switch_curr,
            curses.KEY_F2: self.fetch_coins,
            curses.KEY_F3: self.init,
            curses.KEY_F4: self.quit,
            curses.KEY_F5: self.reload,
            curses.KEY_LEFT: self.prev_page,
            curses.KEY_RIGHT: self.next_page,
            KEY_BACKSPACE: self.remove_last_char,
            KEY_RETURN: self.load_coin
        }

        self.key_press = KEY_RETURN
        self.stdscr = stdscr
        self.window = curses.initscr()
        self.window.nodelay(True)
        self.init()
        self.mainloop()

    def init(self):
        self.tick = 0
        self.default_curr = "EUR"
        self.page = 0
        self.number_of_pages = 0
        self.search_pattern = ""
        self.height, self.width = self.stdscr.getmaxyx()
        self.coins = {}
        self.loaded_coins = {}
        self.symbols = []
        self.filtered_symbols = []
        self.fetch_coins()
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def draw(self):
        if self.key_press in self.keybindings:
            self.stdscr.clear()
            self.keybindings[self.key_press]()
        elif is_ascii(self.key_press):
            self.stdscr.clear()
            self.search_pattern += chr(self.key_press)
        else:
            if self.key_press != -1:
                self.log("Wrong key => {}".format(self.key_press))
        self.show_list()
        self.show_loaded_coins()
        self.render_ui()
        self.key_press = self.stdscr.getch()
        self.stdscr.refresh()
        self.tick += 1

    def draw_spinner(self):
        self.print(self.height-1, self.width-2, get_spin_sign(self.tick))

    def mainloop(self):
        while True:
            self.draw_spinner()
            if not self.tick % 600 and self.tick and len(self.loaded_coins) > 0:
                self.stdscr.clear()
                self.reload()
                self.log('Refresh loaded coins')
            self.draw()
            sleep(0.05)
        self.quit()

    def remove_last_char(self):
        if len(self.search_pattern) > 0:
            self.search_pattern = self.search_pattern[0:len(self.search_pattern)-1]

    def reload(self):
        for symbol, coin in self.loaded_coins.items():
            coin.fetch_value(self.default_curr)

    def load_coin(self):
        symbol = self.search_pattern
        if symbol in self.symbols:
            coin = self.coins[symbol]
            coin.fetch_value(self.default_curr)
            self.loaded_coins[symbol] = coin
            self.search_pattern = ""
        else:
            self.log("Invalid pattern.")

    def quit(self, exit_code=0):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        exit(exit_code)

    def prev_page(self):
        if self.page > 0:
            self.page -= 1

    def next_page(self):
        if self.page < self.number_of_pages-1:
            self.page += 1

    def fetch_coins(self):
        coin_list = Coin.fetch_all()

        self.coins = {}
        self.symbols = []
        for symbol, coin in coin_list.items():
            self.coins[symbol] = Coin(symbol, curr=self.default_curr, data=coin_list[symbol])
            self.symbols.append(symbol)

    def switch_curr(self):
        self.log("Switch default currency.")
        self.default_curr = 'EUR' if self.default_curr == 'USD' else 'USD'
        self.menu[0]['action'] = self.default_curr

    def render_ui(self):
        self.print(1, self.center(self.width, len(self.title)), self.title)
        pad = int(self.width / len(self.menu))
        for i in range(len(self.menu)):
            item = self.menu[i]
            self.print(self.height-2, pad * i, item["key"])
            self.print(self.height-2, pad * i + 5, item["action"], curses.A_REVERSE)
        self.print(self.height-1, int(self.width / 2),
                "Search pattern: {}".format(self.search_pattern))

    def show_loaded_coins(self):
        min_y = self.height - 10
        number_of_columns = int((self.width-10) / 25)

        if number_of_columns < len(self.loaded_coins):
            self.loaded_coins = self.loaded_coins[1:]
        f = 0
        for symbol, coin in self.loaded_coins.items():
            self.render_coin(5 + 20  * f, min_y, coin)
            f += 1

    def render_coin(self, x, y, coin):
        self.print(y, x, "{}".format(coin.data['FullName']))
        if coin.last_value:
            if coin.last_value < coin.value:
                color = curses.color_pair(2)
            else:
                color = curses.color_pair(3)
        else:
            color = 0
        self.print(y+1, x, coin.format_value(), color)
        self.print(y+2, x, "Total {}".format(coin.data['TotalCoinSupply']))
        self.print(y+3, x, coin.format_timedelta())

    def filter_symbols(self):
        self.filtered_symbols = []
        if len(self.search_pattern) > 0:
            for symbol in self.symbols:
                if self.search_pattern in symbol:
                    self.filtered_symbols.append(symbol)
        else:
            self.filtered_symbols = self.symbols

    def show_list(self):
        if len(self.symbols) > 0:
            self.filter_symbols()
            coords, items_numbers = self.get_grid(1, 3,
                    self.width, self.height-10, len(max(self.symbols)))

            index = self.page * items_numbers
            self.number_of_pages = int(len(self.filtered_symbols) / items_numbers) + 1
            for coord in coords:
                if index < len(self.filtered_symbols):
                    self.print(coord[0], coord[1], self.filtered_symbols[index])
                index += 1
            if self.page > self.number_of_pages-1:
                self.page = 0
            self.print(self.height-13, 5, "Page ({}/{})".format(self.page + 1, self.number_of_pages))

    def log(self, message, style=0):
        self.print(self.height-1, 0, "> ".format(message), style)

    def print(self, x, y, message, style=0):
        self.stdscr.addstr(x, y, message, style)

    def center(self, max_pos, length):
        return int(round(max_pos/2, 0) - round(length/2, 0))

    def get_grid(self, x, y, width, height, max_length):
        pad = int((width - x) / max_length) + 5
        rows = height - y
        cols = int((width - x) / pad)
        coords = []
        index = 0
        for col in range(x, width, pad):
            for row in range(y, rows):
                coords.append((row, col))
                index += 1
        return coords, index

if __name__ == '__main__':
    curses.wrapper(Window)

