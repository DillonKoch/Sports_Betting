# ==============================================================================
# File: esb_game_scraper2.py
# Project: ESB
# File Created: Saturday, 22nd August 2020 1:41:06 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 23rd August 2020 11:30:40 am
# Modified By: Dillon Koch
# -----
#
# -----
# Elite Sportsbook Game Lines scraper
# ==============================================================================


from Utility.selenium_scraper import Selenium_Scraper
import datetime
import re
import sys
from os.path import abspath, dirname

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESB.esb_base_scraper import ESB_Base_Scraper


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
        self.home_spread_ml = None
        self.away_spread = None
        self.away_spread_ml = None
        self.home_ml = None
        self.away_ml = None


class ESB_Game_Scraper(ESB_Base_Scraper):
    """
    scraper for games on ESB, inheriting from ESB Base Scraper
    """

    def __init__(self, league, bet_name, sp):
        super().__init__(league, bet_name, sp)

    @property
    def df_cols(self):  # Tested
        cols = ["Title", "datetime", "Game_Time", "Home", "Away", "Over_ESB", "Over_ml_ESB",
                "Under_ESB", "Under_ml_ESB", "Home_Line_ESB", "Home_Line_ml_ESB",
                "Away_Line_ESB", "Away_Line_ml_ESB", "Home_ML_ESB", "Away_ML_ESB", "scraped_ts"]
        return cols

    def _get_box_date_pairs(self, dates_and_boxes):  # Helping Helper get_date_event_boxes  Tested
        """
        Takes the [[html, 'date'], [html, 'box'], ...] list from get_date_event_boxes
        - makes sure the first one is a date
        - creates clean list of [[game_html, date], [game_html, date], ...]
        """
        # if the first box doesn't have a date, we don't know what day the game is on
        if dates_and_boxes[0][1] != "date":
            raise ValueError("First date-event item is not a date")

        # creating a list of [html, date] for each game
        # adding each game html to box_results, updating the current date as date html's are found
        box_results = []
        for pair in dates_and_boxes:
            sp, label = pair
            if label == "date":
                current_date = sp.get_text()
            elif label == "box":
                box_results.append([sp, current_date])
        return box_results

    def get_date_event_boxes(self):  # Specific Helper esb_game_from_box_date_pair  Tested
        """
        finds the html and date of each game on the ESB page
        - for example, the first NFL week would return 16 (html, date) pairs for 16 games
        - [[html, date], [html, date], ...]
        """
        main_sp = self.sp.find_all('div', attrs={'class': 'row event'})[0]
        divs = main_sp.find_all('div')

        # each game and date above the games are in the divs. for each div, the html is added
        # with a string indicating if it's for a game, or the date of upcoming games
        dates_and_boxes = []
        for div in divs:
            div_str = str(div)
            if "col-sm-12 eventbox" in div_str:
                dates_and_boxes.append([div, "box"])
            elif "col-xs-12 date" in div_str:
                dates_and_boxes.append([div, "date"])

        box_date_pairs = self._get_box_date_pairs(dates_and_boxes)
        return box_date_pairs

    def _game_box_time(self, game_box):  # Specific Helper esb_game_from_box_date_pair Tested
        """
        finds the game time from a box of game html
        """
        time = game_box.find_all('div', attrs={'class': 'col-xs-12 visible-xs visible-sm'})
        time_str = time[0].contents[1].contents[1].get_text()
        return time_str

    def _game_box_teams(self, game_box):  # Specific Helper esb_game_from_box_date_pair Tested
        """
        finds the two teams from a box of game html
        """
        teams = game_box.find_all('span', attrs={'class': 'team-title'})
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
                result = 100 if result == "even" else result
        return result

    def _check_spread_zero(self, bet_strings, spread_fav, spread_dog):  # Helping Helper _bets_from_box
        if None not in spread_fav:
            return spread_fav, spread_dog

        zero_spread_comp = re.compile(r"^(0)\(([-\d]+)\)")
        spread_strings = [bet_strings[1], bet_strings[4]]
        matches = [re.match(zero_spread_comp, ss) for ss in spread_strings]
        if None not in matches:
            spread_fav = ['', matches[0].group(1), matches[0].group(2)]
            spread_dog = ['', matches[1].group(1), matches[1].group(2)]
        return spread_fav, spread_dog

    def _bets_from_box(self, box):  # Helping Helper esb_game_from_box_date_pair
        """
        finds all the bets from a game html box
        """
        bet_strings = [item.get_text() for item in box.find_all('div', attrs={'class': 'market'})]
        home_is_fav = self._home_fav_check(bet_strings)

        over_comp = re.compile(r"(O) ((\d|\.)+)\((((\d|-)+)|even)\)")
        under_comp = re.compile(r"(U) ((\d|\.)+)\((((\d|-)+)|even)\)")
        spread_fav_comp = re.compile(r"(-)((\d|\.)+)\((((\d|-)+)|even)\)")
        spread_dog_comp = re.compile(r"(\+)((\d|\.)+)\((((\d|-)+)|even)\)")
        ml_fav_comp = re.compile(r"-(\d+)$")
        ml_dog_comp = re.compile(r"(\+(\d+)$)|even")

        over = self._get_bet_match(bet_strings, over_comp)
        under = self._get_bet_match(bet_strings, under_comp)
        spread_fav = self._get_bet_match(bet_strings, spread_fav_comp)
        spread_dog = self._get_bet_match(bet_strings, spread_dog_comp)
        ml_fav = self._get_bet_match(bet_strings, ml_fav_comp, ml=True)
        ml_dog = self._get_bet_match(bet_strings, ml_dog_comp, ml=True)
        spread_fav, spread_dog = self._check_spread_zero(bet_strings, spread_fav, spread_dog)

        for item in [over, under, spread_fav, spread_dog]:
            if item[2] == "even":
                item[2] = "-100"

        home_spread = spread_fav if home_is_fav else spread_dog
        away_spread = spread_dog if home_is_fav else spread_fav
        home_ml = ml_fav if home_is_fav else ml_dog
        away_ml = ml_dog if home_is_fav else ml_fav
        return over, under, home_spread, away_spread, home_ml, away_ml

    def esb_game_from_box_date_pair(self, box_date_pair):  # Specific Helper make_new_df
        """
        creates an ESB_Game instance from a box_date_pair
        """
        box, date = box_date_pair
        esb_game = ESB_Game()
        esb_game.date = date
        esb_game.game_time = self._game_box_time(box)
        esb_game.away_team, esb_game.home_team = self._game_box_teams(box)
        # esb_game.over, esb_game.under = self._box_over_under(box)
        over, under, home_spread, away_spread, home_ml, away_ml = self._bets_from_box(box)
        esb_game.over = over
        esb_game.under = under
        esb_game.home_spread = ''.join([home_spread[0], home_spread[1]]) if None not in home_spread else "NL"
        esb_game.home_spread_ml = home_spread[2] if home_spread[2] is not None else "NL"
        esb_game.away_spread = ''.join([away_spread[0], away_spread[1]]) if None not in away_spread else "NL"
        esb_game.away_spread_ml = away_spread[2] if away_spread[2] is not None else "NL"
        esb_game.home_ml = home_ml
        esb_game.away_ml = away_ml
        return esb_game

    def esb_game_to_df(self, df, esb_game, title):  # Specific Helper make_new_df
        """
        adds an esb_game and its title to a new row in the df created with self.create_df()
        """
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
            esb_game.home_spread,
            esb_game.home_spread_ml,
            esb_game.away_spread,
            esb_game.away_spread_ml,
            esb_game.home_ml,
            esb_game.away_ml,
            today
        ]
        new_row = [item if item is not None else "NL" for item in new_row]
        df.loc[len(df)] = new_row
        return df

    def make_new_df(self, save):  # Top Level
        """
        overwriting from bool prop scraper - creates new df with all current odds
        """
        df = self.create_df()
        title = self._get_sp_title()
        box_date_pairs = self.get_date_event_boxes()
        esb_games = [self.esb_game_from_box_date_pair(bdp) for bdp in box_date_pairs]
        for game in esb_games:
            df = self.esb_game_to_df(df, game, title)
        df['datetime'] = pd.to_datetime(df['datetime']).apply(lambda x: x.date())
        df = self._clean_df_names(df)

        if save:
            df.to_csv(self.df_path, index=False)
        return df

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

            drop_cols = ['Title', 'datetime', 'Home', 'Away']
            strings_cols = ["Title", "datetime", "Game_Time", "Home", "Away", "Over_ESB", "Over_ml_ESB",
                            "Under_ESB", "Under_ml_ESB", "Home_Line_ESB", "Home_Line_ml_ESB", "Away_Line_ESB",
                            "Away_Line_ml_ESB", "Home_ML_ESB", "Away_ML_ESB"]
            print_indices = [0, 1, 2, 3, 4]
            full_df = self.combine_dfs(current_df, new_df, drop_cols, strings_cols, print_indices)
            full_df.to_csv(self.df_path, index=False)


if __name__ == "__main__":
    e = Selenium_Scraper(["IOWA", "BET NOW", "PRO FOOTBALL LINES", "Week 1"])
    sp = e.run()
    x = ESB_Game_Scraper("NFL", "Game_Lines", sp)
    self = x
    df = x.update_df()
