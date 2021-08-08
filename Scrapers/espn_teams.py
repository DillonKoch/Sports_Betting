# ==============================================================================
# File: espn_teams.py
# Project: Scrapers
# File Created: Monday, 14th June 2021 10:42:42 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 14th June 2021 10:42:43 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping the team names for each league to the official team lists
# ==============================================================================


import datetime
import sys
import time
import urllib.request
from os.path import abspath, dirname

import pandas as pd
from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Team_Scraper:
    def __init__(self):
        self.url_base = "https://www.espn.com/"
        self.url_endings = {"NFL": "nfl/teams",
                            "NBA": "nba/teams",
                            "NCAAF": "college-football/teams",
                            "NCAAB": "mens-college-basketball/teams"}

    def blank_output(self):  # Top Level
        """
        creates a blank output to be populated with team data
        """
        cols = ["League", "Conference/Division", "Team"]
        df = pd.DataFrame(columns=cols)
        return df

    def get_sp1(self, link):  # Top Level
        """
        scrapes the HTML from a link
        """
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        return sp

    def conference_name(self, conference_section):  # Top Level
        """
        retrieves the conference name from the HTML conference section
        """
        conference_name = conference_section.find_all('div', attrs={'class': 'headline headline pb4 n8 fw-heavy clr-gray-01'})
        conference_name = conference_name[0].get_text()
        return conference_name

    def conference_teams(self, conference_section):  # Top Level
        """
        retrieves the conference teams from the HTML conference section
        """
        teams = conference_section.find_all('h2', attrs={'class': "di clr-gray-01 h5"})
        teams = [team.get_text() for team in teams]
        return teams

    def update_df(self, df, league, conference_name, teams):  # Top Level
        """
        updates the df with the new data
        """
        for team in teams:
            df.loc[len(df)] = [league, conference_name, team]
        return df

    def save_df(self, df, league):  # Top Level
        """
        Saves the final df to its path in /Data/Teams/
        """
        path = ROOT_PATH + f"/Data/Teams/{league}/{league}_Teams.csv"
        df.to_csv(path, index=False)

    def run(self, league):  # Run
        df = self.blank_output()
        link = self.url_base + self.url_endings[league]
        sp = self.get_sp1(link)
        conference_sections = sp.find_all('div', attrs={'class': 'mt7'})
        for conference_section in conference_sections:
            conference_name = self.conference_name(conference_section)
            teams = self.conference_teams(conference_section)
            df = self.update_df(df, league, conference_name, teams)
        self.save_df(df, league)
        return df

    def run_all(self):  # Run
        print('-' * 50)
        print(datetime.datetime.now())
        for league in ["NFL", "NCAAF", "NBA", "NCAAB"]:
            df = self.run(league)
            print(f"{league} - Saved {len(df)} teams")
            time.sleep(3)


if __name__ == '__main__':
    x = ESPN_Team_Scraper()
    self = x
    league = "NCAAB"
    # df = x.run(league)
    x.run_all()
