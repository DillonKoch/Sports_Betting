# ==============================================================================
# File: espn_season_scraper.py
# Project: ESPN_Scrapers
# File Created: Saturday, 23rd May 2020 11:04:56 am
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 24th June 2020 5:36:45 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraping seasons from ESPN
# ==============================================================================

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

from ESPN_Scrapers.espn_game_scraper import ESPN_Game_Scraper
from Utility.Utility import get_sp1, null_if_error


class ESPN_Season_Scraper:
    def __init__(self, league):
        self.league = league
        self.egs = ESPN_Game_Scraper()
        self.root_path = ROOT_PATH + '/'
        self.data_path = self.root_path + 'ESPN_Data/{}'.format(self.league)

    @property
    def config(self):  # Property  Tested
        with open(self.root_path + "ESPN_Scrapers/{}.json".format(self.league.lower())) as f:
            data = json.load(f)
        return data

    @property
    def game_link_re(self):  # Property  Tested
        nba = re.compile(r"http://www.espn.com/nba/game\?gameId=(\d+)")
        nfl = re.compile(r"http://www.espn.com/nfl/game/_/gameId/(\d+)")
        ncaaf = re.compile(r"http://www.espn.com/college-football/game/_/gameId/(\d+)")
        ncaab = re.compile(r"http://www.espn.com/mens-college-basketball/game\?gameId=(\d+)")
        return nba if self.league == "NBA" else nfl if self.league == "NFL" else ncaaf if self.league == "NCAAF" else ncaab

    @property
    def game_info_func(self):  # Property
        nba = self.egs.all_nba_info
        nfl = self.egs.all_nfl_info
        ncaaf = self.egs.all_ncaaf_info
        ncaab = self.egs.all_ncaab_info
        return nba if self.league == "NBA" else nfl if self.league == "NFL" else ncaaf if self.league == "NCAAF" else ncaab

    @property
    def q_amount(self):  # Property  Tested
        return 2 if self.league == 'NCAAB' else 4

    def _make_season_df(self):  # Specific Helper scrape_season  Tested
        cols = self.config["DF Columns"]
        df = pd.DataFrame(columns=cols)
        return df

    def _get_game_sections(self, team_abbrev, year, season_type=2):  # Specific Helper scrape_season  Tested
        base_link = self.config["Season Base Link"].format(
            team_abbrev=team_abbrev, year=year, season_type=season_type)
        sp = get_sp1(base_link)
        sections = sp.find_all('tr', attrs={'class': 'filled Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'filled bb--none Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'bb--none Table__TR Table__TR--sm Table__even'})
        return sections

    def _week_from_section(self, section):  # Helping Helper _link_week_from_game_section  Tested
        """
        ONLY TO BE USED FOR NFL GAMES TO GET THE WEEK - GAME DATES COME FROM ESPN_GAME_SCRAPER
        """
        td_htmls = section.find_all('td', attrs={'class': 'Table__TD'})
        week = td_htmls[0].get_text()
        return week

    def _link_from_game_section(self, section):  # Specific Helper scrape_season  Tested
        link = None
        td_htmls = section.find_all('td', attrs={'class': 'Table__TD'})
        for html in td_htmls:
            match = re.search(self.game_link_re, str(html))
            if match:
                link = match.group(0)
        return link

    def _link_week_to_row(self, df, link, week, year):  # Specific Helper scrape_season
        game_id = self.game_link_re.search(link).group(1)
        game = self.game_info_func(game_id)

        season = year if self.league in ["NFL", "NCAAF"] else str(int(year) - 1)
        row = [game.ESPN_ID, season, game.game_date, game.home_name, game.away_name,
               game.home_record, game.away_record,
               game.home_score, game.away_score, game.line, game.over_under,
               game.final_status, game.network]

        if self.league != "NCAAB":
            for scores in [game.home_qscores, game.away_qscores]:
                row += [item for item in scores]
                if len(scores) == self.q_amount:
                    row += [None]
        else:
            for scores in [game.home_half_scores, game.away_half_scores]:
                if ((self.league == "NCAAB") and (len(scores) == 4)):
                    first_half = int(scores[0]) + int(scores[1])
                    second_half = int(scores[2]) + int(scores[3])
                    row += [first_half, second_half, None]
                elif ((self.league == "NCAAB") and (len(scores) == 5)):
                    first_half = int(scores[0]) + int(scores[1])
                    second_half = int(scores[2]) + int(scores[3])
                    overtime = int(scores[4])
                    row += [first_half, second_half, overtime]
                else:
                    row += [item for item in scores]
                    if len(scores) == self.q_amount:
                        row += [None]

        if self.league == "NFL":
            row.append(week)
        row.append(self.league)
        df.loc[len(df)] = row
        return df

    def scrape_season(self, team_abbrev, year, season_type=2):  # Top Level
        df = self._make_season_df()
        game_sections = self._get_game_sections(team_abbrev, year, season_type)
        for section in tqdm(game_sections):
            week = self._week_from_section(section) if self.league == "NFL" else None
            link = self._link_from_game_section(section)
            if link is None:
                continue
            df = self._link_week_to_row(df, link, week, year)
            time.sleep(5)
        return df

    def scrape_upcoming_games(self, team_abbrev, year, season_type=2):  # Run  FIXME
        df = self.scrape_season(team_abbrev, year, season_type)
        # make cols None if the game hasn't happened yet...

    def _find_unscraped_playoff_years(self, team):  # Specific Helper scrape_nba_playoffs
        team_csvs = os.listdir(ROOT_PATH + "/ESPN_Data/NBA/{}/".format(team))
        playoff_csvs = [item for item in team_csvs if '.csv' in item and "playoff" in item]
        playoff_csv_years = [item[-8:-4] for item in playoff_csvs]
        all_years = [str(item) for item in list(range(1993, 2021, 1))]
        unscraped_years = [item for item in all_years if item not in playoff_csv_years]
        return unscraped_years

    def scrape_nba_playoffs(self):  # Run
        """
        ONLY USED FOR NBA SINCE THEIR PLAYOFF GAMES ARE ON A SEPARATE PAGE
        """
        teams = [item[0] for item in self.config["Teams"]]
        team_abbrevs = [item[1] for item in self.config["Teams"]]
        all_years = [str(item) for item in list(range(1993, 2021, 1))]

        for team, abrev in zip(teams, team_abbrevs):
            unscraped_years = self._find_unscraped_playoff_years(team)
            years = [item for item in all_years if item in unscraped_years]
            for year in years:
                try:
                    print("Scraping {} {} playoffs data...".format(team, year))
                    df = self.scrape_season(abrev, year, 3)
                    year1, year2 = self._get_years(year)
                    df.to_csv(ROOT_PATH + "/ESPN_Data/NBA/{}/{}_playoffs_{}-{}.csv".format(team, team, year1, year2))
                except Exception as e:
                    print(e)
                    print("Error scraping {} {} playoffs data, moving on...".format(team, year))
                    time.sleep(30)

    def find_years_unscraped(self, team_name):  # Top Level
        path = self.root_path + "ESPN_Data/{}/{}/".format(self.league, team_name)
        beginning_year = 1999 if self.league == "NCAAF" else 2002 if self.league == 'NCAAB' else 2006
        all_years = [str(item) for item in list(range(beginning_year, 2021, 1))]
        years_found = []
        year_comp = re.compile(r"(\d{4}).csv")
        for filename in os.listdir(path):
            if "playoff" not in filename:
                match = re.search(year_comp, filename)
                if match:
                    year = match.group(1)
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

    def scrape_team_history(self, team_abbrev, name):  # Run
        years_unscraped = self.find_years_unscraped(name)
        for year in years_unscraped:
            print("Scraping data for {} {}".format(name, year))
            df = self.scrape_season(team_abbrev, year)
            year1, year2 = self._get_years(year)
            path = self.root_path + "ESPN_Data/{}/{}/{}_{}-{}.csv".format(self.league, name, name, year1, year2)
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


if __name__ == "__main__":
    nfl = ESPN_Season_Scraper("NFL")
    nba = ESPN_Season_Scraper("NBA")
    ncaaf = ESPN_Season_Scraper("NCAAF")
    ncaab = ESPN_Season_Scraper("NCAAB")
    # nfl.scrape_all_leauge_history()
