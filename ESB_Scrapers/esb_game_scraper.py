# ==============================================================================
# File: esb_scraper.py
# Project: ESB
# File Created: Tuesday, 16th June 2020 7:58:09 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 22nd June 2020 8:28:49 pm
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


class ESB_Bool_Prop_Scraper:
    def __init__(self, league, bet_name, sp):
        self.league = league
        self.bet_name = bet_name
        self.sp = sp
        self.df_path = ROOT_PATH + "/ESB_Data/{}/{}.csv".format(self.league, self.bet_name)

    def _get_scrape_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%m")

    def create_prop_df(self):  # Top Level
        cols = ["Title", "description", "Team", "Option", "Odds", "scraped_ts"]
        df = pd.DataFrame(columns=cols)
        return df

    def get_sp_title(self):  # Top Level
        title = self.sp.find_all('div', attrs={'id': 'eventTitleBar'})[0].get_text().strip()
        return title

    def get_sp_description(self):  # Specific Helper scrape_prop
        try:
            description = self.sp.find_all('div', attrs={'id': 'futureDescription'})[0].get_text()
        except IndexError:
            print("No description found")
            description = None
        return description

    def get_bets(self):  # Top Level
        headers = sp.find_all('div', attrs={'class': 'row event eventheading'})
        headers = [item.get_text().strip() for item in headers]

        teams = self.sp.find_all('span', attrs={'class': 'team'})
        teams += self.sp.find_all('span', attrs={'class': 'team-title'})
        teams = (item.get_text() for item in teams)

        odds = self.sp.find_all('div', attrs={'class': 'market'})
        odds = [item.get_text() for item in odds]
        odds = (item for item in odds if item != "-")

        results = []
        for header in headers:
            results.append([header, next(teams), next(odds)])
            results.append([header, next(teams), next(odds)])

        return results

    def make_new_df(self, save):  # Run
        df = self.create_prop_df()
        title = self.get_sp_title()
        description = self.get_sp_description()
        bets = self.get_bets()
        scraped_ts = self._get_scrape_ts()
        for bet in bets:
            df.loc[len(df)] = [title, description, bet[0], bet[1], bet[2], scraped_ts]
        if save:
            df.to_csv(self.df_path, index=False)
        return df

    def _check_df_exists(self):  # Specific Helper update_df
        try:
            _ = pd.read_csv(self.df_path)
            return True
        except FileNotFoundError:
            return False

    # def _combine_dfs(self, existing_df, new_df):  # Specific Helper update_df
    #     existing_items = [[row['Title'], row['Team'], row['Option'], row['Odds']] for i, row in existing_df.iterrows()]
    #     new_items = [[row['Title'], row['Team'], row['Option'], row['Odds']] for i, row in new_df.iterrows()]

    #     update_indices = [i for i, item in enumerate(new_items) if item not in existing_items]

    #     for index in update_indices:
    #         existing_df.loc[len(existing_df)] = new_df.iloc[index, :]
    #     return existing_df

    def _combine_dfs(self, existing_df, new_df):
        new_items = [[row['Title'], row['Team'], row['Option'], row['Odds']] for i, row in new_df.iterrows()]

        new_bet_indices = []
        for i, new_item in enumerate(new_items):
            match = None
            for j, row in existing_df.iterrows():
                existing_items = [row['Title'], row['Team'], row['Option'], row['Odds']]
                if existing_items == new_item:
                    match = row
            if match is not None:
                new_bet_indices.append(i)

        for i in new_bet_indices:
            existing_df.loc[len(existing_df)] = new_df.iloc[i, :]
        return existing_df
        # FIXME pick up here^^ - check for the newest row in existing df to have a title,
        #  description, team, option match,
        #  then if the odds are different in new vs existing, add the new one
        # that way you could have the same odds show up twice, but with a change
        # in the middle (-120 to -110 back to -120 and get 3 rows)

    def update_df(self):  # Run
        if not self._check_df_exists():
            self.make_new_df(save=True)
        else:
            existing_df = pd.read_csv(self.df_path)
            new_df = self.make_new_df(save=False)
            full_df = self._combine_dfs(existing_df, new_df)
            full_df.to_csv(self.df_path, index=False)


