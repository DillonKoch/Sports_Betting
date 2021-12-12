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
    def __init__(self, league):
        self.league = league
        self.url_base = "https://www.espn.com/"
        self.url_endings = {"NFL": "nfl/teams",
                            "NBA": "nba/teams",
                            "NCAAF": "college-football/teams",
                            "NCAAB": "mens-college-basketball/teams"}
        self.link = self.url_base + self.url_endings[self.league]
        self.json_path = ROOT_PATH + f"/Data/Teams/{self.league}_Teams.json"

    def create_json(self):  # Top Level
        """
        creates a blank teams json file if it doesn't exist
        """
        new_json = {"Teams": {}, "Other Teams": []}
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w') as f:
                json.dump(new_json, f)

    def load_team_dict(self):  # Top Level
        """
        loads the json dictionary from /Data/Teams/
        """
        with open(self.json_path) as f:
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
        existing_teams = list(team_dict['Teams'].keys()) if os.path.exists(self.json_path) else []
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

    def save_team_dict(self, team_dict):  # Top Level
        """
        saves the updated team dict to /Data/Teams
        """
        with open(self.json_path, 'w') as f:
            json.dump(team_dict, f)

    def run(self):  # Run
        print(self.league)
        self.create_json()
        team_dict = self.load_team_dict()
        sp = self.get_sp1(self.link)
        conference_sections = sp.find_all('div', attrs={'class': 'mt7'})
        for conference_section in conference_sections:
            conference_name = self.conference_name(conference_section)
            teams = conference_section.find_all('div', attrs={'class': 'ContentList__Item'})
            for team in teams:
                team_dict = self.update_json(team_dict, conference_name, team)

        self.save_team_dict(team_dict)


if __name__ == '__main__':
    for league in ["NFL", "NCAAF", "NBA", "NCAAB"]:
        x = ESPN_Team_Scraper(league)
        x.run()
