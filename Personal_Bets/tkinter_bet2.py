# ==============================================================================
# File: tkinter_bet2.py
# Project: Personal_Bets
# File Created: Wednesday, 29th July 2020 8:11:56 am
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 30th July 2020 5:24:51 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for creating a bet in a tkinter GUI and recording it in a df
# ==============================================================================

import sys
import tkinter as tk
from tkinter import Checkbutton
from tkinter.font import Font
from os.path import abspath, dirname

import pandas as pd
import numpy as np

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Tkinter_Bet:
    def __init__(self, bettor):
        self.bettor = bettor.replace(" ", "_")

    def _create_buttons(self, button_names, variable, column, padx=10, pady=12, width=8):  # Global Helper
        for i, button_name in enumerate(button_names):
            button = tk.Radiobutton(self.root, text=button_name, padx=padx, pady=pady,
                                    font=self.font, variable=variable, value=button_name, indicatoron=0,
                                    width=width)
            button.grid(row=i, column=column)

    def _refresh_root(self):  # Global Helper
        """
        refreshes the self.root variable - used each time a new window is created/shown
        """
        self.root = tk.Tk()
        self.font_size = 14
        self.font = Font(family='Helvetica', size=12, weight='bold')

    def _create_done_button(self, column, row=0):  # Global Helper
        """
        adds a small "Done" button in the input column that will close the window
        """
        done = tk.Button(text='Done', command=self.root.destroy, fg='red', font=self.font)
        done.grid(row=row, column=column)

    def _window_1_vars(self):  # Specific Helper window_1
        """
        creating variables for the first window: league, bet_type
        """
        self._refresh_root()
        self.league = tk.StringVar()
        self.league.set("null")
        self.leagues = ["NFL", "NBA", "NCAAF", "NCAAB"]

    def window_1(self):  # Top Level
        """
        running the first window to get the league and bet_type for the new bet
        """
        self._window_1_vars()
        self._create_buttons(self.leagues, self.league, 0)
        self._create_done_button(column=2)
        self.root.mainloop()
        league = self.league.get()
        print("League: ", league)
        return league

    def _pull_upcoming_bets(self, league):  # Specific Helper window_2
        """
        pulls upcoming games that have odds in PROD, so the bettor
        can decide which game to bet on in the second window
        """
        prod_path = ROOT_PATH + "/PROD/{}_PROD.csv".format(league)
        df = pd.read_csv(prod_path)
        df = df.loc[df.Final_Status.isnull()]
        df = df.loc[df.Over_ml_ESB.notnull()]
        return df

    def _window_2_vars(self):  # Specific Helper window_2
        """
        creating variables for window 2 - espn_id
        """
        self._refresh_root()
        self.espn_id = tk.StringVar()
        self.espn_id.set("null")

    def _create_game_buttons(self, game_strs, game_dict):  # Specific Helper window_2
        """
        creating game buttons for window 2 - these differ from the global helper
        _create_buttons in that this one has a changing value with game_dict
        """
        for i, game_str in enumerate(game_strs):
            button = tk.Radiobutton(self.root, text=game_str, padx=10, pady=12,
                                    font=self.font, variable=self.espn_id,
                                    value=game_dict[game_str], indicatoron=0, width=80)
            button.grid(row=i, column=0)

    def window_2(self, league):  # Top Level
        """
        running window 2 to get the ESPN_ID of the game to be bet on
        """
        self._window_2_vars()
        df = self._pull_upcoming_bets(league)
        espn_ids = [int(item) for item in list(df['ESPN_ID'])]
        homes = list(df['Home'])
        aways = list(df['Away'])
        dates = list(df['Date'])
        times = list(df['Game_Time'])
        game_strs = [f"{away} at {home} - {date} ({time})" for
                     away, home, date, time in zip(aways, homes, dates, times)]
        game_dict = {game_str: espn_id for game_str, espn_id in zip(game_strs, espn_ids)}
        self._create_game_buttons(game_strs, game_dict)
        self._create_done_button(1)
        self.root.mainloop()
        espn_id = self.espn_id.get()
        print("ESPN_ID: ", espn_id)
        return espn_id, df

    def _create_window_3_vars(self):  # Specific Helper window_3
        self._refresh_root()
        self.bet = tk.StringVar()
        self.bet.set("null")
        self.parlay = tk.BooleanVar()
        self.parlay.set(0)

    def _game_info(self, game):  # Specific Helper window_3
        game = game.iloc[0, :]
        game_str = f"{game['League']} - {game['Date']} ({game['Game_Time']})"
        home = game['Home']
        away = game['Away']

        home_ml = game['Home_ML_ESB']
        away_ml = game['Away_ML_ESB']
        home_ml = "+" + home_ml if "-" not in home_ml else home_ml
        away_ml = "+" + away_ml if "-" not in away_ml else away_ml

        home_spread = f"{game['Home_Line_ESB']} ({int(game['Home_Line_ml_ESB'])})"
        away_spread = f"{game['Away_Line_ESB']} ({int(game['Away_Line_ml_ESB'])})"
        home_spread = "+" + home_spread if "-" not in home_spread.split("(")[0] else home_spread
        away_spread = "+" + away_spread if "-" not in away_spread.split("(")[0] else away_spread

        over = f"O {game['Over_ESB']} ({int(game['Over_ml_ESB'])})"
        under = f"U {game['Under_ESB']} ({int(game['Under_ml_ESB'])})"
        return game_str, home, away, home_ml, away_ml, home_spread, away_spread, over, under

    def _add_labels(self, game_str, home, away):  # Specific Helper window_3
        self.root.title(game_str)
        home_label = tk.Label(self.root, text=home, font=self.font)
        home_label.grid(row=1, column=0)

        away_label = tk.Label(self.root, text=away, font=self.font)
        away_label.grid(row=2, column=0)

        ml_label = tk.Label(self.root, text="ML", font=self.font)
        ml_label.grid(row=0, column=1)

        spread_label = tk.Label(self.root, text="Spread", font=self.font)
        spread_label.grid(row=0, column=2)

        over_under_label = tk.Label(self.root, text="Over/Under", font=self.font)
        over_under_label.grid(row=0, column=3)

    def _add_one_bet_button(self, text, variable, value, row, column):  # Global Helper
        button = tk.Radiobutton(self.root, text=text, padx=10, pady=12,
                                font=self.font, variable=variable, value=value, indicatoron=0,
                                width=20)
        button.grid(row=row, column=column)

    def _add_all_bet_buttons(self, home_ml, away_ml, home_spread, away_spread, over, under):  # Specific Helper window_3
        self._add_one_bet_button(home_ml, self.bet, "Home_ML_ESB", 1, 1)
        self._add_one_bet_button(away_ml, self.bet, "Away_ML_ESB", 2, 1)
        self._add_one_bet_button(home_spread, self.bet, "Home_Line_ESB", 1, 2)
        self._add_one_bet_button(away_spread, self.bet, "Away_Line_ESB", 2, 2)
        self._add_one_bet_button(over, self.bet, "Over_ESB", 1, 3)
        self._add_one_bet_button(under, self.bet, "Under_ESB", 2, 3)

    def _create_parlay_box(self):  # Specific Helper window_3
        pbox = Checkbutton(self.root, text="Parlay", variable=self.parlay)
        pbox.grid(row=2, column=4)

    def window_3(self, espn_id, df):  # Top Level
        self._create_window_3_vars()
        game = df.loc[df.ESPN_ID == int(espn_id)].tail(1)
        game_str, home, away, home_ml, away_ml, home_spread, away_spread, over, under = self._game_info(game)
        self._add_labels(game_str, home, away)
        self._add_all_bet_buttons(home_ml, away_ml, home_spread, away_spread, over, under)
        self._create_done_button(row=1, column=4)
        self._create_parlay_box()
        self.root.mainloop()
        bet = self.bet.get()
        parlay = self.parlay.get()
        return bet, parlay, game

    def _create_window_4_vars(self):  # Specific Helper window_4
        self._refresh_root()
        self.bet_amount = tk.DoubleVar()
        self.bet_amount.set(0.0)
        self.to_win = tk.DoubleVar()
        self.to_win.set(0.0)
        self.to_win_manual = tk.DoubleVar()
        self.to_win_manual.set(0.0)  # manual overrides calculated value if one is given

    def _get_ml(self, bet_list):  # Specific Helper window_4
        _, _, bet, game = bet_list
        if "ML" in bet:
            return int(game[bet])
        elif "Line" in bet:
            line_str = bet.replace("Line", "Line_ml")
            return int(game[line_str])
        elif (("Over" in bet) or ("Under" in bet)):
            ou_str = bet.replace("Over", "Over_ml").replace("Under", "Under_ml")
            return int(game[ou_str])

    def _american_to_decimal(self, moneyline):  # Helping Helper _calculate_multiplier
        """
        converts American moneyline to decimal notation
        - decimal notation is used for calculating parlay multiplier
        """
        if moneyline > 0:
            return (moneyline / 100) + 1
        else:
            return (100 / moneyline) + 1

    def _calculate_multiplier(self, moneylines):  # Specific Helper window_4
        """
        calculates the parlay multiplier given a list of American moneylines
        """
        for ml in moneylines:
            assert ((ml <= -100) or (ml >= 100))

        decimal_odds = [self._american_to_decimal(ml) for ml in moneylines]
        multiplier = np.prod(decimal_odds)
        return multiplier

    def _create_bet_entry(self):  # Specific Helper window_4
        bet_label = tk.Label(self.root, text="Bet: ", font=self.font)
        bet_label.grid(row=0, column=0)
        # bet_entry_box = tk.Entry(self.root)
        # bet_entry_box.grid(row=0, column=1)

    def window_4(self, all_bets):  # Top Level
        self._create_window_4_vars()
        moneylines = [self._get_ml(bet_list) for bet_list in all_bets]
        multiplier = self._calculate_multiplier(moneylines)
        self._create_bet_entry()
        bet_amount = tk.Entry(self.root)
        bet_amount.grid(row=0, column=1)
        self.root.mainloop()
        print(bet_amount)
        return bet_amount, None

    def run(self):  # Run
        all_bets = []
        parlay = True
        while parlay:
            league = self.window_1()
            espn_id, df = self.window_2(league)
            bet, parlay, game = self.window_3(espn_id, df)
            new_bet = [league, espn_id, bet, game]
            all_bets.append(new_bet)
        bet_amount, to_win = self.window_4(all_bets)
        return all_bets


if __name__ == "__main__":
    x = Tkinter_Bet("Dillon Koch")
    self = x
    all_bets = x.run()
