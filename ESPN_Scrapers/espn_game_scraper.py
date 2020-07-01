# ==============================================================================
# File: espn_game_scraper.py
# Project: Sports_Betting
# File Created: Tuesday, 7th April 2020 7:34:33 am
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 30th June 2020 5:40:47 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for scraping game data from ESPN
# ==============================================================================

import string
import re

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import get_sp1, null_if_error
from ESPN_Scrapers.espn_game import Game


class ESPN_Game_Scraper:
    """
     Scrapes data for a game on ESPN.com and returns it in a Game object from espn_game.py
    """

    def __init__(self, league: str):
        self.league = league

    @property
    def link_prefix(self):  # Property
        link_dict = {
            "NFL": 'https://www.espn.com/nfl/game/_/gameId/',
            "NCAAF": 'https://www.espn.com/college-football/game/_/gameId/',
            "NBA": 'https://www.espn.com/nba/game?gameId=',
            "NCAAB": 'https://www.espn.com/mens-college-basketball/game?gameId=',
        }
        return link_dict[self.league]

    def _sp_helper(self, game_id: str, sp=False):  # Global Helper
        """
        Scrapes html for an ESPN game if sp=False.
        If an sp is given, it's returned as it came
        """
        if not sp:
            sp = get_sp1(self.link_prefix + str(game_id))
            return sp
        else:
            return sp

    @null_if_error(2)
    def team_names(self, game_id: str, sp=False):  # Top Level
        """
        returns the home, away team names of the game
        """
        sp = self._sp_helper(game_id, sp)
        locations = sp.find_all('span', attrs={'class': 'long-name'})
        away_loc = locations[0].get_text()
        home_loc = locations[1].get_text()

        team_names = sp.find_all('span', attrs={'class': 'short-name'})
        away_name = team_names[0].get_text()
        home_name = team_names[1].get_text()

        away_full = away_loc + ' ' + away_name
        home_full = home_loc + ' ' + home_name

        return home_full, away_full

    @null_if_error(2)
    def team_records(self, game_id: str, sp=False):  # Top Level
        """
        returns the home, away team records from the game
        if the game is over, these records will include the outcome of the game
        """
        sp = self._sp_helper(game_id, sp)
        records = sp.find_all('div', attrs={'class': 'record'})
        away_record, home_record = [item.get_text() for item in records]
        return home_record, away_record

    @null_if_error(1)
    def final_status(self, game_id: str, sp=False):  # Top Level
        """
        Returns a string indicating if the game is over, includes OT if applicable
        """
        sp = self._sp_helper(game_id, sp)
        status = sp.find_all('span', attrs={'class': 'game-time status-detail'})
        status = status[0].get_text()
        return status

    def _letter_in_string(self, td_str: str):  # Helping Helper _quarter_scores_func
        for char in td_str:
            if char in string.ascii_letters:
                return True
        return False

    @staticmethod
    def _quarter_scores_func(game_id: str, sp=False):  # Specific Helper quarter_scores, half_scores
        sp = self._sp_helper(game_id, sp)
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

        assert len(home_scores) > 2  # need this so we don't return empty lists
        assert len(away_scores) > 2
        _ = [int(item) if item is not None else item for item in home_scores + away_scores]  # making sure all ints or None
        return home_scores[:-1], away_scores[:-1]  # last value is final score

    def quarter_scores(self, game_id: str, sp=False):  # Top Level
        """
        Returns the home, away scores for each quarter/half of the game, and possibly overtime
        [None] * 10 will be returned if there's an error, so it fits into the dataframe
        """
        try:
            home, away = self._quarter_scores_func(game_id, sp)
            assert len(home) == 5
            assert len(away) == 5
            return home, away
        except BaseException:
            return [[None] * 5] * 2

    def half_scores(self, game_id: str, sp=False):  # Top Level
        """
        runs quarter scores, but returns 6 None's if there's an error instead of 10
        """
        try:
            home, away = self._quarter_scores_func(game_id, sp)
            assert len(home) == 3
            assert len(away) == 3
            return home, away
        except BaseException:
            return [[None] * 3] * 2

    @null_if_error(2)
    def game_scores(self, game_id, sp=False):  # Top Level
        """
        returns the home, away final score of the game
        """
        sp = self._sp_helper(game_id, sp)
        away_score = sp.find_all('div', attrs={'class': 'score icon-font-after'})
        away_score = away_score[0].get_text()

        home_score = sp.find_all('div', attrs={'class': 'score icon-font-before'})
        home_score = home_score[0].get_text()

        return home_score, away_score

    @null_if_error(2)
    def line_over_under(self, game_id, sp=False):  # Top Level
        """
        returns the line and over under of the game from ESPN
        most games before 2018 have no data for this, so they return None
        """
        sp = self._sp_helper(game_id, sp)
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

    @null_if_error(1)
    def game_network(self, game_id, sp=False):  # Top Level
        """
        returns the TV network the game was on (e.g. ESPN, FOX, etc)
        """
        sp = self._sp_helper(game_id, sp)
        network = sp.find_all('div', attrs={'class': 'game-network'})
        network = network[0].get_text()
        network = network.replace("\n", '').replace("\t", "")
        network = network.replace("Coverage: ", "")
        return network

    @null_if_error(1)
    def game_date(self, game_id, sp=False):  # Top Level
        """
        returns the date of the game in "%B %d, %Y" format (November 12, 2019)
        """
        sp = self._sp_helper(game_id, sp)
        str_sp = str(sp)
        reg_comp = re.compile(
            r"Game Summary - ((January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4})")
        match = re.search(reg_comp, str_sp)
        return match.group(1)

    def run(self, game_id, sp=False):  # Run
        """
        Applies all the top level functions and returns a Game object with the game's data
        """
        game = Game(self.league)
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self.team_names(game_id, sp)
        game.home_record, game.away_record = self.team_records(game_id, sp)
        game.final_status = self.final_status(game_id, sp)
        game.home_score, game.away_score = self.game_scores(game_id, sp)
        game.network = self.game_network(game_id, sp)
        game.line, game.over_under = self.line_over_under(game_id, sp)
        game.game_date = self.game_date(game_id, sp)
        game.league = self.league
        if self.league == "NCAAB":
            game.home_half_scores, game.away_half_scores = self.half_scores(game_id, sp)
        else:
            game.home_qscores, game.away_qscores = self.quarter_scores(game_id, sp)
        return game


if __name__ == "__main__":
    x = ESPN_Game_Scraper("NCAAB")
    self = x
    nfl_game_id = "401128044"
    nba_game_id = "401160782"
    ncaaf_game_id = "401112199"
    ncaab_game_id = "401166198"
