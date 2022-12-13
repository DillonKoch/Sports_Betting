# ==============================================================================
# File: espn_game.py
# Project: allison
# File Created: Saturday, 26th November 2022 2:32:29 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 26th November 2022 2:32:29 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping game data from ESPN
# ==============================================================================


import datetime
import re
import sys
import time
import urllib.request
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_login import db_cursor


class Scrape_ESPN_Game:
    def __init__(self, league):
        self.league = league
        self.db, self.cursor = db_cursor()
        self.link_dict = {"NFL": "nfl", "NBA": "nba", "NCAAF": "college-football", "NCAAB": "mens-college-basketball"}
        self.football_league = league in ['NFL', 'NCAAF']

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

        self.football_cols = ['Game_ID', 'Season', 'Week',
                              'Date', 'Home', 'Away', 'Home_Record', 'Away_Record',
                              'Network', 'Final_Status', 'H1H', 'H2H', 'H1Q', 'H2Q',
                              'H3Q', 'H4Q', 'HOT', 'A1H', 'A2H', 'A1Q', 'A2Q', 'A3Q',
                              'A4Q', 'AOT', 'Home_Final', 'Away_Final', 'Home_1st_Downs',
                              'Away_1st_Downs', 'Home_Passing_1st_Downs', 'Away_Passing_1st_Downs',
                              'Home_Rushing_1st_Downs', 'Away_Rushing_1st_Downs',
                              'Home_1st_Downs_From_Penalties', 'Away_1st_Downs_From_Penalties',
                              'Home_3rd_Down_Efficiency', 'Away_3rd_Down_Efficiency',
                              'Home_4th_Down_Efficiency', 'Away_4th_Down_Efficiency',
                              'Home_Total_Plays', 'Away_Total_Plays', 'Home_Total_Yards',
                              'Away_Total_Yards', 'Home_Total_Drives', 'Away_Total_Drives',
                              'Home_Yards_Per_Play', 'Away_Yards_Per_Play', 'Home_Passing',
                              'Away_Passing', 'Home_Comp_Att', 'Away_Comp_Att',
                              'Home_Yards_Per_Pass', 'Away_Yards_Per_Pass',
                              'Home_Interceptions_Thrown', 'Away_Interceptions_Thrown',
                              'Home_Sacks_Yards_Lost', 'Away_Sacks_Yards_Lost',
                              'Home_Rushing', 'Away_Rushing', 'Home_Rushing_Attempts',
                              'Away_Rushing_Attempts', 'Home_Yards_Per_Rush',
                              'Away_Yards_Per_Rush', 'Home_Red_Zone_Made_Att',
                              'Away_Red_Zone_Made_Att', 'Home_Penalties', 'Away_Penalties',
                              'Home_Turnovers', 'Away_Turnovers', 'Home_Fumbles_Lost',
                              'Away_Fumbles_Lost', 'Home_Defensive_Special_Teams_TDs',
                              'Away_Defensive_Special_Teams_TDs', 'Home_Possession', 'Away_Possession']

        self.basketball_cols = ['Game_ID', 'Season', 'Week',
                                'Date', 'Home', 'Away', 'Home_Record', 'Away_Record',
                                'Network', 'Final_Status', 'H1H', 'H2H', 'H1Q', 'H2Q',
                                'H3Q', 'H4Q', 'HOT', 'A1H', 'A2H', 'A1Q', 'A2Q', 'A3Q',
                                'A4Q', 'AOT', 'Home_Final', 'Away_Final', 'Home_FG', 'Away_FG',
                                'Home_Field_Goal_Pct', 'Away_Field_Goal_Pct', 'Home_3PT', 'Away_3PT',
                                'Home_Three_Point_Pct', 'Away_Three_Point_Pct', 'Home_FT', 'Away_FT',
                                'Home_Free_Throw_Pct', 'Away_Free_Throw_Pct', 'Home_Rebounds',
                                'Away_Rebounds', 'Home_Offensive_Rebounds', 'Away_Offensive_Rebounds',
                                'Home_Defensive_Rebounds', 'Away_Defensive_Rebounds', 'Home_Assists',
                                'Away_Assists', 'Home_Steals', 'Away_Steals', 'Home_Blocks', 'Away_Blocks',
                                'Home_Total_Turnovers', 'Away_Total_Turnovers', 'Home_Points_Off_Turnovers',
                                'Away_Points_Off_Turnovers', 'Home_Fast_Break_Points', 'Away_Fast_Break_Points',
                                'Home_Points_In_Paint', 'Away_Points_In_Paint', 'Home_Fouls', 'Away_Fouls',
                                'Home_Technical_Fouls', 'Away_Technical_Fouls', 'Home_Flagrant_Fouls',
                                'Away_Flagrant_Fouls', 'Home_Largest_Lead', 'Away_Largest_Lead']
        self.cols = self.football_cols if self.football_league else self.basketball_cols

    def _get_sp1(self, link):  # Global Helper
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        time.sleep(5)
        return sp

    def query_unscraped_games(self):  # Top Level
        """
        querying data from ESPN_Games_{league} for unscraped games
        - we know it's unscraped if home team is Kennedy
        - also filtering out games that occur in the future
        """
        self.cursor.execute("USE sports_betting;")
        sql = f"SELECT * FROM ESPN_Games_{self.league} WHERE Home = 'Kennedy Cougars'"
        self.cursor.execute(sql)
        games = self.cursor.fetchall()
        games = [list(game) for game in games if game[3] < datetime.date.today()]  # list so I can reassign values
        return games

    def scrape_summary_sp(self, game_id):  # Top Level
        """
        scrapes the sp from the game summary page
        """
        league_link_str = self.link_dict[self.league]
        link = f"https://www.espn.com/{league_link_str}/game/_/gameId/{game_id}"
        sp = self._get_sp1(link)
        return sp

    def final_status(self, sp):  # Top Level
        """
        Scraping the "Final Status" of the game (could be "Final" or include OT like "Final/OT")
        """
        if self.league in ['NBA', 'NCAAB']:
            return 'Final'

        final_text = sp.find('span', attrs={'class': 'game-time status-detail'}) or sp.find('div', attrs={'class': 'ScoreCell__Time Gamestrip__Time h9 clr-gray-01'})
        if final_text is None:
            return None
        else:
            return final_text.get_text() if 'Final' in final_text.get_text() else None

    def scrape_date(self, game, sp):  # Top Level
        """
        scrapes the date of the game
        """
        str_sp = str(sp)
        reg_comp = re.compile(
            r"Game Summary - ((January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})")
        match = re.search(reg_comp, str_sp)
        datetime_ob = datetime.datetime.strptime(match.group(1), "%B %d, %Y")
        game[3] = datetime_ob.strftime("%Y-%m-%d")
        return game

    def scrape_teams(self, game, sp):  # Top Level
        """
        scrapes the team names and adds to new_row
        """
        if self.football_league:
            teams = sp.find_all('a', attrs={'class': 'team-name'})
            if not teams:
                teams = sp.find_all('div', attrs={'class': 'ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db'})
                away = teams[0].get_text()
                home = teams[1].get_text()
            else:
                away_long = teams[0].find('span', attrs={'class': 'long-name'}).get_text()
                away_short = teams[0].find('span', attrs={'class': 'short-name'}).get_text()
                away = away_long + ' ' + away_short
                home_long = teams[1].find('span', attrs={'class': 'long-name'}).get_text()
                home_short = teams[1].find('span', attrs={'class': 'short-name'}).get_text()
                home = home_long + ' ' + home_short
        else:
            home = sp.find_all('div', attrs={'class': 'ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db'})[1].get_text()
            away = sp.find_all('div', attrs={'class': 'ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db'})[0].get_text()
        game[4] = home.replace("'", "")
        game[5] = away.replace("'", "")
        return game

    def scrape_team_records(self, game, sp):  # Top Level
        """
        scrapes the home and away team records, adds to game
        """
        records = sp.find_all('div', attrs={'class': 'record'}) or sp.find_all('div', attrs={'class': 'Gamestrip__Record db n10 clr-gray-03'})
        away_record = records[0].get_text()
        home_record = records[1].get_text()
        game[6] = home_record
        game[7] = away_record
        return game

    def scrape_network(self, game, sp):  # Top Level
        """
        scrapes the TV network of the game, adds to game
        """
        try:
            network = sp.find_all('div', attrs={'class': 'game-network'}) or sp.find_all('div', attrs={'class': 'n8 GameInfo__Meta'})[0].find_all('span')[1:]
            network = network[0].get_text()
            network = network.replace("\n", '').replace("\t", "")
            network = network.replace("Coverage: ", "")
        except IndexError:
            network = None
        game[8] = network
        return game

    def scrape_stats_sp(self, game_id):  # Top Level
        """
        Scrapes the HTML from ESPN for the given game_id
        """
        league_link_str = self.link_dict[self.league]
        link = f"https://www.espn.com/{league_link_str}/matchup?gameId={game_id}"
        sp = self._get_sp1(link)
        return sp

    def scrape_halves(self, game, sp, home):  # Top Level
        """
        scrapes the first and second half of the game if it's NCAAB, else returns None
        """
        first_half = None
        second_half = None

        # * scraping halves if the league is NCAAB
        if self.league == 'NCAAB':
            table_sp = sp.find('div', attrs={'class': 'Table__Scroller'})
            table_body = table_sp.find('tbody')
            away_row, home_row = table_body.find_all('tr')
            td_vals = home_row.find_all('td') if home else away_row.find_all('td')

            first_half = None
            second_half = None
            if len(td_vals) in [4, 5]:
                first_half = td_vals[1].get_text()
                second_half = td_vals[2].get_text()

        # * updating game based on home/away team
        if home:
            game[10] = first_half
            game[11] = second_half
        else:
            game[17] = first_half
            game[18] = second_half

        return game

    def scrape_quarters_ot(self, game, sp, home):  # Top Level
        """
        scrapes the quarter values and OT
        - quarters only if it's not NCAAB, but OT either way
        """
        # scores_sp = sp.find_all('table', attrs={'id': 'linescore'})[0] if self.football_league else sp.find('div', attrs={'class': 'Table__Scroller'})
        scores_sp = sp.find('div', attrs={'class': 'Table__Scroller'})
        body = scores_sp.find_all('tbody')[0]
        rows = body.find_all('tr')
        away_row, home_row = rows
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

        if home:
            game[12:17] = [q1, q2, q3, q4, ot]
        else:
            game[19:24] = [q1, q2, q3, q4, ot]
        return game

    def scrape_final_scores(self, game, sp):  # Top Level
        """
        scrapes the game's final scores, adds to new_row
        """
        # scores_sp = sp.find_all('table', attrs={'id': 'linescore'})[0] if self.football_league else sp.find('div', attrs={'class': 'Table__Scroller'})
        scores_sp = sp.find('div', attrs={'class': 'Table__Scroller'})
        body = scores_sp.find_all('tbody')[0]
        rows = body.find_all('tr')
        away_row, home_row = rows
        # away_score = away_row.find_all('td', attrs={'class': 'final-score'})[0].get_text() if self.football_league else away_row.find_all('td')[-1].get_text()
        # home_score = home_row.find_all('td', attrs={'class': 'final-score'})[0].get_text() if self.football_league else home_row.find_all('td')[-1].get_text()
        away_score = away_row.find_all('td')[-1].get_text()
        home_score = home_row.find_all('td')[-1].get_text()
        game[24] = home_score
        game[25] = away_score
        return game

    # def _body_to_stats(self, body, stat):  # Helping Helper _scrape_football, _scrape_basketball
    #     try:
    #         tr = body.find_all('tr', attrs={'data-stat-attr': stat})[0]
    #         tds = tr.find_all('td')
    #         away = tds[1].get_text().strip()
    #         home = tds[2].get_text().strip()
    #         return home, away
    #     except Exception as e:
    #         print(e)
    #         print(f"Invalid values for stat {stat}")
    #         return None, None

    def _body_to_stats(self, body, stat):
        try:
            trs = body.find_all('tr')
            for tr in trs:
                data = tr.find_all('td')
                data = [item.get_text() for item in data]
                if data and stat == data[0]:
                    return data[1], data[2]
            raise ValueError(f"didnt find stat {stat}")

        except Exception as e:
            print(e)
            print(f"Invalid values for stat {stat}")
            return None, None

    def _scrape_football(self, game, body):  # Specific Helper scrape_stats
        game[26:28] = self._body_to_stats(body, "1st Downs")
        game[28:30] = self._body_to_stats(body, "Passing 1st downs")
        game[30:32] = self._body_to_stats(body, "Rushing 1st downs")
        game[32:34] = self._body_to_stats(body, "1st downs from penalties")
        game[34:36] = self._body_to_stats(body, "3rd down efficiency")
        game[36:38] = self._body_to_stats(body, "4th down efficiency")
        game[38:40] = self._body_to_stats(body, "Total Plays")
        game[40:42] = self._body_to_stats(body, "Total Yards")
        game[42:44] = self._body_to_stats(body, "Total Drives")
        game[44:46] = self._body_to_stats(body, "Yards per Play")
        game[46:48] = self._body_to_stats(body, "Passing")
        game[48:50] = self._body_to_stats(body, "Comp-Att")
        game[50:52] = self._body_to_stats(body, "Yards per pass")
        game[52:54] = self._body_to_stats(body, "Interceptions thrown")
        game[54:56] = self._body_to_stats(body, "Sacks-Yards Lost")
        game[56:58] = self._body_to_stats(body, "Rushing")
        game[58:60] = self._body_to_stats(body, "Rushing Attempts")
        game[60:62] = self._body_to_stats(body, "Yards per rush")
        game[62:64] = self._body_to_stats(body, "Red Zone (Made-Att)")
        game[64:66] = self._body_to_stats(body, "Penalties")
        game[66:68] = self._body_to_stats(body, "Turnovers")
        game[68:70] = self._body_to_stats(body, "Fumbles lost")
        game[70:72] = self._body_to_stats(body, "Defensive / Special Teams TDs")
        game[72:74] = self._body_to_stats(body, "Possession")
        return game

    def _scrape_basketball(self, game, body):  # Specific Helper scrape_stats
        rows = body.find_all('tr')
        start = 26
        for row in rows:
            _, away, home = row.find_all('td')
            away = away.get_text()
            home = home.get_text()
            game[start:start + 2] = [home, away]
            start += 2
        return game

    def scrape_stats(self, game, sp):  # Top Level
        try:
            # idx = 0 if self.football_league else 1
            # table = sp.find_all('table', attrs={'class': ['mod-data', 'Table Table--align-right']})[idx]
            table = sp.find('section', attrs={'class': 'Card TeamStatsTable'})
            body = table.find('tbody')
            if self.league in ['NFL', 'NCAAF']:
                game = self._scrape_football(game, body)
            else:
                game = self._scrape_basketball(game, body)
            return game
        except Exception as e:
            print(e)
            print('error scraping stats')
            print(game[0])
            return game

    def game_to_db(self, game):  # Top Level
        """
        inserting a scraped game into the SQL database
        """
        self.cursor.execute("USE sports_betting;")

        table = f"ESPN_Games_{self.league}"

        cv_strs = []
        game = [item if item is not None else "NULL" for item in game]
        for col, val in zip(self.cols, game):
            cv_strs.append(f"{col} = '{val}'")
        updates = ", ".join(cv_strs)

        sql = f"UPDATE {table} SET {updates} WHERE Game_ID = {game[0]};"
        sql = sql.replace("'NULL'", "NULL")
        self.cursor.execute(sql)
        self.db.commit()

    def run(self):  # Run
        unscraped_games = self.query_unscraped_games()
        for game in tqdm(unscraped_games[11:]):
            # try:
            game_id = game[0]

            # ! SUMMARY INFORMATION
            summary_sp = self.scrape_summary_sp(game_id)
            final_status = self.final_status(summary_sp)

            game = self.scrape_date(game, summary_sp)
            if datetime.datetime.strptime(game[3], "%Y-%m-%d") >= datetime.datetime.today():
                continue

            game = self.scrape_teams(game, summary_sp)
            game = self.scrape_team_records(game, summary_sp)
            game = self.scrape_network(game, summary_sp)
            game[9] = final_status

            # ! STATS INFORMATION
            stats_sp = self.scrape_stats_sp(game_id)
            game = self.scrape_halves(game, stats_sp, home=True)
            game = self.scrape_quarters_ot(game, stats_sp, home=True)
            game = self.scrape_halves(game, stats_sp, home=False)
            game = self.scrape_quarters_ot(game, stats_sp, home=False)
            game = self.scrape_final_scores(game, stats_sp)
            game = self.scrape_stats(game, stats_sp)
            self.game_to_db(game)
            # except BaseException as e:
            #     print(e)
            #     print(self.league, game_id)


if __name__ == '__main__':
    for league in ['NFL']:  # ! FIX FOR NCAAB
        x = Scrape_ESPN_Game(league)
        self = x
        x.run()