class ESB_Prop_Scraper(ESB_Bool_Prop_Scraper):

    def create_prop_df(self):
        cols = ["Title", "description", "Team/Player", "ML", "scraped_ts"]
        df = pd.DataFrame(columns=cols)
        return df

    def get_bets(self):  # Top Level
        teams = self.sp.find_all('span', attrs={'class': 'team'})
        teams += self.sp.find_all('span', attrs={'class': 'team-title'})
        teams = [item.get_text() for item in teams]

        odds = self.sp.find_all('div', attrs={'class': 'market'})
        odds = [item.get_text() for item in odds]
        odds = [item for item in odds if item != "-"]

        return [(team, odd) for team, odd in zip(teams, odds)]

    def make_new_df(self, save):  # Run
        df = self.create_prop_df()
        title = self.get_sp_title()
        description = self.get_sp_description()
        bets = self.get_bets()
        scraped_ts = self._get_scrape_ts()
        for bet in bets:
            df.loc[len(df)] = [title, description, bet[0], bet[1], scraped_ts]
        if save:
            df.to_csv(self.df_path, index=False)
        return df

    def _combine_dfs(self, existing_df, new_df):  # Specific Helper update_df
        existing_items = [[row['Title'], row['Team/Player'], row['ML']] for i, row in existing_df.iterrows()]
        new_items = [[row['Title'], row['Team/Player'], row['ML'].replace('+', '')] for i, row in new_df.iterrows()]

        update_indices = [i for i, item in enumerate(new_items) if item not in existing_items]
        for i in update_indices:
            print(new_items[i])

        for index in update_indices:
            existing_df.loc[len(existing_df)] = new_df.iloc[index, :]
        return existing_df


class ESB_Scraper:
    def __init__(self, league):
        self.league = league

    @property
    def config(self):  # Property
        with open("{}_esb.json".format(self.league.lower())) as f:
            config = json.load(f)
        return config

    def _get_scrape_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%m")

    def create_games_df(self):  # Specific Helper scrape_game_lines
        cols = ["Title", "datetime", "Game_Time", "Home", "Away", "Over_ESB", "Over_ml_ESB",
                "Under_ESB", "Under_ml_ESB", "Home_Line_ESB", "Home_Line_ml_ESB",
                "Away_Line_ESB", "Away_Line_ml_ESB", "Home_ML_ESB", "Away_ML_ESB", "scraped_ts"]
        df = pd.DataFrame(columns=cols)
        return df

    def create_prop_df(self):  # Specific Helper scrape_prop
        cols = ["Title", "description", "Team/Player", "ML", "scraped_ts"]  # FIXME
        df = pd.DataFrame(columns=cols)
        return df

    def create_bool_prop_df(self):  # Specific Helper scrape_bool_prop
        cols = ["Title", "description", "Team", "Option", "ML", "scraped_ts"]
        df = pd.DataFrame(columns=cols)
        return df

    def get_sp_title(self, sp):  # Top Level
        title = sp.find_all('div', attrs={'id': 'eventTitleBar'})[0].get_text().strip()
        return title

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

    def _get_sp_description(self, sp):  # Specific Helper scrape_prop
        try:
            description = sp.find_all('div', attrs={'id': 'futureDescription'})[0].get_text()
        except IndexError:
            print("No description found")
            description = None
        return description

    def get_teams(self, sp):  # Specific Helper scrape_prop
        teams = sp.find_all('span', attrs={'class': 'team'})
        teams = [item.get_text() for item in teams]
        return teams

    def _get_prop_bets(self, sp):  # Specific Helper scrape_prop
        teams = sp.find_all('span', attrs={'class': 'team'})
        teams += sp.find_all('span', attrs={'class': 'team-title'})
        teams = [item.get_text() for item in teams]

        odds = sp.find_all('div', attrs={'class': 'market'})
        odds = [item.get_text() for item in odds]
        odds = [item for item in odds if item != "-"]
        print(len(teams), len(odds))

        return [(team, ml) for team, ml in zip(teams, odds)]

    def scrape_prop(self, sp):  # Top Level
        df = self.create_prop_df()
        title = self.get_sp_title(sp)
        description = self._get_sp_description(sp)
        bets = self._get_prop_bets(sp)

        scrape_ts = self._get_scrape_ts()
        for bet in bets:
            df.loc[len(df)] = [title, description, bet[0], bet[1], scrape_ts]
        return df

    def _get_prop_bool_bets(self, sp):  # Specific Helper scrape_bool_prop
        headers = sp.find_all('div', attrs={'class': 'row event eventheading'})
        headers = [item.get_text().strip() for item in headers]
        prop_pairs = self._get_prop_bets(sp)
        return [(header, pair[0], pair[1]) for header, pair in zip(headers, prop_pairs)]

    def scrape_bool_prop(self, sp):  # Top Level
        df = self.create_bool_prop_df()
        title = self.get_sp_title(sp)
        description = self._get_sp_description(sp)
        bets = self._get_prop_bool_bets(sp)

        scrape_ts = self._get_scrape_ts()
        for bet in bets:
            df.loc[len(df)] = [title, description, bet[0], bet[1], bet[2], scrape_ts]
        return df

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

    def _update_prop_df(self):  # Top Level update_bet_df
        pass

    def _update_bool_prop_df(self):  # Top Level update_bet_df
        pass

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


if __name__ == "__main__":
    x = ESB_Scraper("NFL")
    self = x
    sp = get_sp1("https://www.elitesportsbook.com/sports/pro-football-futures-betting/2020-2021-nfc-south.sbk")
    # x.run_all_updates()
    # p = ESB_Bool_Prop_Scraper("NFL", "win_totals", sp)
    p = ESB_Prop_Scraper("NFL", "nfc_south", sp)
