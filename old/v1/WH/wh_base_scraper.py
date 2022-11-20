# ==============================================================================
# File: wh_base_scraper.py
# Project: Data
# File Created: Saturday, 29th August 2020 4:57:15 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 1st September 2020 4:45:39 pm
# Modified By: Dillon Koch
# -----
#
# -----
# base scraper for all william hill sportsbook scrapers
# ==============================================================================


import abc
import sys
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class WH_Base_Scraper(metaclass=abc.ABCMeta):
    def __init__(self, league, bet_name, sp=None):
        self.league = league
        self.bet_name = bet_name
        self.sp = sp
        self.df_path = ROOT_PATH + "/WH/Data/{}/{}.csv".format(self.league, self.bet_name)

    @abc.abstractmethod
    def update_df(self):
        """
        each sub-scraper must have an update_df method for wh_perform_scrapes.py
        """
        pass

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
    pass
