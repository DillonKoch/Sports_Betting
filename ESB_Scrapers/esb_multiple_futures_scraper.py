# ==============================================================================
# File: esb_multiple_futures_scraper.py
# Project: ESB_Scrapers
# File Created: Wednesday, 19th August 2020 10:11:48 am
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 19th August 2020 11:34:06 am
# Modified By: Dillon Koch
# -----
#
# -----
# File for scraping pages that show multiple different futures bets
# for example, this was used for NBA Playoff Series exact results bets
# where it had multiple sections for each series
# ==============================================================================


import datetime
import sys
from os.path import abspath, dirname

import pandas as pd

from ESB_Scrapers.esb_selenium import ESB_Selenium

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESB_Multiple_Futures_Scraper:
    """
    class for scraping ESB pages with multiple futures bets shown on the same page
    """

    def __init__(self, league, bet_name, sp):
        self.league = league
        self.bet_name = bet_name
        self.sp = sp
        self.df_path = ROOT_PATH + "/ESB_Data/{}/{}.csv".format(self.league, self.bet_name)

    def check_df_exists(self):  # Top Level update_df
        """
        returns True if there is already a dataframe for the bet, otherwise False
        """
        try:
            _ = pd.read_csv(self.df_path)
            return True
        except FileNotFoundError:
            return False

    def _create_df(self):  # Specific Helper make_new_df
        """
        creates base df for a new multiple futures bet
        """
        cols = ["Title", "Description", "Option", "Odds", "scraped_ts"]
        df = pd.DataFrame(columns=cols)
        return df

    def _get_section_bet_options(self, section):  # Helping Helper _get_bets
        """
        finds all the bet options (e.g. "Heat in 4 Games") in a given section
        """
        options = section.find_all('span', attrs={'class': 'team'})
        options = [item.get_text() for item in options]
        options = [opt for opt in options if opt != 'Selection']
        return options

    def _get_section_bet_odds(self, section):  # Helping Helper _get_bets
        """
        finds all the odds to go along with each bet option in a given section
        - the number of bet options and bet odds must match in each section
        """
        odds = section.find_all('div', attrs={'class': 'market'})
        odds = [item.get_text() for item in odds]
        return odds

    def _get_section_title(self, section):  # Helping Helper _get_bets
        """
        finds the title of a given section
        - e.g. "NBA EXACT SERIES RESULT"
        """
        title = section.find_all('span', attrs={'class': 'titleLabel'})
        title_text = title[0].get_text()
        title_text = title_text.replace('\n', '').replace('\t', '')
        return title_text

    def _get_section_description(self, section):  # Helping Helper _get_bets
        """
        finds the description of a given section
        - e.g. "Exact Series Result | Pacers vs Heat- August 30, 2020 22:00 CDT"
        """
        desc = section.find_all('div', attrs={'id': 'futureDescription'})
        desc_text = desc[0].get_text()
        desc_text = desc_text.replace('\n', '').replace('\t', '')
        return desc_text

    def _get_scrape_ts(self):  # Specific Helper make_new_df
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def _get_bets(self):  # Specific Helper make_new_df
        """
        finds all the bets in all the sections
        - format: lists in the form [title, description, bet_option, bet_odd]
        """
        scraped_ts = self._get_scrape_ts()
        main_content = self.sp.find_all('div', attrs={'id': 'main-content'})
        sections = main_content[0].find_all('div', attrs={'class': 'panel panel-primary'})

        bets = []
        for section in sections:
            title = self._get_section_title(section)
            description = self._get_section_description(section)
            bet_options = self._get_section_bet_options(section)
            bet_odds = self._get_section_bet_odds(section)
            assert len(bet_odds) == len(bet_options)

            for bet_option, bet_odd in zip(bet_options, bet_odds):
                new_bet = [title, description, bet_option, bet_odd, scraped_ts]
                bets.append(new_bet)
        return bets

    def make_new_df(self, save):  # Top Level
        df = self._create_df()
        bets = self._get_bets()
        for bet in bets:
            df.loc[len(df)] = bet
        if save:
            df.to_csv(self.df_path, index=False)
        return df

    def _make_strings(self, lis):  # Specific Helper combine_dfs
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

    def combine_dfs(self, current_df, new_df):  # Top Level
        newest_current = current_df.drop_duplicates(['Title', 'Description', 'Option'], keep="last")
        current_items = [[row['Title'], row['Description'], row['Option'], row['Odds']] for i, row in newest_current.iterrows()]
        new_items = [[row['Title'], row['Description'], row['Option'], row['Odds']] for i, row in new_df.iterrows()]
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
        if not self.check_df_exists():
            self.make_new_df(save=True)
            print("-" * 25)
            print("New file created for {}".format(self.bet_name))
            print("-" * 25)
        else:
            current_df = pd.read_csv(self.df_path)
            new_df = self.make_new_df(save=False)
            full_df = self.combine_dfs(current_df, new_df)
            full_df.to_csv(self.df_path, index=False)


if __name__ == "__main__":
    links_to_click = [
        "IOWA",
        "BET NOW",
        "NBA",
        "Futures",
        "Playoff Series Exact Result"]
    s = ESB_Selenium(links_to_click)
    sp = s.run()
    x = ESB_Multiple_Futures_Scraper("NBA", "Playoff_Series_Exact_Result", sp)
    self = x
    x.update_df()
