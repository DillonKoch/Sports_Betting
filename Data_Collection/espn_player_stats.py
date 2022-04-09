# ==============================================================================
# File: espn_player_stats.py
# Project: allison
# File Created: Sunday, 17th October 2021 9:25:04 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 17th October 2021 9:25:04 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraping players stats from ESPN.com for each game since 2007
# ==============================================================================

import os
import sys
import time
import urllib.request
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Player_Stats:
    def __init__(self, league):
        # ! league/path setup
        self.league = league
        self.stats_path = ROOT_PATH + f"/Data/ESPN/{self.league}/Player_Stats.csv"
        self.football_league = league in ['NFL', 'NCAAF']

        # ! football stat columns
        passing = ['Passing_Comp_Att', 'Passing_Yards', 'Avg_Yards_per_Pass', 'Passing_Touchdowns', 'Interceptions_Thrown',
                   'Times_Sacked', 'QBR', 'Passer_Rating']
        rushing = ['Carries', 'Rushing_Yards', 'Avg_Yards_per_Rush', 'Rushing_Touchdowns', 'Longest_Rush']
        receiving = ['Receptions', 'Receiving_Yards', 'Yards_per_Catch', 'Receiving_Touchdowns', 'Longest_Reception', 'Targets']
        fumbles = ['Fumbles', 'Fumbles_Lost', 'Fumbles_Recovered']
        defensive = ['Tackles', 'Solo_Tackles', 'Sacks', 'Tackles_for_Loss', 'QB_Hurries', 'Passes_Defended',
                     'QB_Hits', 'Touchdowns']
        interceptions = ['Interceptions_Caught', 'Interception_Return_Yards', 'Pick_Sixes']
        kick_returns = ['Kicks_Returned', 'Kick_Return_Yards', 'Avg_Kick_Return_Yards', 'Longest_Kick_Return', 'Kick_Return_Touchdowns']
        punt_returns = ['Punts_Returned', 'Punt_Return_Yards', 'Avg_Punt_Return_Yards', 'Longest_Punt_Return', 'Punt_Return_Touchdowns']
        kicking = ['FG_Made_Att', 'FG_Pct', 'Longest_Field_Goal', 'XP_Made_Att', 'Kicking_Points']
        punting = ['Punts', 'Punt_Yards', 'Touchbacks', 'Punts_Inside_20', 'Longest_Punt']
        self.football_cols = passing + rushing + receiving + fumbles + defensive + interceptions + kick_returns + punt_returns + kicking + punting

        # ! basketball stat columns
        self.basketball_cols = ['Minutes', 'FG', '3PT', 'FT', 'Offensive_Rebounds',
                                'Defensive_Rebounds', 'Total_Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers', 'Fouls', 'Plus_Minus', 'Points']

        # ! overall column setup
        self.columns = self.football_cols if self.football_league else self.basketball_cols
        self.columns = ['Game_ID', 'Date', 'Team', 'Player', 'Player_ID', 'Position'] + self.columns

    def make_load_df(self):  # Top Level
        """
        creating/updating the Stats.csv file
        """
        stats_df = pd.read_csv(self.stats_path) if os.path.exists(self.stats_path) else pd.DataFrame(columns=self.columns)
        return stats_df

    def load_new_game_ids_date_home_away(self, stats_df):  # Top Level
        """
        loading Game_ID's from Games.csv that are not in Stats.csv yet
        - returning new game ID's and the home/away teams in those games
        """
        games_path = ROOT_PATH + f"/Data/ESPN/{self.league}/Games.csv"
        games_df = pd.read_csv(games_path)
        games_df = games_df.loc[games_df['Final_Status'].notnull()]
        games_df_game_ids = list(games_df['Game_ID'])
        stats_df_game_ids = list(stats_df['Game_ID'])
        new_game_ids = [item for item in games_df_game_ids if item not in stats_df_game_ids]
        new_games_df = games_df.loc[games_df['Game_ID'].isin(new_game_ids)]
        dates = list(new_games_df['Date'])
        home_teams = list(new_games_df['Home'])
        away_teams = list(new_games_df['Away'])
        return new_game_ids, dates, home_teams, away_teams

    def get_stats_link(self, new_game_id):  # Top Level
        """
        creating the link to the box score for a new_game_id
        """
        ncaab_str = "mens-college-basketball"
        ncaaf_str = "college-football"
        nfl_str = "nfl"
        nba_str = "nba"
        str_dict = {"NFL": nfl_str, "NBA": nba_str, "NCAAF": ncaaf_str, "NCAAB": ncaab_str}
        stats_link = f"https://www.espn.com/{str_dict[self.league]}/boxscore/_/gameId/{new_game_id}"
        print(stats_link)
        return stats_link

    def _get_sp(self, link):  # Specific Helper scrape_stats
        """
        scraping HTML from a link
        """
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        print('start sleep')
        time.sleep(5)
        print('end sleep')
        return sp

    def _sp_section_to_rows(self, sp_section):  # Global Helper
        """
        going through the common process of converting an sp section to the rows of each player
        """
        bodies = sp_section.find_all('tbody')
        row_lists = [body.find_all('tr', attrs={'class': ''}) for body in bodies]
        rows = [subitem for item in row_lists for subitem in item]
        return rows

    def _blank_football_stat_dict(self, new_game_id, date, player_name, player_id, team_name):  # Global Helper
        stat_dict = {col: None for col in self.columns}
        stat_dict['Game_ID'] = new_game_id
        stat_dict['Date'] = date
        stat_dict['Player'] = player_name
        stat_dict['Player_ID'] = player_id
        stat_dict['Team'] = team_name
        return stat_dict

    def _football_boxscore_to_rows(self, boxscore, stat_name, home_away):  # Global Helper
        stat_sp = boxscore.find('div', attrs={'id': f'gamepackage-{stat_name}'})
        if stat_sp is None:
            print(f"NO {stat_name} STATS FOUND")
            return []
        col_num = 'two' if home_away == 'home' else 'one'
        home_away_sp = stat_sp.find('div', attrs={'class': f'col column-{col_num} gamepackage-{home_away}-wrap'})
        rows = self._sp_section_to_rows(home_away_sp)
        rows = [row for row in rows if len(row.find_all('td', attrs={'class': 'name'})) > 0]
        return rows

    def _rows_to_stat_dicts(self, rows, stat_dicts, class_col_dict, new_game_id, date, team_name):  # Global Helper
        """
        converting the rows found in the boxscore to the stat_dicts, used in each footbal stat
        """
        for row in rows:
            link_sp = row.find('a', href=True)
            # * if there's no link, it's not actually a player -> move on
            if link_sp is None:
                continue
            player_link = link_sp['href']
            player_name = player_link.split('/')[-1]
            player_id = player_link.split('/')[-2]
            if player_id not in stat_dicts:
                stat_dicts[player_id] = self._blank_football_stat_dict(new_game_id, date, player_name, player_id, team_name)

            for stat in list(class_col_dict.keys()):
                row_class = class_col_dict[stat]
                stat_val = row.find_all('td', attrs={'class': row_class})
                if len(stat_val) > 0:
                    stat_dicts[player_id][stat] = stat_val[0].get_text().replace("--", "")
        return stat_dicts

    def _scrape_passing(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'passing', home_away)
        passing_class_col_dict = {'Passing_Comp_Att': "c-att", "Passing_Yards": "yds",
                                  "Avg_Yards_per_Pass": "avg", "Passing_Touchdowns": "td",
                                  "Interceptions_Thrown": "int", 'Times_Sacked': 'sacks',
                                  'QBR': 'qbr', "Passer_Rating": "rtg"}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, passing_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_rushing(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'rushing', home_away)
        rushing_class_col_dict = {'Carries': 'car', 'Rushing_Yards': 'yds', 'Avg_Yards_per_Rush': 'avg',
                                  'Rushing_Touchdowns': 'td', 'Lontest_Rush': 'long'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, rushing_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_receiving(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'receiving', home_away)
        receiving_class_col_dict = {'Receptions': 'rec', 'Receiving_Yards': 'yds', 'Yards_per_Catch': 'avg',
                                    'Receiving_Touchdowns': 'td', 'Longest_Reception': 'long', 'Targets': 'tgts'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, receiving_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_fumbles(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'fumbles', home_away)
        fumbles_class_col_dict = {'Fumbles': 'fum', 'Fumbles_Lost': 'lost', 'Fumbles_Recovered': 'rec'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, fumbles_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_defensive(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'defensive', home_away)
        defensive_class_col_dict = {'Tackles': 'tot', 'Solo_Tackles': 'solo', 'Sacks': 'sacks',
                                    'Tackles_for_Loss': 'tfl', 'QB_Hurries': 'qb hur',
                                    'Passes_Defended': 'pd', 'QB_Hits': 'qb hts', 'Touchdowns': 'td'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, defensive_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_interceptions(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'interceptions', home_away)
        interceptions_class_col_dict = {'Interceptions_Caught': 'int', 'Interception_Return_Yards': 'yds',
                                        'Pick_Sixes': 'td'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, interceptions_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_kick_returns(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'kickReturns', home_away)
        kick_returns_class_col_dict = {'Kicks_Returned': 'no', 'Kick_Return_Yards': 'yds',
                                       'Average_Kick_Return_Yards': 'avg',
                                       'Longest_Kick_Return': 'long', 'Kick_Return_Touchdowns': 'td'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, kick_returns_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_punt_returns(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'puntReturns', home_away)
        punt_returns_class_col_dict = {'Punts_Returned': 'no', 'Punt_Return_Yards': 'yds',
                                       'Average_Punt_Return_Yards': 'avg',
                                       'Longest_Punt_Return': 'long', 'Punt_Return_Touchdowns': 'td'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, punt_returns_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_kicking(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'kicking', home_away)
        kicking_class_col_dict = {'FG_Made_Att': 'fg', 'FG_Pct': 'pct', 'Longest_Field_Goal': 'long',
                                  'XP_Made_Att': 'xp', 'Kicking_Points': 'pts'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, kicking_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_punting(self, new_game_id, date, boxscore, stat_dicts, home_away, team_name):  # Helping Helper _scrape_football
        rows = self._football_boxscore_to_rows(boxscore, 'punting', home_away)
        punting_class_col_dict = {'Punts': 'no', 'Punt_Yards': 'yds', 'Touchbacks': 'tb',
                                  'Punts_Inside_20': 'in 20', 'Longest_Punt': 'long'}
        stat_dicts = self._rows_to_stat_dicts(rows, stat_dicts, punting_class_col_dict, new_game_id, date, team_name)
        return stat_dicts

    def _scrape_football(self, new_game_id, boxscore, date, team_name, home_away):  # Specific Helper scrape_stats
        stat_dicts = {}
        stat_dicts = self._scrape_passing(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_rushing(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_receiving(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_fumbles(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_defensive(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_interceptions(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_kick_returns(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_punt_returns(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_kicking(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        stat_dicts = self._scrape_punting(new_game_id, date, boxscore, stat_dicts, home_away, team_name)
        return stat_dicts

    def _check_did_not_play(self, row):  # Helping Helper # ! possibly global helper for football
        """
        checks if a player is listed as "Did not play" in a game
        """
        dnp_sp = row.find_all('td', attrs={'class': 'dnp'})
        return len(dnp_sp) > 0

    def _basketball_boxscore_to_rows(self, boxscore, home_away):  # Helping Helper _scrape_basketball
        col_num = 'two' if home_away == 'home' else 'one'
        table = boxscore.find('div', attrs={'class': f'col column-{col_num} gamepackage-{home_away}-wrap'})
        bodies = table.find_all('tbody')
        row_lists = [body.find_all('tr', attrs={"class": ""}) for body in bodies]
        rows = [subitem for item in row_lists for subitem in item]
        return rows

    def _basketball_row_to_player_stat_dict(self, row):  # Helping Helper _scrape_basketball
        did_not_play = self._check_did_not_play(row)
        stat_class_col_dict = {"Minutes": "min", 'FG': 'fg', '3PT': '3pt', 'FT': 'ft',
                               'Offensive_Rebounds': 'oreb', 'Defensive_Rebounds': 'dreb',
                               'Total_Rebounds': 'reb', 'Assists': 'ast', 'Steals': 'stl',
                               'Blocks': 'blk', 'Turnovers': 'to', 'Fouls': 'pf',
                               'Plus_Minus': 'plusminus', 'Points': 'pts'}

        new_stat_dict = {column: None for column in self.columns}
        for stat in list(stat_class_col_dict.keys()):
            row_class = stat_class_col_dict[stat]
            if not did_not_play:
                stat_val = row.find_all('td', attrs={'class': row_class})
                if len(stat_val) > 0:
                    new_stat_dict[stat] = stat_val[0].get_text().replace("--", "")

        # * link information
        link_sp = row.find('a', href=True)
        if link_sp is None:
            return new_stat_dict
        player_link = link_sp['href']
        new_stat_dict['Player'] = player_link.split('/')[-1]
        new_stat_dict['Player_ID'] = player_link.split('/')[-2]
        position = row.find_all('span', attrs={'class': 'position'})
        new_stat_dict['Position'] = position[0].get_text() if len(position) > 0 else None
        return new_stat_dict

    def _scrape_basketball(self, new_game_id, boxscore, date, team_name, home_away):  # Specific Helper scrape_stats
        """
        scraping basketball statistics from the box score, returning list of stat dicts for each player
        """
        rows = self._basketball_boxscore_to_rows(boxscore, home_away)
        stat_dicts = [self._basketball_row_to_player_stat_dict(row) for row in rows]
        for stat_dict in stat_dicts:
            stat_dict['Team'] = team_name
            stat_dict['Game_ID'] = new_game_id
            stat_dict['Date'] = date
        return stat_dicts

    def scrape_stats(self, stats_link, new_game_id, date, home_team, away_team):  # Top Level
        """
        given a link to a game's boxscore, this method scrapes all the player stats into
        a list of 'player_stats_dicts', which is a dict for each player's stats
        """
        sp = self._get_sp(stats_link)
        boxscore = sp.find('div', attrs={"id": ["gamepackage-boxscore-module", "gamepackage-box-score"]})
        if boxscore.get_text().strip() == 'No Box Score Available':
            print("NO BOX SCORE, MOVING ON")
            return []

        if self.football_league:
            home_stats_dicts = self._scrape_football(new_game_id, boxscore, date, home_team, 'home')
            away_stats_dicts = self._scrape_football(new_game_id, boxscore, date, away_team, 'away')
            stats_dicts = list(home_stats_dicts.values()) + list(away_stats_dicts.values())
        else:
            home_stats_dicts = self._scrape_basketball(new_game_id, boxscore, date, home_team, 'home')
            away_stats_dicts = self._scrape_basketball(new_game_id, boxscore, date, away_team, 'away')
            stats_dicts = home_stats_dicts + away_stats_dicts

        return stats_dicts

    def update_csv(self, stats_df, player_stats_dicts):  # Top Level
        """
        updates the stats_df with the player_stats_dicts scraped from a game's box score
        """
        new_df = pd.DataFrame(player_stats_dicts)
        new_df.replace('-', np.nan, inplace=True)
        stats_df = pd.concat([stats_df, new_df])
        # stats_df.replace("-", np.nan, inplace=True)
        stats_df.to_csv(self.stats_path, index=None)
        print(str(len(stats_df)) + " rows")
        print(str(list(stats_df['Date'])[-1]) + " last date")
        return stats_df

    def run(self):  # Run
        stats_df = self.make_load_df()
        new_game_ids, dates, home_teams, away_teams = self.load_new_game_ids_date_home_away(stats_df)
        for i, (new_game_id, date, home_team, away_team) in enumerate(zip(new_game_ids, dates, home_teams, away_teams)):
            try:
                print(f"{i}/{len(new_game_ids)}")
                stats_link = self.get_stats_link(new_game_id)
                player_stats_dicts = self.scrape_stats(stats_link, new_game_id, date, home_team, away_team)
                stats_df = self.update_csv(stats_df, player_stats_dicts)
            except Exception as e:
                print(e)
                print("SLEEPING 10 SECONDS")
                time.sleep(10)


if __name__ == '__main__':
    # for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
    for league in ['NBA']:
        x = ESPN_Player_Stats(league)
        self = x
        x.run()
