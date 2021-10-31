# ==============================================================================
# File: espn_players.py
# Project: allison
# File Created: Friday, 29th October 2021 3:05:35 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 29th October 2021 3:05:36 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping basic player data from espn.com (height, weight, college, etc - not stats)
# ==============================================================================

import datetime
import os
import re
import sys
import time
import urllib.request
from os.path import abspath, dirname

import pandas as pd
from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Players:
    def __init__(self, league):
        self.league = league
        self.df_cols = ['Player_ID', 'Player', 'Team', 'Number', 'Position', 'Height', 'Weight',
                        'Birth_Date', 'Birth_Place', 'College', 'Draft_Year', 'Draft_Round', 'Draft_Pick', 'Draft_Team',
                        'Experience', 'Status', 'Team_History', 'Career_Highlights', 'scrape_ts']
        self.player_dict_keys = ['Team', 'Position', 'HT/WT', 'DOB', 'College', 'Draft Info', 'Status',
                                 'Experience', 'Birthplace', 'Number', 'Name']

    def load_player_df(self):  # Top Level
        """
        loading the player df from /Data/ESPN/{league}/players.csv if it exists, or creating it
        """
        path = ROOT_PATH + f"/Data/ESPN/{self.league}/Players.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame(columns=self.df_cols)
        return df

    def load_stats_df(self):  # Top Level
        """
        loading the df from /Data/ESPN/{league}/Player_Stats.csv
        """
        path = ROOT_PATH + f"/Data/ESPN/{self.league}/Player_Stats.csv"
        df = pd.read_csv(path)
        return df

    def get_unscraped_player_ids(self, player_df, stats_df):  # Top Level
        """
        locating the player ids that have not been scraped yet
        - showing up in stats.csv but not players.csv
        """
        player_df_ids = list(set(list(player_df['Player_ID'])))
        stats_df_ids = stats_df['Player_ID'][stats_df['Player_ID'].notnull()].tolist()
        stats_df_ids = list(set(stats_df_ids))

        player_df_ids = [int(item) for item in player_df_ids]
        stats_df_ids = [int(item) for item in stats_df_ids]
        unscraped_player_ids = [pid for pid in stats_df_ids if pid not in player_df_ids]
        return unscraped_player_ids

    def _new_player_dict(self, player_id):  # Specific Helper scrape_player_data
        """
        blank dict to store the player data before putting it in the df
        """
        player_dict = {key: None for key in self.player_dict_keys}
        player_dict['Player_ID'] = player_id
        return player_dict

    def _get_sp1(self, link):  # Specific Helper scrape_player_data
        """
        scraping HTML from a link
        """
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        time.sleep(5)
        return sp

    def _bio_item_to_player_dict(self, player_dict, bio_item):  # Specific Helper scrape_player_data
        bio_label = bio_item.find('span', attrs={'class': 'Bio__Label ttu mr2 dib clr-gray-04'})
        bio_value = bio_item.find('span', attrs={'class': 'dib flex-uniform mr3 clr-gray-01'})
        if bio_label is not None:
            player_dict[bio_label.get_text().strip()] = bio_value.get_text().strip()
        return player_dict

    def _number(self, header_sp):  # Specific Helper scrape_player_data
        """
        scraping a player's number from the header_sp
        """
        item_sps = header_sp.find_all('li')
        number_comp = re.compile(r"^#\d{1,2}$")
        number = None
        for item_sp in item_sps:
            item_text = item_sp.get_text().strip()
            if re.match(number_comp, item_text):
                number = item_text.replace('#', '')
        return number

    def _name(self, header_sp):  # Specific Helper scrape_player_data
        first_name = header_sp.find('span', attrs={'class': 'truncate min-w-0 fw-light'}).get_text().strip()
        last_name = header_sp.find('span', attrs={'class': 'truncate min-w-0'}).get_text().strip()
        return first_name + ' ' + last_name

    def _team_history(self, sp):  # Specific Helper scrape_player_data
        history_sp = sp.find('div', attrs={'class': 'Wrapper Card__Content Career__History__Content'})
        if history_sp is None:
            return None
        team_items = history_sp.find_all('a', attrs={'class': 'AnchorLink Career__History__Item n8 mb4 flex align-center'})
        history_str = ""
        for team_item in team_items:
            team = team_item.find('span', attrs={'class': 'db n8 clr-black'}).get_text().strip()
            seasons = team_item.find('span', attrs={'class': 'db n10 clr-gray-05'}).get_text().strip()
            history_str += team + ' ' + seasons + ', '
        return history_str[:-2]

    def _career_highlights(self, sp):  # Specific Helper scrape_player_data
        highlights_sp = sp.find('div', attrs={'class': 'Wrapper Card__Content Career__Highlights__Content'})
        if highlights_sp is None:
            return None

        highlight_items = highlights_sp.find_all('div', attrs={'class': 'Career__Highlights__Item n8 mb4 flex align-center'})
        highlights_str = ""
        for highlight_item in highlight_items:
            count_name_sp = highlight_item.find('div', attrs={'class': 'clr-black'})
            count_name_spans = count_name_sp.find_all('span')
            count_name = ' '.join([item.get_text() for item in count_name_spans])
            seasons = highlight_item.find('div', attrs={'class': 'n10 clr-gray-05'}).get_text().strip()
            highlights_str += count_name + ' ' + seasons + ', '
        return highlights_str[:-2]

    def scrape_player_data(self, player_id):  # Top Level
        """
        scraping data from the player's ESPN bio
        """
        link = f"https://www.espn.com/{self.league.lower()}/player/bio/_/id/{int(player_id)}/"
        link = link.replace('ncaaf', 'college-football').replace('ncaab', 'mens-college-basketball')
        print(link)
        sp = self._get_sp1(link)
        header_sp = sp.find('div', attrs={'class': 'ResponsiveWrapper'})
        bio_sp = sp.find('section', attrs={'class': 'Card Bio'})
        bio_items = bio_sp.find_all('div', attrs={'class': 'Bio__Item n8 mb4'})

        player_dict = self._new_player_dict(player_id)
        for bio_item in bio_items:
            player_dict = self._bio_item_to_player_dict(player_dict, bio_item)
        player_dict['Number'] = self._number(header_sp)
        player_dict['Name'] = self._name(header_sp)
        player_dict['Team_History'] = self._team_history(sp)
        player_dict['Career_Highlights'] = self._career_highlights(sp)
        return player_dict

    def _draft_info(self, draft_str):  # Specific Helper player_dict_to_df
        """
        """
        if draft_str is None:
            return (None, None, None, None)
        draft_comp = re.compile(r"^(\d{4}): Rd (\d{1}), Pk (\d{1,2}) (.+)")
        match = re.match(draft_comp, draft_str)
        if match:
            return match.group(1), match.group(2), match.group(3), match.group(4).replace("(", "").replace(")", "")
        else:
            return (None, None, None, None)

    def player_dict_to_df(self, player_id, player_df, player_dict):  # Top Level
        height, weight = player_dict['HT/WT'].split(',') if player_dict['HT/WT'] is not None else (None, None)
        draft_year, draft_round, draft_pick, draft_team = self._draft_info(player_dict['Draft Info'])
        new_row = [player_id, player_dict['Name'], player_dict['Team'], player_dict['Number'],
                   player_dict['Position'], height, weight, player_dict['DOB'], player_dict['Birthplace'], player_dict['College'],
                   draft_year, draft_round, draft_pick, draft_team, player_dict['Experience'],
                   player_dict['Status'], player_dict['Team_History'], player_dict['Career_Highlights'],
                   datetime.datetime.now().strftime("%Y-%m-%d %H:%M")]
        player_df.loc[len(player_df)] = new_row
        return player_df

    def run(self):  # Run
        player_df = self.load_player_df()
        stats_df = self.load_stats_df()
        unscraped_player_ids = self.get_unscraped_player_ids(player_df, stats_df)
        for i, unscraped_player_id in enumerate(unscraped_player_ids):
            try:
                print(f"{i}/{len(unscraped_player_ids)}")
                player_dict = self.scrape_player_data(unscraped_player_id)
                player_df = self.player_dict_to_df(unscraped_player_id, player_df, player_dict)
                player_df.to_csv(f"{ROOT_PATH}/Data/ESPN/{self.league}/Players.csv", index=False)
                print(player_dict['Name'])
            except Exception as e:
                print(e)
                print(f"{unscraped_player_id} failed")


if __name__ == '__main__':
    league = "NFL"
    x = ESPN_Players(league)
    self = x
    player_df = x.load_player_df()
    player_id = '112'
    player_id = '6430'
    # x.scrape_player_data(player_id)
    x.run()
