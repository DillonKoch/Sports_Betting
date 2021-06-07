# ==============================================================================
# File: make_bet.py
# Project: Personal_Bets
# File Created: Wednesday, 24th June 2020 10:58:18 am
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 24th June 2020 11:21:06 am
# Modified By: Dillon Koch
# -----
#
# -----
# File to run using tkinter to make a bet and store in personal bets file
# ==============================================================================

import sys
import tkinter as tk
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Make_Bet:
    def __init__(self):
        self.root = tk.Tk()
        self.font = "bitstream charter"
        self.font_size = 10

        self.bettor = tk.StringVar()
        self.bettor.set('null')
        self.league = tk.StringVar()
        self.league.set('null')

        self.bettor_options = ["Dillon", "Todd", "Clay", "Sal"]
        self.league_options = ["NFL", "NBA", "NCAAF", "NCAAB"]

    def _add_one_button(self, text, variable, row, column, value=None):  # Specific Helper add_column
        value = text if value is None else value
        button = tk.Radiobutton(self.root, text=text, padx=10, pady=12, font=(
            self.font, self.font_size, 'bold'), variable=variable, value=value, indicatoron=0, width=7)
        button.grid(row=row, column=column)

    def add_column(self, options, variable, column, value=None):  # Top Level
        for i, option in enumerate(options):
            self._add_one_button(option, variable, i, column, value)

    def run_bettor_league(self):  # Run
        self.add_column(self.bettor_options, self.bettor, 0)
        self.add_column(self.league_options, self.league, 1)
        self.root.mainloop()
        bettor = self.bettor.get()
        league = self.league.get()
        print(bettor, league)
        return bettor, league

    def get_newest_bets(self, league):  # Top Level
        pass

    def run_all(self):
        self.run_bettor_league()


if __name__ == "__main__":
    x = Make_Bet()
    x.run_all()
