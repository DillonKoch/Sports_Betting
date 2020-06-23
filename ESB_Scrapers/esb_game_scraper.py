# ==============================================================================
# File: esb_scraper.py
# Project: ESB
# File Created: Tuesday, 16th June 2020 7:58:09 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 23rd June 2020 1:55:46 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for Elite Sportsbook games
# ==============================================================================

import datetime
import json
import re
import sys
from os.path import abspath, dirname

import os
import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import get_sp1
from ESB_Scrapers.esb_prop_scrapers import ESB_Bool_Prop_Scraper


class ESB_Game:
    def __init__(self):
        self.date = None
        self.home_team = None
        self.away_team = None
        self.game_time = None
        self.over = None
        self.under = None
        self.home_spread = None
        self.away_spread = None
        self.home_ml = None
        self.away_ml = None


class ESB_Perform_Scrapes:
    @property
    def config(self):  # Property
        with open("{}_esb.json".format(self.league.lower())) as f:
            config = json.load(f)
        return config

    def run_all_updates(self):  # Run
        bet_lists = self.config["Bets"]
        for bet_list in bet_lists:
            bet_name, link, category = bet_list
            sp = get_sp1(link)

            if self._bet_df_exists(bet_name):
                self.update_bet_df(bet_name, category, sp)
            else:
                self.make_new_df(bet_name, category, sp)
        print("DONE")

    def update_bet_df(self, bet_name, category, sp):  # Run
        full_path = ROOT_PATH + "/ESB_Data/{}/{}.csv".format(self.league, bet_name)
        existing_df = pd.read_csv(full_path)

        if category == "Games":
            new_df = self._update_games_df(sp)
        elif category == "Prop":
            new_df = self._update_prop_df(sp)
        elif category == "Bool_Prop":
            new_df = self._update_bool_prop_df(sp)

        new_df = self._update_games_df(existing_df, sp) if category == "Games" else self._update_prop_df(existing_df, sp)
        new_df.to_csv(full_path)

    def _bet_df_exists(self, bet_list):  # Specific Helper run_all_updates
        bet_list_title, link, category = bet_list
        df_name = bet_list_title + ".csv"
        return True if df_name in os.listdir(ROOT_PATH + "/ESB_Data/{}/".format(self.league)) else False


