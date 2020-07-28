# ==============================================================================
# File: espn_game.py
# Project: ESPN_Scrapers
# File Created: Tuesday, 30th June 2020 4:36:08 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 28th July 2020 11:12:48 am
# Modified By: Dillon Koch
# -----
#
# -----
# Representation of an ESPN Game
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Game:
    """
     Represents one game from ESPN in any league
    """

    def __init__(self, league):
        self.league = league

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
        self.league = None
        self.game_date = None

    def _get_ncaab_scores(self):  # Specific Helper to_row_list  Tested
        """
        returns a list of the 6 ncaab scores (two halves and OT for each team)
        """
        if "Final" not in str(self.final_status):
            scores = [None] * 6
        else:
            scores = self.home_half_scores + self.away_half_scores
        assert len(scores) == 6
        return scores

    def _get_non_ncaab_scores(self):  # Specific Helper to_row_list  Tested
        """
        returns a list of the 10 non-ncaab scores (4 quarters and OT for each team)
        """
        if "Final" not in str(self.final_status):
            scores = [None] * 10
        else:
            scores = self.home_qscores + self.away_qscores
        assert len(scores) == 10
        return scores

    def _test_row(self, row, league):  # QA Testing
        """
        does a quick length test on the entire row being returned
        """
        if league == "NCAAB":
            assert len(row) == 20
        elif league == "NFL":
            assert len(row) == 25
        else:
            assert len(row) == 24

    def to_row_list(self, league, season, week=None):  # Run  Tested
        """
        transforms the Game object into a list that can be easily inserted to a pd.DataFrame
        """
        row = [self.ESPN_ID, season, self.game_date, self.home_name, self.away_name,
               self.home_record, self.away_record, self.home_score, self.away_score,
               self.line, self.over_under, self.final_status, self.network]
        if league == "NCAAB":
            row += self._get_ncaab_scores()
        else:
            row += self._get_non_ncaab_scores()

        if league == "NFL":
            row.append(week)
        row.append(league)

        self._test_row(row, league)
        return row
