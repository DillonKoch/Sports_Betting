# ==============================================================================
# File: player_data.py
# Project: allison
# File Created: Tuesday, 13th December 2022 2:57:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 13th December 2022 2:57:08 pm
# Modified By: Dillon Koch
# -----
#
# -----
# class for creating feature vectors of individual players' stats
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_login import db_cursor


class Player_Stats:
    def __init__(self, league):
        self.league = league
        self.football_league = league in ['NFL', 'NCAAF']

        self.db, self.cursor = db_cursor()
        self.cursor.execute("USE sports_betting;")

        self.football_pos_nums = [('QB', 2), ('RB', 2)]
        self.basketball_pos_nums = []
        self.pos_nums = self.football_pos_nums if self.football_league else self.basketball_pos_nums

    def get_player_ids(self, team, date, pos, num):  # Top Level
        # * if game has been played, use player ID's from THAT game's stats
        sql = f"""SELECT * FROM ESPN_Player_Stats_{self.league}
                 WHERE Date = '{date}' AND Team = '{team}';"""
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        print('here')

        # if game is today or in future, use team roster and recent stats to find ID's

    def one_player_stats(self, player_id, date, past_games, avg_stats):  # Top Level
        pass

    def run(self, team, date, past_games, avg_stats):  # Run
        # if game is played, grab the stats of those who played
        # if game is not yet played, locate players who will play via rosters
        # incorporate injury status
        # * goal output is a df of stats for all players on the team (ML-ready, raw or avgs)
        output = []

        for pos, num in self.pos_nums:
            # * ID's of top 2 QB's, top 4 WR's, etc
            player_ids = self.get_player_ids(team, date, pos, num)
            for player_id in player_ids:
                # * add stats to the output for the player
                output += self.one_player_stats(player_id, date, past_games, avg_stats)

        return output


if __name__ == '__main__':
    league = 'NFL'
    x = Player_Stats(league)
    self = x
    data = x.run('Minnesota Vikings', '20070909', 5, True)
    print(data)
