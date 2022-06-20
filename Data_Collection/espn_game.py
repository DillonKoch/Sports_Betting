# ==============================================================================
# File: espn_game.py
# Project: allison
# File Created: Tuesday, 10th August 2021 9:19:09 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 10th August 2021 9:19:09 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping game data from espn.com
# given
# ==============================================================================

import copy
import datetime
import re
import sys
import time
import urllib.request
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as soup
from selenium import webdriver

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Game_Scraper:
    def __init__(self, league):
        self.league = league
        self.football_league = league in ['NFL', 'NCAAF']
        self.link_dict = {"NFL": "nfl", "NBA": "nba", "NCAAF": "college-football", "NCAAB": "mens-college-basketball"}

        self.df_cols = ['Game_ID', 'Season', 'Week', 'Date', 'Home', 'Away', 'Home_Record', 'Away_Record', 'Network',
                        'Final_Status', 'H1H', 'H2H', 'H1Q', 'H2Q', 'H3Q', 'H4Q', 'HOT',
                        'A1H', 'A2H', 'A1Q', 'A2Q', 'A3Q', 'A4Q', 'AOT', 'Home_Final', 'Away_Final']

        self.football_stats = ['1st_Downs', 'Passing_1st_downs', 'Rushing_1st_downs', '1st_downs_from_penalties',
                               '3rd_down_efficiency', '4th_down_efficiency', 'Total_Plays', 'Total_Yards', 'Total_Drives',
                               'Yards_per_Play', 'Passing', 'Comp_Att', 'Yards_per_pass', 'Interceptions_thrown',
                               'Sacks_Yards_Lost', 'Rushing', 'Rushing_Attempts', 'Yards_per_rush', 'Red_Zone_Made_Att',
                               'Penalties', 'Turnovers', 'Fumbles_lost', 'Defensive_Special_Teams_TDs',
                               'Possession']

        self.basketball_stats = ['FG', 'Field_Goal_pct', '3PT', 'Three_Point_pct', 'FT', 'Free_Throw_pct', 'Rebounds',
                                 'Offensive_Rebounds', 'Defensive_Rebounds', 'Assists', 'Steals', 'Blocks',
                                 'Total_Turnovers', 'Points_Off_Turnovers', 'Fast_Break_Points', 'Points_in_Paint',
                                 'Fouls', 'Technical_Fouls', 'Flagrant_Fouls', 'Largest_Lead']
        self.start_selenium()

    def start_selenium(self):  # Top Level
        """
        fires up the selenium window to start scraping
        """
        # options = Options()
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # options.headless = False
        self.driver = webdriver.Firefox(executable_path=ROOT_PATH + "/Data_Collection/geckodriver")
        time.sleep(1)

    def get_soup_sp(self):  # Top Level
        """
        saves the selenium window's current page as a beautifulsoup object
        """
        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        return sp

    def load_games_df(self):  # Top Level
        """
        loads the df from /Data/{league}/Games.csv to populate it with new game data
        """
        path = ROOT_PATH + f"/Data/ESPN/{self.league}/Games.csv"
        df = pd.read_csv(path)
        return df

    def add_new_df_cols(self, df):  # Top Level
        """
        adds new columns to the df from self.df_cols if they're not there already
        """
        stats_cols = self.football_stats if self.football_league else self.basketball_stats
        home_away_stats_cols = []
        for stat in stats_cols:
            home_away_stats_cols.append('Home_' + stat)
            home_away_stats_cols.append('Away_' + stat)

        for col in self.df_cols + home_away_stats_cols:
            if col not in list(df.columns):
                df[col] = None
        return df

    def check_today_past_game_date(self, row):  # Top Level
        """
        returns True if today's date is past the game date OR the basic info isn't scraped, False otherwise
        """
        try:
            game_datetime = datetime.datetime.strptime(str(row[3]), "%Y-%m-%d")
            return datetime.datetime.now() > game_datetime
        except ValueError:
            return True

    def _get_sp1(self, link):  # Specific Helper scrape_stats_page, scrape_summary_page
        """
        Scraping HTML of the link
        """
        time.sleep(5)
        # user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        # headers = {'User-Agent': user_agent, }
        # request = urllib.request.Request(link, None, headers)  # The assembled request
        # response = urllib.request.urlopen(request)
        # http = urllib3.PoolManager()
        # response = http.request('GET', link)
        # sp = soup(response.data, 'html.parser')

        # a = response.read().decode('utf-8', 'ignore')
        # sp = soup(a, 'html.parser')
        self.driver.get(link)
        sp = self.get_soup_sp()
        return sp

    def scrape_summary_page(self, game_id):  # Top Level
        """
        scrapes the sp from the game summary page
        """
        league_link_str = self.link_dict[self.league]
        link = f"https://www.espn.com/{league_link_str}/game/_/gameId/{game_id}"
        print(link)
        sp = self._get_sp1(link)
        return sp

    def final_status(self, sp):  # Top Level
        """
        Scraping the "Final Status" of the game (could be "Final" or include OT like "Final/OT")
        """
        final_text = sp.find('span', attrs={'class': 'game-time status-detail'})
        if final_text is None:
            return None
        else:
            return final_text.get_text() if 'Final' in final_text.get_text() else None

    def scrape_date(self, new_row, sp):  # Top Level
        """
        scrapes the date of the game
        """
        str_sp = str(sp)
        reg_comp = re.compile(
            r"Game Summary - ((January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})")
        match = re.search(reg_comp, str_sp)
        datetime_ob = datetime.datetime.strptime(match.group(1), "%B %d, %Y")
        new_row.append(datetime_ob.strftime("%Y-%m-%d"))
        return new_row

    def scrape_teams(self, new_row, sp):  # Top Level
        """
        scrapes the team names and adds to new_row
        """
        # locations = sp.find_all('span', attrs={'class': 'long-name'})
        # away_loc = locations[0].get_text()
        # home_loc = locations[1].get_text()

        # team_names = sp.find_all('span', attrs={'class': 'short-name'})
        # away_name = team_names[0].get_text()
        # home_name = team_names[1].get_text()

        # away_full = away_loc + ' ' + away_name
        # home_full = home_loc + ' ' + home_name
        # new_row.extend([home_full, away_full])
        # return new_row
        teams = sp.find_all('a', attrs={'class': 'AnchorLink truncate'})
        away = teams[0].get_text()
        home = teams[1].get_text()
        new_row.extend([home, away])
        return new_row

    def scrape_team_records(self, new_row, sp):  # Top Level
        """
        scrapes the home and away team records, adds to new_row
        """
        # records = sp.find_all('div', attrs={'class': 'record'})
        # away_record, home_record = [item.get_text() for item in records]
        records = sp.find_all('div', attrs={'class': 'Gamestrip__Record db n10 clr-gray-03'})
        away_record = records[0].get_text()
        home_record = records[1].get_text()
        new_row.extend([home_record, away_record])
        return new_row

    def scrape_network(self, new_row, sp):  # Top Level
        """
        scrapes the TV network of the game, adds to new_row
        """
        try:
            network = sp.find_all('div', attrs={'class': 'game-network'})
            network = network[0].get_text()
            network = network.replace("\n", '').replace("\t", "")
            network = network.replace("Coverage: ", "")
        except IndexError:
            network = None
        new_row.append(network)
        return new_row

    def scrape_stats_page(self, game_id):  # Top Level
        """
        Scrapes the HTML from ESPN for the given game_id
        """
        league_link_str = self.link_dict[self.league]
        link = f"https://www.espn.com/{league_link_str}/matchup?gameId={game_id}"
        print(link)
        sp = self._get_sp1(link)
        return sp

    def scrape_halves(self, new_row, sp, home):  # Top Level
        """
        scrapes the first and second half of the game if it's NCAAB, else returns None
        """
        first_half = None
        second_half = None

        if self.league == 'NCAAB':
            table_sp = sp.find('table', attrs={'id': 'linescore'})
            table_body = table_sp.find('tbody')
            away_row, home_row = table_body.find_all('tr')
            td_vals = home_row.find_all('td') if home else away_row.find_all('td')

            first_half = None
            second_half = None
            if len(td_vals) in [4, 5]:
                first_half = td_vals[1].get_text()
                second_half = td_vals[2].get_text()

        new_row.extend([first_half, second_half])
        return new_row

    def scrape_quarters_OT(self, new_row, sp, home):  # Top Level
        """
        scrapes the quarter values and OT
        - quarters only if it's not NCAAB, but OT either way
        """
        # table_sp = sp.find('table', attrs={'id': 'linescore'})
        # table_body = table_sp.find('tbody')
        # away_row, home_row = table_body.find_all('tr')
        top_banner = sp.find_all('div', attrs={'class': 'Gamestrip__Competitors relative flex'})
        score_rows = top_banner[0].find_all('tr', attrs={'class': 'Table__TR Table__TR--sm Table__even'})
        away_row, home_row = score_rows
        # !
        td_vals = home_row.find_all('td') if home else away_row.find_all('td')

        q1, q2, q3, q4, ot = None, None, None, None, None
        if len(td_vals) == 5:
            ot = td_vals[3].get_text()

        if len(td_vals) in [6, 7]:
            q1 = td_vals[1].get_text()
            q2 = td_vals[2].get_text()
            q3 = td_vals[3].get_text()
            q4 = td_vals[4].get_text()

        if len(td_vals) == 7:
            ot = td_vals[5].get_text()

        new_row.extend([q1, q2, q3, q4, ot])
        return new_row

    def scrape_final_scores(self, new_row, sp):  # Top Level
        """
        scrapes the game's final scores, adds to new_row
        """
        top_banner = sp.find_all('div', attrs={'class': 'Gamestrip__Competitors relative flex'})
        scores = top_banner[0].find_all('div', attrs={'class': 'Gamestrip__Score relative tc w-100 fw-heavy h2 clr-gray-01'})
        away_score = scores[0].get_text()
        home_score = scores[1].get_text()

        # away_score = sp.find_all('div', attrs={'class': 'score icon-font-after'})
        # away_score = away_score[0].get_text()

        # home_score = sp.find_all('div', attrs={'class': 'score icon-font-before'})
        # home_score = home_score[0].get_text()

        new_row.extend([home_score, away_score])
        return new_row

    def _clean_stat_name(self, stat_name):  # Specific Helper scrape_football_stats, scrape_basketball_stats
        """
        cleans the stat name so it's more suitable as a dataframe column name
        """
        for val in [' / ', '-', ' ']:
            stat_name = stat_name.replace(val, '_')
        for val in ['(', ')']:
            stat_name = stat_name.replace(val, '')
        stat_name = stat_name.replace('%', 'pct')
        return stat_name

    def scrape_stats(self, new_row, sp):  # Top Level
        """
        scrapes all the game stats for a game and adds them to the new_row
        """
        stat_cols = self.football_stats if self.football_league else self.basketball_stats
        # table_sp = sp.find('table', attrs={'class': 'mod-data'})
        table_sp = sp.find_all('table', attrs={'class': 'Table Table--align-right'})[1]
        table_body = table_sp.find('tbody')

        rows = table_body.find_all('tr')
        home_stat_dict = {stat: None for stat in stat_cols}
        away_stat_dict = {stat: None for stat in stat_cols}
        for row in rows:
            td_vals = row.find_all('td')
            stat = td_vals[0].get_text()
            stat = self._clean_stat_name(stat)
            away_stat_dict[stat.strip()] = td_vals[1].get_text().strip()
            home_stat_dict[stat.strip()] = td_vals[2].get_text().strip()

        for stat in stat_cols:
            new_row.append(home_stat_dict[stat])
            new_row.append(away_stat_dict[stat])

        return new_row

    def run(self):  # Run
        # * load dataframe, update columns
        df = self.load_games_df()
        df = self.add_new_df_cols(df)

        for i, row in df.iterrows():
            try:
                print(f"{i}/{len(df)}")
                # * if the game is already Final and scraped, move on
                game_is_final = 'Final' in str(row['Final_Status'])
                if game_is_final:
                    continue

                # * If we've scraped pregame data, and the game's not over, move on
                pregame_data_scraped = row['Home'] not in ['', None, np.nan]
                today_past_game_date = self.check_today_past_game_date(list(row))
                if pregame_data_scraped and (not today_past_game_date):
                    continue

                # * scraping now that we know we need to (starting row over from first 3 vals)
                game_id = row['Game_ID']
                try:
                    summary_sp = self.scrape_summary_page(game_id)
                except Exception as e:
                    print('ERROR SCRAPING SUMMARY')
                    print(e)
                    continue
                final_status = self.final_status(summary_sp)
                new_row = copy.deepcopy(list(row[:3]))

                # * always scraping pregame data again
                new_row = self.scrape_date(new_row, summary_sp)
                new_row = self.scrape_teams(new_row, summary_sp)
                new_row = self.scrape_team_records(new_row, summary_sp)
                new_row = self.scrape_network(new_row, summary_sp)
                new_row.append(final_status)

                # * scraping stats if the game's over
                today_past_game_date = self.check_today_past_game_date(new_row)
                if today_past_game_date:
                    stats_sp = self.scrape_stats_page(game_id)
                    new_row = self.scrape_halves(new_row, stats_sp, home=True)
                    new_row = self.scrape_quarters_OT(new_row, stats_sp, home=True)
                    new_row = self.scrape_halves(new_row, stats_sp, home=False)
                    new_row = self.scrape_quarters_OT(new_row, stats_sp, home=False)
                    new_row = self.scrape_final_scores(new_row, stats_sp)
                    new_row = self.scrape_stats(new_row, stats_sp)
                else:
                    num_cols = len(self.football_stats) if self.football_league else len(self.basketball_stats)
                    new_row.extend([None] * (16 + (num_cols * 2)))

                df.loc[i] = new_row
                df = df.sort_values(by=['Date'])
                df.to_csv(ROOT_PATH + f"/Data/ESPN/{self.league}/Games.csv", index=False)
            except AttributeError as e:
                print(e)
                print("ATTRIBUTE ERROR")


if __name__ == '__main__':
    # for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
    for league in ['NBA']:
        x = ESPN_Game_Scraper(league)
        self = x
        x.run()
