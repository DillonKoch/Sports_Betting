# ==============================================================================
# File: esb_prop_scraper.py
# Project: ESB
# File Created: Wednesday, 17th June 2020 6:37:45 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 23rd June 2020 1:15:56 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for prop bets on Elite Sportsbook
# ==============================================================================

import datetime
import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import get_sp1


class ESB_Bool_Prop_Scraper:
    def __init__(self, league, bet_name, sp):
        self.league = league
        self.bet_name = bet_name
        self.sp = sp
        self.df_path = ROOT_PATH + "/ESB_Data/{}/{}.csv".format(self.league, self.bet_name)

    def _get_scrape_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def check_df_exists(self):  # Top Level update_df
        try:
            _ = pd.read_csv(self.df_path)
            return True
        except FileNotFoundError:
            return False

    def _create_prop_df(self):  # Specific Helper make_new_df
        cols = ["Title", "description", "Team", "Option", "Odds", "scraped_ts"]
        df = pd.DataFrame(columns=cols)
        return df

    def _get_sp_title(self):  # Specific Helper make_new_df
        title = self.sp.find_all('div', attrs={'id': 'eventTitleBar'})[0].get_text().strip()
        return title

    def _get_sp_description(self):  # Specific Helper make_new_df
        try:
            description = self.sp.find_all('div', attrs={'id': 'futureDescription'})[0].get_text()
        except IndexError:
            print("No description found")
            description = None
        return description

    def _get_bets(self):  # Specific Helper make_new_df
        headers = self.sp.find_all('div', attrs={'class': 'row event eventheading'})
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

    def make_new_df(self, save):  # Top Level
        df = self._create_prop_df()
        title = self._get_sp_title()
        description = self._get_sp_description()
        bets = self._get_bets()
        scraped_ts = self._get_scrape_ts()
        for bet in bets:
            df.loc[len(df)] = [title, description, bet[0], bet[1], bet[2], scraped_ts]
        if save:
            df.to_csv(self.df_path, index=False)
        return df

    def _make_strings(self, lis):  # Specific Helper combine_dfs
        new_lis = []
        for item in lis:
            new_item = []
            for subitem in item:
                new_item.append(str(subitem).replace('+', ''))
            new_lis.append(new_item)
        return new_lis

    def combine_dfs(self, current_df, new_df):  # Top Level
        newest_current = current_df.drop_duplicates(['Title', 'Team', 'Option'], keep="last")
        current_items = [[row['Title'], row['Team'], row['Option'], row['Odds']] for i, row in newest_current.iterrows()]
        new_items = [[row['Title'], row['Team'], row['Option'], row['Odds']] for i, row in new_df.iterrows()]
        current_items = self._make_strings(current_items)
        new_items = self._make_strings(new_items)

        add_indices = []
        for i, item in enumerate(new_items):
            if item not in current_items:
                add_indices.append(i)

        for i in add_indices:
            current_df.loc[len(current_df)] = new_df.iloc[i, :]
            print("Added new bet to {} {}".format(self.league, self.bet_name))
            print(new_items[i][1], new_items[i][2], new_items[i][3])
        return current_df

    def update_df(self):  # Run
        if not self.check_df_exists():
            self.make_new_df(save=True)
            print("New file created for {}".format(self.bet_name))
        else:
            current_df = pd.read_csv(self.df_path)
            new_df = self.make_new_df(save=False)
            full_df = self.combine_dfs(current_df, new_df)
            full_df.to_csv(self.df_path, index=False)


class ESB_Prop_Scraper(ESB_Bool_Prop_Scraper):

    def _create_prop_df(self):  # Specific Helper make_new_df
        cols = ["Title", "description", "Team/Player", "Odds", "scraped_ts"]
        df = pd.DataFrame(columns=cols)
        return df

    def _get_bets(self):  # Specific Helper make_new_df
        teams = self.sp.find_all('span', attrs={'class': 'team'})
        teams += self.sp.find_all('span', attrs={'class': 'team-title'})
        teams = [item.get_text() for item in teams]

        odds = self.sp.find_all('div', attrs={'class': 'market'})
        odds = [item.get_text() for item in odds]
        odds = [item for item in odds if item != "-"]
        return [(team, odd) for team, odd in zip(teams, odds)]

    def make_new_df(self, save):  # Top Level
        df = self._create_prop_df()
        title = self._get_sp_title()
        description = self._get_sp_description()
        bets = self._get_bets()
        scraped_ts = self._get_scrape_ts()
        for bet in bets:
            df.loc[len(df)] = [title, description, bet[0], bet[1], scraped_ts]
        if save:
            df.to_csv(self.df_path, index=False)
        return df

    def combine_dfs(self, current_df, new_df):  # Top Level
        newest_current = current_df.drop_duplicates(['Title', 'Team/Player'], keep="last")
        current_items = [[row['Title'], row['Team/Player'], row['Odds']] for i, row in newest_current.iterrows()]
        new_items = [[row['Title'], row['Team/Player'], row['Odds']] for i, row in new_df.iterrows()]
        current_items = self._make_strings(current_items)
        new_items = self._make_strings(new_items)

        add_indices = []
        for i, item in enumerate(new_items):
            if item not in current_items:
                add_indices.append(i)

        for i in add_indices:
            current_df.loc[len(current_df)] = new_df.iloc[i, :]
            print("Added new bet to {} {}".format(self.league, self.bet_name))
            print(new_items[i][0], new_items[i][1], new_items[i][2])
        return current_df


if __name__ == "__main__":
    sp = get_sp1("https://www.elitesportsbook.com/sports/pro-football-futures-betting/2021-pro-football-championship.sbk")
    x = ESB_Prop_Scraper("NFL", "super_bowl", sp)
    self = x
