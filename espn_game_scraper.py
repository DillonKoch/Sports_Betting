# ==============================================================================
# File: espn_game_scraper.py
# Project: Sports_Betting
# File Created: Tuesday, 7th April 2020 7:34:33 am
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 16th April 2020 7:57:44 pm
# Modified By: Dillon Koch
# -----
#
#
# -----
# File for scraping game data from ESPN
# ==============================================================================

import string
import re

from Utility import get_sp1, null_if_error


class Game:
    def __init__(self):
        self.ESPN_ID = None
        self.home_name = None
        self.away_name = None
        self.home_record = None
        self.away_record = None
        self.final_status = None
        self.home_qscores = None
        self.away_qscores = None
        self.home_score = None
        self.away_score = None
        self.home_half_scores = None
        self.away_half_scores = None
        self.network = None
        self.line = None
        self.over_under = None


class ESPN_Game_Scraper:
    def __init__(self):
        self.link_dict = {
            "NFL": 'https://www.espn.com/nfl/game/_/gameId/',
            "NCAAF": 'https://www.espn.com/college-football/game/_/gameId/',
            "MLB": 'https://www.espn.com/mlb/game?gameId=',
            "NBA": 'https://www.espn.com/nba/game?gameId=',
            "NCAAB": 'https://www.espn.com/mens-college-basketball/game?gameId=',
            "NHL": 'https://www.espn.com/nhl/game/_/gameId/'
        }

    def _sp_helper(self, league, game_id, sp=False):
        if not sp:
            sp = get_sp1(self.link_dict[league] + str(game_id))
            return sp
        else:
            return sp

    def _letter_in_string(self, td_str):
        for char in td_str:
            if char in string.ascii_letters:
                return True
        return False

    # ########### GAME INFO FUNCTIONS ####################

    @null_if_error
    def _team_names(self, league, game_id, sp=False):
        sp = self._sp_helper(league, game_id, sp)
        locations = sp.find_all('span', attrs={'class': 'long-name'})
        away_loc = locations[0].get_text()
        home_loc = locations[1].get_text()

        team_names = sp.find_all('span', attrs={'class': 'short-name'})
        away_name = team_names[0].get_text()
        home_name = team_names[1].get_text()

        away_full = away_loc + ' ' + away_name
        home_full = home_loc + ' ' + home_name

        return home_full, away_full

    @null_if_error
    def _team_records(self, league, game_id, sp=False):
        sp = self._sp_helper(league, game_id, sp)
        records = sp.find_all('div', attrs={'class': 'record'})
        away_record, home_record = [item.get_text() for item in records]
        return home_record, away_record

    @null_if_error
    def _final_status(self, league, game_id, sp=False):
        sp = self._sp_helper(league, game_id, sp)
        status = sp.find_all('span', attrs={'class': 'game-time status-detail'})
        status = status[0].get_text()
        return status

    @null_if_error
    def _quarter_scores(self, league, game_id, sp=False):
        sp = self._sp_helper(league, game_id, sp)
        td_htmls = [item.get_text() for item in sp.find_all('td')]

        away_scores = []
        home_scores = []
        updating_home = False
        for td in td_htmls[1:]:
            if self._letter_in_string(td):
                if updating_home:
                    break
                else:
                    updating_home = True
                    continue
            if updating_home:
                home_scores.append(td)
            else:
                away_scores.append(td)

        return home_scores[:-1], away_scores[:-1]

    @null_if_error
    def _game_scores(self, league, game_id, sp=False):
        sp = self._sp_helper(league, game_id, sp)
        away_score = sp.find_all('div', attrs={'class': 'score icon-font-after'})
        away_score = away_score[0].get_text()

        home_score = sp.find_all('div', attrs={'class': 'score icon-font-before'})
        home_score = home_score[0].get_text()

        return home_score, away_score

    @null_if_error
    def _line_ou(self, league, game_id, sp=False):
        sp = self._sp_helper(league, game_id, sp)
        li_htmls = [item.get_text() for item in sp.find_all('li')]

        line_comp = re.compile(r"^Line: (.+)$")
        ou_comp = re.compile(r"\s+Over/Under: (\d+)\s+$")
        line = None
        over_under = None

        for html in li_htmls:
            line_match = re.match(line_comp, html)
            ou_match = re.match(ou_comp, html)
            if line_match:
                line = line_match.group(1)
            elif ou_match:
                over_under = ou_match.group(1)

        return line, over_under

    @null_if_error
    def _game_network(self, league, game_id, sp=False):
        sp = self._sp_helper(league, game_id, sp)
        network = sp.find_all('div', attrs={'class': 'game-network'})
        network = network[0].get_text()
        network = network.replace("\n", '').replace("\t", "")
        network = network.replace("Coverage: ", "")
        return network

    # ############## LEAGUE SPECIFIC FUNCTIONS ################

    def all_nfl_info(self, game_id, sp=False):
        sp = self._sp_helper("NFL", game_id, sp)
        game = Game()
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self._team_names("NFL", game_id, sp)
        game.home_record, game.away_record = self._team_records("NFL", game_id, sp)
        game.final_status = self._final_status("NFL", game_id, sp)
        game.home_qscores, game.away_qscores = self._quarter_scores("NFL", game_id, sp)
        game.home_score, game.away_score = self._game_scores("NFL", game_id, sp)
        game.network = self._game_network("NFL", game_id, sp)
        game.line, game.over_under = self._line_ou("NFL", game_id, sp)
        return game

    def all_nba_info(self, game_id, sp=False):
        sp = self._sp_helper("NBA", game_id, sp)
        game = Game()
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self._team_names("NBA", game_id, sp)
        game.home_record, game.away_record = self._team_records("NBA", game_id, sp)
        game.final_status = self._final_status("NBA", game_id, sp)
        game.home_qscores, game.away_qscores = self._quarter_scores("NBA", game_id, sp)
        game.home_score, game.away_score = self._game_scores("NBA", game_id, sp)
        game.network = self._game_network("NBA", game_id, sp)
        game.line, game.over_under = self._line_ou("NBA", game_id, sp)
        return game

    def all_ncaaf_info(self, game_id, sp=False):
        sp = self._sp_helper("NCAAF", game_id, sp)
        game = Game()
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self._team_names("NCAAF", game_id, sp)
        game.home_record, game.away_record = self._team_records("NCAAF", game_id, sp)
        game.final_status = self._final_status("NCAAF", game_id, sp)
        game.home_qscores, game.away_qscores = self._quarter_scores("NCAAF", game_id, sp)
        game.home_score, game.away_score = self._game_scores("NCAAF", game_id, sp)
        game.network = self._game_network("NCAAF", game_id, sp)
        game.line, game.over_under = self._line_ou("NCAAF", game_id, sp)
        return game

    def all_ncaab_info(self, game_id, sp=False):
        sp = self._sp_helper("NCAAB", game_id, sp)
        game = Game()
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self._team_names("NCAAB", game_id, sp)
        game.home_record, game.away_record = self._team_records("NCAAB", game_id, sp)
        game.final_status = self._final_status("NCAAB", game_id, sp)
        game.home_half_scores, game.away_half_scores = self._quarter_scores("NCAAB", game_id, sp)
        game.home_score, game.away_score = self._game_scores("NCAAB", game_id, sp)
        game.network = self._game_network("NCAAB", game_id, sp)
        game.line, game.over_under = self._line_ou("NCAAB", game_id, sp)
        return game

    # ########### NHL ###############

    def _hockey_team_names(self, game_id, sp=False):
        sp = self._sp_helper("NHL", game_id, sp)

        team_names = sp.find_all('div', attrs={'class': "ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db"})
        away_full, home_full = [item.get_text() for item in team_names]

        return home_full, away_full

    def _hockey_records(self, game_id, sp=False):
        sp = self._sp_helper("NHL", game_id, sp)

        records = sp.find_all('div', attrs={'class': 'Gamestrip__Record db n10 clr-gray-03'})
        away_record, home_record = [item.get_text() for item in records]

        return home_record, away_record

    def hockey_score(self, game_id, sp=False):
        sp = self._sp_helper("NHL", game_id, sp)

        scores = sp.find_all('div', attrs={'class': 'Gamestrip__Score relative tc w-100 fw-heavy h2 clr-gray-01'})
        away_score, home_score = [item.get_text() for item in scores]

        return home_score, away_score

    def all_hockey_info(self, game_id):
        link = self.link_dict["NHL"] + str(game_id)
        sp = get_sp1(link)

        home_team, away_team = self._hockey_team_names(game_id, sp)
        home_record, away_record = self._hockey_records(game_id, sp)
        home_score, away_score = self.hockey_score(game_id, sp)


if __name__ == "__main__":
    e = ESPN_Game_Scraper()
#     nflh, nfla = e._nfl_team_names("401128044")
#     nflhr, nflar = e._nfl_records("401128044")
#     status = e._nfl_final_status("401128044")
#     home_score, away_score = e.nfl_scores("401128044")
