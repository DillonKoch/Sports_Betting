
import json
import os
import re
import sys
import time
from os.path import abspath, dirname

import pandas as pd
from func_timeout import func_set_timeout
from tqdm import tqdm


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from espn_game_scraper import ESPN_Game_Scraper
from Utility import get_sp1, null_if_error


class ESPN_Season_Scraper:
    def __init__(self, league):
        self.league = league
        self.egs = ESPN_Game_Scraper()
        self.root_path = ROOT_PATH + '/'
        self.data_path = self.root_path + 'Data/{}'.format(self.league)

    @property
    def config(self):  # Property
        with open("{}.json".format(self.league.lower())) as f:
            data = json.load(f)
        return data

    @property
    def game_link_re(self):  # Property
        nba = re.compile(r"http://www.espn.com/nba/game\?gameId=(\d+)")
        nfl = re.compile(r"http://www.espn.com/nfl/game/_/gameId/(\d+)")
        ncaaf = re.compile(r"http://www.espn.com/college-football/game/_/gameId/(\d+)")
        ncaab = re.compile(r"http://www.espn.com/mens-college-basketball/game\?gameId=(\d+)")
        # "http://www.espn.com/mens-college-basketball/game?gameId=(\d+)"
        return nba if self.league == "NBA" else nfl if self.league == "NFL" else ncaaf if self.league == "NCAAF" else ncaab

    @property
    def game_info_func(self):  # Property
        nba = self.egs.all_nba_info
        nfl = self.egs.all_nfl_info
        ncaaf = self.egs.all_ncaaf_info
        ncaab = self.egs.all_ncaab_info
        return nba if self.league == "NBA" else nfl if self.league == "NFL" else ncaaf if self.league == "NCAAF" else ncaab

    @property
    def q_amount(self):  # Property
        return 2 if self.league == 'NCAAB' else 4

    def _make_season_df(self):  # Specific Helper scrape_season
        cols = self.config["DF Columns"]
        df = pd.DataFrame(columns=cols)
        return df

    def _get_game_sections(self, team_abbrev, year, season_type=2):  # Specific Helper scrape_season
        base_link = self.config["Season Base Link"].format(
            team_abbrev=team_abbrev, year=year, season_type=season_type)
        sp = get_sp1(base_link)
        sections = sp.find_all('tr', attrs={'class': 'filled Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'filled bb--none Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'bb--none Table__TR Table__TR--sm Table__even'})
        return sections

    def _week_from_section(self, section):  # Helping Helper _link_week_from_game_section
        td_htmls = section.find_all('td', attrs={'class': 'Table__TD'})
        week = td_htmls[0].get_text()
        return week

    def _link_week_from_game_section(self, section):  # Specific Helper scrape_season
        link = None
        td_htmls = section.find_all('td', attrs={'class': 'Table__TD'})
        for html in td_htmls:
            match = re.search(self.game_link_re, str(html))
            if match:
                link = match.group(0)

        week = self._week_from_section(section)
        return link, week

    def _link_week_to_row(self, df, link, week, year):  # Specific Helper scrape_season
        game_id = self.game_link_re.search(link).group(1)
        game = self.game_info_func(game_id)
        if self.league in ["NCAAB", "NCAAF"]:
            game.game_date = week

        season = year if self.league in ["NFL", "NCAAF"] else str(int(year) - 1)
        row = [game.ESPN_ID, season, game.game_date, game.home_name, game.away_name,
               game.home_record, game.away_record,
               game.home_score, game.away_score, game.line, game.over_under,
               game.final_status, game.network]

        if self.league != "NCAAB":
            for scores in [game.home_qscores, game.away_qscores]:
                row += [item for item in scores]
                if len(scores) == self.q_amount:
                    row += ["NULL"]
        else:
            for scores in [game.home_half_scores, game.away_half_scores]:
                row += [item for item in scores]
                if len(scores) == self.q_amount:
                    row += ['NULL']

        if self.league == "NFL":
            row.append(week)

        row.append(self.league)
        df.loc[len(df)] = row
        return df

    def scrape_season(self, team_abbrev, year, season_type=2):  # Run
        df = self._make_season_df()
        game_sections = self._get_game_sections(team_abbrev, year, season_type)
        link_week_pairs = [self._link_week_from_game_section(section) for section in game_sections]
        link_week_pairs = [item for item in link_week_pairs if item[0] is not None]
        for pair in tqdm(link_week_pairs):
            link, week = pair
            df = self._link_week_to_row(df, link, week, year)
            time.sleep(5)
        return df

    def find_years_unscraped(self, team_abbrev):  # Top Level
        path = "../Data/{}/{}/".format(self.league, team_abbrev)
        beginning_year = 1999 if self.league == "NCAAF" else 2002 if self.league == 'NCAAB' else 1993
        all_years = [str(item) for item in list(range(beginning_year, 2020, 1))]
        years_found = []
        year_comp = re.compile(r"\d{4}")
        for filename in os.listdir(path):
            match = re.search(year_comp, filename)
            if match:
                year = match.group(0)
                years_found.append(year)
        return [item for item in all_years if item not in years_found]

    def _get_years(self, year):  # Specific Helper scrape_team_history
        year = int(year)
        if self.league in ["NFL", "NCAAF"]:
            year1 = year
            year2 = year + 1
        else:
            year1 = year - 1
            year2 = year
        return year1, year2

    def scrape_team_history(self, team_abbrev, name=None):  # Run
        if name is None:
            name = team_abbrev
        years_unscraped = self.find_years_unscraped(name)
        for year in years_unscraped:
            print("Scraping data for {} {}".format(name, year))
            df = self.scrape_season(team_abbrev, year)
            year1, year2 = self._get_years(year)
            path = "../Data/{}/{}/{}_{}-{}.csv".format(self.league, name, name, year1, year2)
            df.to_csv(path, index=False)

    def scrape_all_leauge_history(self):  # Run
        team_abbrevs = [item[1] for item in self.config["Teams"]]
        names = [item[0] for item in self.config["Teams"]]
        for team_abbrev, name in zip(team_abbrevs, names):
            try:
                self.scrape_team_history(team_abbrev, name)
            except Exception as e:
                print(e)
                print("Error scraping, moving on to the next team")
                time.sleep(1)


def parse_league():  # Parse
    return None


if __name__ == "__main__":
    x = ESPN_Season_Scraper("NCAAB")
    # team_abbrev = 2294
    # name = "Iowa Hawkeyes"
    # year = 2019
    # season_type = 2
    # self = x
    x.scrape_all_leauge_history()