# ==============================================================================
# File: espn_teams.py
# Project: allison
# File Created: Sunday, 8th August 2021 8:49:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 8th August 2021 8:49:10 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraping the teams for NFL/NBA/NCAAF/NCAAB from espn.com
# using these as the official team names for the whole project
# Creating JSON files for each league in /Data/Teams/
# ==============================================================================


import copy
import datetime
import json
import os
import sys
import time
import urllib.request
from os.path import abspath, dirname

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

    def create_json(self, league):  # Top Level
        """
        creates a blank teams json file if it doesn't exist
        """
        path = ROOT_PATH + f"/Data/Teams/{league}_Teams.json"
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump({}, f)

    def load_team_dict(self, league):  # Top Level
        """
        loads the json dictionary from /Data/Teams/
        """
        path = ROOT_PATH + f"/Data/Teams/{league}_Teams.json"
        with open(path) as f:
            team_dict = json.load(f)
        return team_dict

    def get_sp1(self, link):  # Top Level
        """
        scrapes the HTML from a link
        """
        time.sleep(2)
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

    def _get_link(self, links, link_chunk):  # Specific Helper  update_json
        """
        gets the ESPN link to a particular team page (e.g. stats, schedule, roster, etc.)
        """
        eligible_links = [link for link in links if link_chunk in link]
        if len(eligible_links) > 0:
            return "https://www.espn.com" + eligible_links[0]
        return ""

    def update_json(self, team_dict, conference_name, team):  # Top Level
        """
        updates the json file with any changes found from scraping
        """
        existing_teams = list(team_dict['Teams'].keys())
        team_name = team.find_all('h2')[0].get_text()
        if team_name not in existing_teams:
            team_dict['Teams'][team_name] = {"Conference": conference_name, "Other Names": [], "Statistics": "",
                                             "Schedule": "", "Roster": "", "Depth Chart": ""}
        links = [item['href'] for item in team.find_all('a', attrs={'class': 'AnchorLink'}, href=True)]

        team_dict['Teams'][team_name]['Statistics'] = self._get_link(links, '/stats/')
        team_dict['Teams'][team_name]['Schedule'] = self._get_link(links, '/schedule/')
        team_dict['Teams'][team_name]['Roster'] = self._get_link(links, '/roster/')
        team_dict['Teams'][team_name]['Depth Chart'] = self._get_link(links, '/depth/')
        return team_dict

    def save_team_dict(self, league, team_dict):  # Top Level
        """
        saves the updated team dict to /Data/Teams
        """
        path = ROOT_PATH + f"/Data/Teams/{league}_Teams.json"
        with open(path, 'w') as f:
            json.dump(team_dict, f)

    def run(self, league):  # Run
        print(league)
        self.create_json(league)
        team_dict = self.load_team_dict(league)
        original_team_dict = copy.deepcopy(team_dict)
        link = self.url_base + self.url_endings[league]
        sp = self.get_sp1(link)
        conference_sections = sp.find_all('div', attrs={'class': 'mt7'})
        for conference_section in conference_sections:
            conference_name = self.conference_name(conference_section)
            teams = conference_section.find_all('div', attrs={'class': 'ContentList__Item'})
            for team in teams:
                team_dict = self.update_json(team_dict, conference_name, team)

        # * saving new data or skipping, printing to log
        print(datetime.datetime.now())
        if team_dict != original_team_dict:
            self.save_team_dict(league, team_dict)
            print('saving new data...')
        else:
            print('no new data, not saving')


if __name__ == '__main__':
    x = ESPN_Team_Scraper()
    self = x
    for league in ["NFL", "NCAAF", "NBA", "NCAAB"]:
        x.run(league)
