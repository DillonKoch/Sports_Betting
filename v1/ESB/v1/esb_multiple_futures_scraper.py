# ==============================================================================
# File: esb_multiple_futures_scraper.py
# Project: ESB_Scrapers
# File Created: Wednesday, 19th August 2020 10:11:48 am
# Author: Dillon Koch
# -----
# Last Modified: Monday, 24th August 2020 7:52:58 am
# Modified By: Dillon Koch
# -----
#
# -----
# File for scraping pages that show multiple different futures bets
# for example, this was used for NBA Playoff Series exact results bets
# where it had multiple sections for each series
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESB.esb_base_scraper import ESB_Base_Scraper


class ESB_Multiple_Futures_Scraper(ESB_Base_Scraper):
    """
    class for scraping ESB pages with multiple futures bets shown on the same page
    """

    def __init__(self, league, bet_name, sp):
        super().__init__(league, bet_name, sp)

    @property
    def df_cols(self):
        cols = ["Title", "Description", "Option", "Odds", "scraped_ts"]
        return cols

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
            try:
                title = self._get_section_title(section)
                description = self._get_section_description(section)
                bet_options = self._get_section_bet_options(section)
                bet_odds = self._get_section_bet_odds(section)
                assert len(bet_odds) == len(bet_options)
                print("successfully found section!")
            except Exception as e:
                print("Error with section ({})".format(e))
                continue

            for bet_option, bet_odd in zip(bet_options, bet_odds):
                new_bet = [title, description, bet_option, bet_odd, scraped_ts]
                bets.append(new_bet)
        return bets

    def make_new_df(self, save):  # Top Level
        df = self.create_df()
        bets = self._get_bets()
        for bet in bets:
            df.loc[len(df)] = bet
        if save:
            df.to_csv(self.df_path, index=False)
        return df

    def update_df(self):  # Run
        if not self.check_df_exists():
            self.make_new_df(save=True)
            print("-" * 25)
            print("New file created for {}".format(self.bet_name))
            print("-" * 25)
        else:
            current_df = pd.read_csv(self.df_path)
            new_df = self.make_new_df(save=False)

            drop_cols = ['Title', 'Description', 'Option']
            strings_cols = ['Title', 'Description', 'Option', 'Odds']
            print_indices = [0, 1, 2, 3]
            full_df = self.combine_dfs(current_df, new_df, drop_cols, strings_cols, print_indices)
            full_df.to_csv(self.df_path, index=False)


if __name__ == "__main__":
    from Utility.selenium_scraper import Selenium_Scraper

    links_to_click = [
        "IOWA",
        "BET NOW",
        "NBA",
        "Futures",
        "Playoff Series Exact Result"]
    start_site = "https://www.elitesportsbook.com/sports/home.sbk"
    s = Selenium_Scraper(start_site, links_to_click)
    sp = s.run()
    x = ESB_Multiple_Futures_Scraper("NBA", "Playoff_Series_Exact_Result", sp)
    self = x
    x.update_df()
