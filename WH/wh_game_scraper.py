# ==============================================================================
# File: wh_game_scraper.py
# Project: WH
# File Created: Saturday, 29th August 2020 5:17:52 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 30th August 2020 8:36:38 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Game scraper for william hill sportsbook
# https://stackoverflow.com/questions/7867537/how-to-select-a-drop-down-menu-value-with-selenium-using-python
# https://selenium-python.readthedocs.io/locating-elements.html
# ==============================================================================


import re
import sys
import time
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from selenium import webdriver


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.selenium_scraper import Selenium_Scraper
# from WH.wh_base_scraper import WH_Base_Scraper


class WH_Game_Scraper:
    def __init__(self, league, bet_name):
        self.league = league
        self.bet_name = bet_name
        sport = "football" if self.league in ["NFL", "NCAAF"] else "basketball"
        self.today_link = "https://www.williamhill.com/us/nj/bet/{}/events/today".format(sport)
        self.all_link = "https://www.williamhill.com/us/nj/bet/{}/events/all".format(sport)

    def get_all_leagues_sp(self, link):  # Top Level
        """
        given a link for games today or all games, this method will expand all the league dropdowns
        and return the sp with all game information
        - link to great stackoverflow post in header
        """
        driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')
        driver.get(link)

        # while there are still leagues to expand, we'll expand them
        try:
            while True:
                driver.find_element_by_xpath("//div[@class='expanderHeader collapsed']").click()
                time.sleep(1)
        except BaseException:
            print("No more leagues to expand")

        html = driver.page_source
        sp = soup(html, 'html.parser')
        driver.close()
        return sp

    def find_league_section(self, sp):  # Top Level
        """
        finds all the league sections, then once it finds a match with self.league, will
        return only the section for the current league we care about
        """
        league_sections = sp.find_all('div', attrs={'class': 'Expander has--toggle competitionExpander'})
        for section in league_sections:
            league_name = section.find_all('span', attrs={'class': 'title'})[0].get_text()
            print(f"Found section for league: {league_name}")
            if league_name == self.league:
                return section

        raise ValueError(f"Could not find a section for league: {self.league}!")

    def find_games_sections(self, league_section):  # Top Level
        pass

    def get_event_info(self, event):  # Specific Helper update_df
        date = event.find_all('div', attrs={'class': 'dateContainer'})
        game_time = date[0].get_text()
        print(f"game time: {game_time}")

        teams = event.find_all('span', attrs={'class': 'truncate2Rows'})
        teams = [item.get_text() for item in teams]
        away_name, home_name = teams
        print(f"Home: {home_name}")
        print(f"Away: {away_name}")

        col2_header = event.find_all('div', attrs={'class': 'header selectionHeader truncate3Rows col2'})
        print(col2_header[0].get_text())

        spread_ml_comp = re.compile(r"^((\+|\-)\d+.\d+)((\+|\-)\d+)$")
        spreads = event.find_all('div', attrs={'class': 'selectionContainer col2'})
        spreads = [item.get_text().strip() for item in spreads]

        away_spread = re.search(spread_ml_comp, spreads[0]).group(1)
        away_spread_ml = re.search(spread_ml_comp, spreads[0]).group(3)

        home_spread = re.search(spread_ml_comp, spreads[1]).group(1)
        home_spread_ml = re.search(spread_ml_comp, spreads[1]).group(3)

        print(f"home spread: {home_spread} ({home_spread_ml})")
        print(f"away spread: {away_spread} ({away_spread_ml})")

        col3_header = event.find_all('div', attrs={'class': 'header selectionHeader truncate3Rows col3'})
        print(col3_header[0].get_text())

        moneylines = event.find_all('div', attrs={'class': 'selectionContainer col3'})
        away_ml, home_ml = [item.get_text().strip() for item in moneylines]

        print(f"home moneyline: {home_ml}")
        print(f"away moneyline: {away_ml}")

        col4_header = event.find_all('div', attrs={'class': 'header selectionHeader truncate3Rows col4'})
        print(col4_header[0].get_text())

        totals = event.find_all('div', attrs={'class': 'selectionContainer col4'})
        totals = [item.get_text() for item in totals]

        total_comp = re.compile(r"^(Over|Under)  (\d+.\d+)((\-|\+)\d+)$")
        over_label = re.search(total_comp, totals[0]).group(1)
        over_amount = re.search(total_comp, totals[0]).group(2)
        over_total_ml = re.search(total_comp, totals[0]).group(3)

        under_label = re.search(total_comp, totals[1]).group(1)
        under_amount = re.search(total_comp, totals[1]).group(2)
        under_total_ml = re.search(total_comp, totals[1]).group(3)

        print(f"Over ({over_label}): {over_amount} ({over_total_ml})")
        print(f"Under ({under_label}): {under_amount} ({under_total_ml})")

        more_bets_link = event.find_all('div', attrs={'class': 'footer'})
        more_bets_link = more_bets_link[0].find_all(href=True)
        more_bets_link = more_bets_link[0]['href']
        print(more_bets_link)

    def update_df(self):  # Run
        today_sp = self.get_all_leagues_sp(self.today_link)
        league_section = self.find_league_section(today_sp)
        events = league_section.find_all('div', attrs={'class': 'eventContainer'})
        for event in events:
            info = self.get_event_info(event)

        # games_sections = self.find_games_sections(league_section)
        # all_sp = self.get_all_leagues_sp(self.all_link)
if __name__ == "__main__":
    # link = "https://www.williamhill.com/us/nj/bet/football/events/all"
    # s = Selenium_Scraper(link, ["Hockey"])
    # sp = s.run()
    sp = None
    x = WH_Game_Scraper("NBA", "Game_Lines")
    self = x
    # sp = x.get_all_leagues_sp()

    # my_select = Select(driver.find_element_by_tag_name('svg'))
    # # for item in my_select.options:
    # #     print(item.text)

    # new_link = driver.find_element_by_css("NFL")
    # mySelect = Select(driver.find_element_by_id(""))
    # # mySelect = Select(driver.find_element_by_id("mySelectID"))
    # mySelect.select_by_visible_text("NFL")
