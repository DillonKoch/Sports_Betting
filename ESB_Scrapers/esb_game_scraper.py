# ==============================================================================
# File: esb_scraper.py
# Project: ESB
# File Created: Tuesday, 16th June 2020 7:58:09 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 27th July 2020 5:59:57 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for Elite Sportsbook games
# ==============================================================================

import datetime
import re
import sys
from os.path import abspath, dirname

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import get_sp1
from ESB_Scrapers.esb_prop_scrapers import ESB_Bool_Prop_Scraper


class ESB_Game:
    """
    class for representing a single game on Elite Sportsbook
    """

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


class ESB_Game_Scraper(ESB_Bool_Prop_Scraper):
    """
    scraper for games on ESB, inheriting from ESB bool prop scraper
    """

    def create_games_df(self) -> pd.DataFrame:  # Specific Helper make_new_df
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

    def _home_fav_check(self, bet_strings):  # Helping Helper _bets_from_box
        half_num = int(len(bet_strings) / 2)
        home_strings = bet_strings[half_num:]
        has_plus = False
        for home_str in home_strings:
            if "+" in home_str:
                has_plus = True
        return not has_plus

    def _get_bet_match(self, bet_strings, reg_comp, ml=False):  # Helping Helper _bets_from_box
        result = None if ml else [None] * 3
        for bet_string in bet_strings:
            match = re.match(reg_comp, bet_string)
            if match:
                result = match.group(0) if ml else [match.group(1), match.group(2), match.group(4)]
        return result

    def _bets_from_box(self, box):  # Helping Helper esb_game_from_box_date_pair
        bet_strings = [item.get_text() for item in box.find_all('div', attrs={'class': 'market'})]
        home_is_fav = self._home_fav_check(bet_strings)

        over_comp = re.compile(r"(O) ((\d|\.)+)\((((\d|-)+)|even)\)")
        under_comp = re.compile(r"(U) ((\d|\.)+)\((((\d|-)+)|even)\)")
        spread_fav_comp = re.compile(r"(-)((\d|\.)+)\((((\d|-)+)|even)\)")
        spread_dog_comp = re.compile(r"(\+)((\d|\.)+)\((((\d|-)+)|even)\)")
        ml_fav_comp = re.compile(r"-(\d+)$")
        ml_dog_comp = re.compile(r"\+(\d+)$")

        over = self._get_bet_match(bet_strings, over_comp)
        under = self._get_bet_match(bet_strings, under_comp)
        spread_fav = self._get_bet_match(bet_strings, spread_fav_comp)
        spread_dog = self._get_bet_match(bet_strings, spread_dog_comp)
        ml_fav = self._get_bet_match(bet_strings, ml_fav_comp, ml=True)
        ml_dog = self._get_bet_match(bet_strings, ml_dog_comp, ml=True)

        for item in [over, under, spread_fav, spread_dog]:
            if item[2] == "even":
                item[2] = "-100"

        home_spread = spread_fav if home_is_fav else spread_dog
        away_spread = spread_dog if home_is_fav else spread_fav
        home_ml = ml_fav if home_is_fav else ml_dog
        away_ml = ml_dog if home_is_fav else ml_fav
        return over, under, home_spread, away_spread, home_ml, away_ml

    def esb_game_from_box_date_pair(self, box_date_pair):  # Specific Helper make_new_df
        box, date = box_date_pair
        esb_game = ESB_Game()
        esb_game.date = date
        esb_game.game_time = self._box_time(box)
        esb_game.away_team, esb_game.home_team = self._box_teams(box)
        # esb_game.over, esb_game.under = self._box_over_under(box)
        over, under, home_spread, away_spread, home_ml, away_ml = self._bets_from_box(box)
        esb_game.over = over
        esb_game.under = under
        esb_game.home_spread = home_spread
        esb_game.away_spread = away_spread
        esb_game.home_ml = home_ml
        esb_game.away_ml = away_ml
        return esb_game

    def esb_game_to_df(self, df, esb_game, title):  # Specific Helper make_new_df
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

    def _clean_df_names(self, df):  # Specific Helper make_new_df
        df = df.replace("LA Chargers", "Los Angeles Chargers")
        df = df.replace("Los Angeles Clippers", "LA Clippers")
        return df

    def make_new_df(self, save):  # Top Level
        """
        overwriting from bool prop scraper - creates new df with all current odds
        """
        df = self.create_games_df()
        title = self._get_sp_title()
        box_date_pairs = self.get_date_event_boxes(self.sp)
        esb_games = [self.esb_game_from_box_date_pair(bdp) for bdp in box_date_pairs]
        for game in esb_games:
            df = self.esb_game_to_df(df, game, title)
        df['datetime'] = pd.to_datetime(df['datetime']).apply(lambda x: x.date())
        df = self._clean_df_names(df)

        if save:
            df.to_csv(self.df_path, index=False)
        return df

    def combine_dfs(self, current_df, new_df):  # Top Level
        """
        overwriting method in bool prop scraper
        - combines current and newly scraped df, keeping only changed/new bets from new df
        """
        newest_current = current_df.drop_duplicates(['Title', 'datetime', 'Home', 'Away'], keep="last")

        items_cols = ["Title", "datetime", "Game_Time", "Home", "Away", "Over_ESB", "Over_ml_ESB",
                      "Under_ESB", "Under_ml_ESB", "Home_Line_ESB", "Home_Line_ml_ESB", "Away_Line_ESB",
                      "Away_Line_ml_ESB", "Home_ML_ESB", "Away_ML_ESB"]
        current_items = [[row[col] for col in items_cols] for i, row in newest_current.iterrows()]
        new_items = [[row[col] for col in items_cols] for i, row in new_df.iterrows()]
        current_items = self._make_strings(current_items)
        new_items = self._make_strings(new_items)

        add_indices = []
        for i, item in enumerate(new_items):
            if item not in current_items:
                add_indices.append(i)

        for i in add_indices:
            current_df.loc[len(current_df)] = new_df.iloc[i, :]
            print("-" * 25)
            print("Added new bet to {} {}".format(self.league, self.bet_name))
            print("-" * 25)
            print(new_items[i][1], new_items[i][2], new_items[i][3])
        return current_df

    def update_df(self):  # Run
        """
        updating the existing df or making a new one
        """
        if not self.check_df_exists():
            self.make_new_df(save=True)
            print("-" * 25)
            print("New file created for {}".format(self.bet_name))
            print("-" * 25)
        else:
            current_df = pd.read_csv(self.df_path)
            current_df['datetime'] = pd.to_datetime(current_df['datetime']).apply(lambda x: x.date())
            new_df = self.make_new_df(save=False)
            full_df = self.combine_dfs(current_df, new_df)
            full_df.to_csv(self.df_path, index=False)


if __name__ == "__main__":
    link = "https://www.elitesportsbook.com/sports/pro-football-lines-betting/week-1.sbk"
    sp = get_sp1(link)
    x = ESB_Game_Scraper("NFL", "Game_Lines", sp)
    self = x
    df = self.make_new_df(False)
