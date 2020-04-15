# ==============================================================================
# File: espn_game_scraper.py
# Project: Sports_Betting
# File Created: Tuesday, 7th April 2020 7:34:33 am
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 7th April 2020 7:41:07 am
# Modified By: Dillon Koch
# -----
#
#
# -----
# File for scraping game data from ESPN
# ==============================================================================

import string

from Utility import get_sp1


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

        # ########### NFL ############

    def _nfl_team_names(self, game_id, sp=False):
        sp = self._sp_helper("NFL", game_id, sp)

        locations = sp.find_all('span', attrs={'class': 'long-name'})
        away_loc, home_loc = [item.get_text() for item in locations]

        team_names = sp.find_all('span', attrs={'class': 'short-name'})
        away_name, home_name = [item.get_text() for item in team_names]

        away_full = away_loc + ' ' + away_name
        home_full = home_loc + ' ' + home_name

        return home_full, away_full

    def _nfl_records(self, game_id, sp=False):
        sp = self._sp_helper("NFL", game_id, sp)

        records = sp.find_all('div', attrs={'class': 'record'})
        away_record, home_record = [item.get_text() for item in records]

        return home_record, away_record

    def _nfl_final_status(self, game_id, sp=False):
        sp = self._sp_helper("NFL", game_id, sp)

        status = sp.find_all('span', attrs={'class': 'game-time status-detail'})

        status = status[0].get_text()
        return status

    def _nfl_quarter_scores(self, game_id, sp=False):
        sp = self._sp_helper("NFL", game_id, sp)

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

    def nfl_scores(self, game_id, sp=False):
        sp = self._sp_helper("NFL", game_id, sp)

        away_score = sp.find_all('div', attrs={'class': 'score icon-font-after'})
        away_score = away_score[0].get_text()

        home_score = sp.find_all('div', attrs={'class': 'score icon-font-before'})
        home_score = home_score[0].get_text()

        return home_score, away_score

    def all_nfl_info(self, game_id, sp=False):
        sp = self._sp_helper("NFL", game_id, sp)
        game = Game()
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self._nfl_team_names(game_id, sp)
        game.home_record, game.away_record = self._nfl_records(game_id, sp)
        game.final_status = self._nfl_final_status(game_id, sp)
        game.home_qscores, game.away_qscores = self._nfl_quarter_scores(game_id, sp)
        game.home_score, game.away_score = self.nfl_scores(game_id, sp)
        return game

    # ############## NBA ################

    def _nba_team_names(self, game_id, sp=False):
        sp = self._sp_helper("NBA", game_id, sp)

        locations = sp.find_all('span', attrs={'class': 'long-name'})
        away_loc = locations[0].get_text()
        home_loc = locations[1].get_text()

        team_names = sp.find_all('span', attrs={'class': 'short-name'})
        away_name = team_names[0].get_text()
        home_name = team_names[1].get_text()

        home_full = home_loc + ' ' + home_name
        away_full = away_loc + ' ' + away_name

        return home_full, away_full

    def _nba_records(self, game_id, sp=False):
        sp = self._sp_helper("NBA", game_id, sp)

        records = sp.find_all('div', attrs={'class': 'record'})
        away_record, home_record = [item.get_text() for item in records]

        return home_record, away_record

    def _nba_final_status(self, game_id, sp=False):
        sp = self._sp_helper("NBA", game_id, sp)

        status = sp.find_all("span", attrs={'class': 'game-time status-detail'})
        status = status[0].get_text()

        return status

    def _nba_quarter_scores(self, game_id, sp=False):
        sp = self._sp_helper("NBA", game_id, sp)

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

    def nba_scores(self, game_id, sp=False):
        sp = self._sp_helper("NBA", game_id, sp)

        away_score = sp.find_all('div', attrs={'class': 'score icon-font-after'})
        away_score = away_score[0].get_text()

        home_score = sp.find_all('div', attrs={'class': 'score icon-font-before'})
        home_score = home_score[0].get_text()

        return home_score, away_score

    def all_nba_info(self, game_id, sp=False):
        sp = self._sp_helper("NBA", game_id, sp)
        game = Game()
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self._nba_team_names(game_id, sp)
        game.home_record, game.away_record = self._nba_records(game_id, sp)
        game.final_status = self._nba_final_status(game_id, sp)
        game.home_qscores, game.away_qscores = self._nba_quarter_scores(game_id, sp)
        game.home_score, game.away_score = self.nba_scores(game_id, sp)
        return game

    # ############ NCAAF ############

    def _ncaaf_team_names(self, game_id, sp=False):
        sp = self._sp_helper("NCAAF", game_id, sp)

        locations = sp.find_all('span', attrs={'class': 'long-name'})
        away_loc, home_loc = [item.get_text() for item in locations]

        team_names = sp.find_all('span', attrs={'class': 'short-name'})
        away_name, home_name = [item.get_text() for item in team_names]

        home_full = home_loc + ' ' + home_name
        away_full = away_loc + ' ' + away_name

        return home_full, away_full

    def _ncaaf_records(self, game_id, sp=False):
        sp = self._sp_helper("NCAAF", game_id, sp)

        records = sp.find_all('div', attrs={'class': 'record'})
        away_record, home_record = [item.get_text() for item in records]

        return home_record, away_record

    def _ncaaf_final_status(self, game_id, sp=False):
        sp = self._sp_helper("NCAAF", game_id, sp)

        status = sp.find_all('span', attrs={'class': 'game-time status-detail'})
        status = status[0].get_text()

        return status

    def _ncaaf_quarter_scores(self, game_id, sp=False):
        # TODO forgot this one, get to it next time :)
        sp = self._sp_helper("NCAAF", game_id, sp)

        td_htmls = [item.get_text() for item in sp.find_all('td')]
        away_qscores = td_htmls[1:5]
        home_qscores = td_htmls[7:11]

        return home_qscores, away_qscores

    def ncaaf_scores(self, game_id, sp=False):
        sp = self._sp_helper("NCAAF", game_id, sp)

        away_score = sp.find_all('div', attrs={'class': 'score icon-font-after'})
        away_score = away_score[0].get_text()

        home_score = sp.find_all('div', attrs={'class': 'score icon-font-before'})
        home_score = home_score[0].get_text()

        return home_score, away_score

    def all_ncaaf_info(self, game_id, sp=False):
        sp = self._sp_helper("NCAAF", game_id, sp)
        game = Game()
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self._ncaaf_team_names(game_id, sp)
        game.home_record, game.away_record = self._ncaaf_records(game_id, sp)
        game.final_status = self._ncaaf_final_status(game_id, sp)
        game.home_qscores, game.away_qscores = self._ncaaf_quarter_scores(game_id, sp)
        game.home_score, game.away_score = self.ncaaf_scores(game_id, sp)
        return game

    # ########### NCAAB ##############

    def _ncaab_team_names(self, game_id, sp=False):
        sp = self._sp_helper("NCAAB", game_id, sp)

        locations = sp.find_all('span', attrs={'class': 'long-name'})
        locations_text = [item.get_text() for item in locations]
        away_loc = locations_text[0]
        home_loc = locations_text[1]

        team_names = sp.find_all('span', attrs={'class': 'short-name'})
        team_names_text = [item.get_text() for item in team_names]
        away_name = team_names_text[0]
        home_name = team_names_text[1]

        home_full = home_loc + ' ' + home_name
        away_full = away_loc + ' ' + away_name
        return home_full, away_full

    def _ncaab_records(self, game_id, sp=False):
        sp = self._sp_helper("NCAAB", game_id, sp)

        records = sp.find_all('div', attrs={'class': 'record'})
        away_record, home_record = [item.get_text() for item in records]

        return home_record, away_record

    def _ncaab_final_status(self, game_id, sp=False):
        sp = self._sp_helper("NCAAB", game_id, sp)

        status = sp.find_all('span', attrs={'class': 'game-time status-detail'})
        status = status[0].get_text()

        return status

    def _ncaab_half_scores(self, game_id, sp=False):
        sp = self._sp_helper("NCAAB", game_id, sp)

        td_htmls = [item.get_text() for item in sp.find_all('td')]
        away_half_scores = td_htmls[1:3]
        home_half_scores = td_htmls[5:7]

        return home_half_scores, away_half_scores

    def ncaab_scores(self, game_id, sp=False):
        sp = self._sp_helper("NCAAB", game_id, sp)

        away_score = sp.find_all('div', attrs={'class': 'score icon-font-after'})
        away_score = away_score[0].get_text()

        home_score = sp.find_all('div', attrs={'class': 'score icon-font-before'})
        home_score = home_score[0].get_text()

        return home_score, away_score

    def all_ncaab_info(self, game_id, sp=False):
        sp = self._sp_helper("NCAAB", game_id, sp)
        game = Game()
        game.ESPN_ID = game_id
        game.home_name, game.away_name = self._ncaab_team_names(game_id, sp)
        game.home_record, game.away_record = self._ncaab_records(game_id, sp)
        game.final_status = self._ncaab_final_status(game_id, sp)
        game.home_half_scores, game.away_half_scores = self._ncaab_half_scores(game_id, sp)
        game.home_score, game.away_score = self.ncaab_scores(game_id, sp)
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


# if __name__ == "__main__":
#     e = ESPN_Scraper()
#     nflh, nfla = e._nfl_team_names("401128044")
#     nflhr, nflar = e._nfl_records("401128044")
#     status = e._nfl_final_status("401128044")
#     home_score, away_score = e.nfl_scores("401128044")