class ESB_Game_Scraper(ESB_Bool_Prop_Scraper):

    def create_games_df(self):  # Specific Helper scrape_game_lines
        cols = ["Title", "datetime", "Game_Time", "Home", "Away", "Over_ESB", "Over_ml_ESB",
                "Under_ESB", "Under_ml_ESB", "Home_Line_ESB", "Home_Line_ml_ESB",
                "Away_Line_ESB", "Away_Line_ml_ESB", "Home_ML_ESB", "Away_ML_ESB", "scraped_ts"]
        df = pd.DataFrame(columns=cols)
        return df

    def _get_box_date_pairs(self, dates_and_boxes):  # Helping Helper get_date_event_boxes
        if dates_and_boxes[0][1] != "date":
            raise ValueError("First date-event item is not a date")

        box_results = []
        for pair in dates_and_boxes:
            sp, label = pair
            if label == "date":
                current_date = sp.get_text()
            elif label == "box":
                box_results.append([sp, current_date])
        return box_results

    def get_date_event_boxes(self, sp):  # Specific Helper esb_game_from_box_date_pair
        main_sp = sp.find_all('div', attrs={'class': 'row event'})[0]
        divs = main_sp.find_all('div')
        dates_and_boxes = []
        for div in divs:
            div_str = str(div)
            if "col-sm-12 eventbox" in div_str:
                dates_and_boxes.append([div, "box"])
            elif "col-xs-12 date" in div_str:
                dates_and_boxes.append([div, "date"])

        box_date_pairs = self._get_box_date_pairs(dates_and_boxes)
        return box_date_pairs

    def _box_time(self, box):  # Specific Helper esb_game_from_box_date_pair
        time = box.find_all('div', attrs={'class': 'col-xs-12 visible-xs visible-sm'})
        time_str = time[0].get_text()
        time_str = time_str.strip()
        return time_str

    def _box_teams(self, box):  # Specific Helper esb_game_from_box_date_pair
        teams = box.find_all('span', attrs={'class': 'team-title'})
        teams = [item.get_text() for item in teams]
        return teams

    def _box_over_under(self, box):  # Specific Helper esb_game_from_box_date_pair
        bet_strings = [item.get_text() for item in box.find_all('div', attrs={'class': 'market'})]
        over_comp = re.compile(r"(O) ((\d|\.)+)\(((\d|-)+)\)")
        under_comp = re.compile(r"(U) ((\d|\.)+)\(((\d|-)+)\)")

        for bet_string in bet_strings:
            over_match = re.match(over_comp, bet_string)
            if over_match:
                over = [over_match.group(1), over_match.group(2), over_match.group(4)]

            under_match = re.match(under_comp, bet_string)
            if under_match:
                under = [under_match.group(1), under_match.group(2), under_match.group(4)]

        return over, under

    def _box_spreads(self, box):  # Specific Helper esb_game_from_box_date_pair
        bet_strings = [item.get_text() for item in box.find_all('div', attrs={'class': 'market'})]
        fav_comp = re.compile(r"(-)((\d|\.)+)\(((\d|-)+)\)")
        dog_comp = re.compile(r"(\+)((\d|\.)+)\(((\d|-)+)\)")

        for bet_string in bet_strings:
            fav_match = re.match(fav_comp, bet_string)
            if fav_match:
                fav = [fav_match.group(1), fav_match.group(2), fav_match.group(4)]

            dog_match = re.match(dog_comp, bet_string)
            if dog_match:
                dog = [dog_match.group(1), dog_match.group(2), dog_match.group(4)]

        return fav, dog

    def _home_fav_check(self, bet_strings):  # Helping Helper _bets_from_box
        half_num = int(len(bet_strings) / 2)
        home_strings = bet_strings[: half_num]
        has_plus = False
        for home_str in home_strings:
            if "+" in home_str:
                has_plus = True
        return not has_plus

    def _get_bet_match(self, bet_strings, reg_comp, ml=False):  # Helping Helper _bets_from_box
        result = None
        for bet_string in bet_strings:
            match = re.match(reg_comp, bet_string)
            if match:
                result = match.group(0) if ml else [match.group(1), match.group(2), match.group(4)]
        return result

    def _bets_from_box(self, box):  # Helping Helper esb_game_from_box_date_pair
        bet_strings = [item.get_text() for item in box.find_all('div', attrs={'class': 'market'})]
        home_is_fav = self._home_fav_check(bet_strings)

        over_comp = re.compile(r"(O) ((\d|\.)+)\(((\d|-)+)\)")
        under_comp = re.compile(r"(U) ((\d|\.)+)\(((\d|-)+)\)")
        spread_fav_comp = re.compile(r"(-)((\d|\.)+)\(((\d|-)+)\)")
        spread_dog_comp = re.compile(r"(\+)((\d|\.)+)\(((\d|-)+)\)")
        ml_fav_comp = re.compile(r"-(\d+)$")
        ml_dog_comp = re.compile(r"\+(\d+)$")

        over = self._get_bet_match(bet_strings, over_comp)
        under = self._get_bet_match(bet_strings, under_comp)
        spread_fav = self._get_bet_match(bet_strings, spread_fav_comp)
        spread_dog = self._get_bet_match(bet_strings, spread_dog_comp)
        ml_fav = self._get_bet_match(bet_strings, ml_fav_comp, ml=True)
        ml_dog = self._get_bet_match(bet_strings, ml_dog_comp, ml=True)

        home_spread = spread_fav if home_is_fav else spread_dog
        away_spread = spread_dog if home_is_fav else spread_fav
        home_ml = ml_fav if home_is_fav else ml_dog
        away_ml = ml_dog if home_is_fav else ml_fav
        return over, under, home_spread, away_spread, home_ml, away_ml

    def esb_game_from_box_date_pair(self, box_date_pair):  # Specific Helper scrape_game_lines
        box, date = box_date_pair
        esb_game = ESB_Game()
        esb_game.date = date
        esb_game.game_time = self._box_time(box)
        esb_game.away_team, esb_game.home_team = self._box_teams(box)
        esb_game.over, esb_game.under = self._box_over_under(box)
        over, under, home_spread, away_spread, home_ml, away_ml = self._bets_from_box(box)
        esb_game.over = over
        esb_game.under = under
        esb_game.home_spread = home_spread
        esb_game.away_spread = away_spread
        esb_game.home_ml = home_ml
        esb_game.away_ml = away_ml
        return esb_game

    def esb_game_to_df(self, df, esb_game, title):  # Specific Helper scrape_game_lines
        dt = datetime.datetime.strptime(esb_game.date, "%B %d, %Y")
        today = self._get_scrape_ts()
        new_row = [
            title,
            dt,
            esb_game.game_time,
            esb_game.home_team,
            esb_game.away_team,
            esb_game.over[1],
            esb_game.over[2],
            esb_game.under[1],
            esb_game.under[2],
            ''.join([esb_game.home_spread[0], esb_game.home_spread[1]]),
            esb_game.home_spread[2],
            ''.join([esb_game.away_spread[0], esb_game.away_spread[1]]),
            esb_game.away_spread[2],
            esb_game.home_ml,
            esb_game.away_ml,
            today
        ]
        new_row = [item if item is not None else "NL" for item in new_row]
        df.loc[len(df)] = new_row
        return df

    def scrape_game_lines(self, sp):  # Top Level make_new_df
        df = self.create_games_df()
        title = self.get_sp_title(sp)
        box_date_pairs = self.get_date_event_boxes(sp)
        esb_games = [self.esb_game_from_box_date_pair(bdp) for bdp in box_date_pairs]
        for game in esb_games:
            df = self.esb_game_to_df(df, game, title)
        return df

    def get_teams(self, sp):  # Specific Helper scrape_prop
        teams = sp.find_all('span', attrs={'class': 'team'})
        teams = [item.get_text() for item in teams]
        return teams

    def make_new_df(self, bet_name, category, sp):  # Run
        if category == "Games":
            df = self.scrape_game_lines(sp)
        elif category == "Prop":
            df = self.scrape_prop(sp)
        elif category == "Bool_Prop":
            df = self.scrape_bool_prop(sp)

        df.to_csv(ROOT_PATH + "/ESB_Data/{}/{}.csv".format(self.league, bet_name), index=False)
        return df

    def _update_games_df(self):  # Top Level update_bet_df
        pass


if __name__ == "__main__":
    x = ESB_Game_Scraper("NFL", "nfc_south", sp)
    self = x
    sp = get_sp1("https://www.elitesportsbook.com/sports/pro-football-futures-betting/2020-2021-nfc-south.sbk")
