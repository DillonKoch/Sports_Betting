# ==============================================================================
# File: esb_base_scraper.py
# Project: ESB
# File Created: Saturday, 22nd August 2020 1:33:35 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 23rd August 2020 11:27:55 am
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Base class for all esb scrapers to inherit from
# subclasses must define an update_df() method
# ==============================================================================

import abc
import datetime
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESB_Base_Scraper(metaclass=abc.ABCMeta):
    def __init__(self, league, bet_name, sp):
        self.league = league
        self.bet_name = bet_name
        self.sp = sp
        self.df_path = ROOT_PATH + "/ESB/Data/{}/{}.csv".format(self.league, self.bet_name)

    @abc.abstractmethod
    def update_df(self):
        """
        - this method is used in esb_perform_scrapes.py
        - must be defined in all scraping subclasses
        """
        pass

    def check_df_exists(self):  # Top Level
        """
        returns True if there is already a dataframe for the bet, otherwise False
        """
        try:
            _ = pd.read_csv(self.df_path)
            return True
        except FileNotFoundError:
            return False

    def create_df(self):  # Top Level
        try:
            df = pd.DataFrame(columns=self.df_cols)
            return df
        except BaseException:
            print("Must create self.df_cols to create a dataframe!")

    def _get_scrape_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def _get_sp_title(self):  # Specific Helper make_new_df
        title = self.sp.find_all('div', attrs={'id': 'eventTitleBar'})[0].get_text().strip()
        return title

    def _get_sp_description(self):  # Specific Helper make_new_df
        try:
            description = self.sp.find_all('div', attrs={'id': 'futureDescription'})[0].get_text()
            description = description.replace('\n', ' ').replace('\t', ' ')
        except IndexError:
            print("No description found")
            description = None
        return description

    def _clean_df_names(self, df):  # Top Level
        """
        any Elite Sportsbook instances where the names are not the same as ESPN
        are corrected here
        """
        df = df.replace("LA Chargers", "Los Angeles Chargers")
        df = df.replace("Los Angeles Clippers", "LA Clippers")
        return df

    def _make_strings(self, lis):  # Specific Helper
        new_lis = []
        for item in lis:
            new_item = []
            for subitem in item:
                try:
                    subitem = float(subitem)
                except ValueError:
                    pass
                except TypeError:
                    pass
                except Exception as e:
                    print(e)
                new_item.append(str(subitem).replace('+', ''))
            new_lis.append(new_item)
        return new_lis

    def combine_dfs(self, current_df, new_df, drop_cols, strings_cols, print_indices):  # Top Level
        newest_current = current_df.drop_duplicates(drop_cols, keep="last")
        current_items = [[row[col] for col in strings_cols] for i, row in newest_current.iterrows()]
        new_items = [[row[col] for col in strings_cols] for i, row in new_df.iterrows()]
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
            print(new_items[i][0], new_items[i][1], new_items[i][2])
            print_items = [new_items[i][j] for j in print_indices]
            for item in print_items:
                print(item)
        return current_df


if __name__ == "__main__":
    x = ESB_Base_Scraper("NFL", "Game_Lines", None)
    self = x
