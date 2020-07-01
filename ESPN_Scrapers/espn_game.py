# ==============================================================================
# File: espn_game.py
# Project: ESPN_Scrapers
# File Created: Tuesday, 30th June 2020 4:36:08 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 30th June 2020 5:18:37 pm
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

    def _get_ncaab_scores(self):  # Specific Helper to_row_list
        """
        returns a list of ncaab half scores and overtime, always length 6 (even NIT 4-quarter games)
        [H1H, H2H, HOT, A1H, A2H, AOT]
        """
        scores = []
        for score_list in [self.home_half_scores, self.away_half_scores]:
            num_scores = len(score_list)
            try:
                if num_scores == 4:  # NIT 4-quarter game
                    first_half = int(score_list[0]) + int(score_list[1])
                    second_half = int(score_list[2]) + int(score_list[3])
                    scores += [first_half, second_half, None]
                elif num_scores == 5:  # NIT 4-quarter ncaab game, went into overtime
                    first_half = int(score_list[0]) + int(score_list[1])
                    second_half = int(score_list[2]) + int(score_list[3])
                    scores += [first_half, second_half, score_list[4]]
                elif num_scores == 2:  # normal ncaab game
                    scores += score_list
                    scores.append(None)
                elif num_scores == 3:  # normal ncaab game, went into overtime
                    scores += score_list

            except Exception as e:
                print(e)
                scores = [None] * 6

        scores = [str(item) if item is not None else item for item in scores]
        assert len(scores) == 6
        return scores

    def _get_non_ncaab_scores(self):  # Specific Helper to_row_list
        scores = []
        try:
            for score_list in [self.home_qscores, self.away_qscores]:
                scores += score_list
                if len(score_list) == 4:
                    scores.append(None)
        except Exception as e:
            print(e)
            scores = [None] * 10
        return scores

    def _test_row(self, row, league):  # QA Testing
        if league == "NCAAB":
            assert len(row) == 20
        elif league == "NFL":
            assert len(row) == 25
        else:
            assert len(row) == 24

    def to_row_list(self, league, season, week=None):  # Run
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

        self._test_row(row)
        return row
