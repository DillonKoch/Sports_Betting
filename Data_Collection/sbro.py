# ==============================================================================
# File: sbro.py
# Project: allison
# File Created: Friday, 18th November 2022 10:59:12 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 18th November 2022 10:59:15 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping Sportsbook Reviews Online odds data
# * downloading .xlsx files to be saved locally in /Data/Odds
# ==============================================================================

import datetime
import os
import sys
from os.path import abspath, dirname

import wget

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class SBRO_Scraper:
    def __init__(self):
        self.leagues = ['NFL', 'NBA', 'NCAAF', 'NCAAB']
        self.current_year = datetime.datetime.now().year
        self.last_year = self.current_year - 1

    def create_folders(self):  # Top Level
        """
        creating "Odds" folder in /Data/ and league folders in /Data/Odds
        """
        if not os.path.exists(ROOT_PATH + "/Data/Odds/"):
            os.mkdir(ROOT_PATH + "/Data/Odds")

        for league in self.leagues:
            path = ROOT_PATH + f"/Data/Odds/{league}"
            if not os.path.exists(path):
                os.mkdir(path)

    def _year_strs(self):  # Specific Helper run_one
        """
        creates strings of the season start/end years for all seasons since 2007-08
        """
        year_strs = []
        for year in range(2007, self.current_year + 1):  # +1 makes it search for 2021-22 in late 2021
            next_yr_abbrev = str(int(year) + 1)[2:]
            year_str = f"{year}-{next_yr_abbrev}"
            year_strs.append(year_str)
        return year_strs

    def _get_url(self, league, year_str):  # Specific Helper run_one
        """
        given a league and year_str, this will return the proper url for SBRO
        """
        url_base = "https://www.sportsbookreviewsonline.com/scoresoddsarchives/"
        if league in ["NFL", "NBA"]:
            url = url_base + f"{league.replace(' ', '')}/{league} odds {year_str}.xlsx"
        else:
            long_league = "ncaa football" if league == "NCAAF" else "ncaa basketball"
            url = url_base + f"{long_league.replace(' ', '')}/{long_league} {year_str}.xlsx"
        return url

    def _download_xlsx(self, url, league):  # Specific Helper run_one
        """
        downloading one .xlsx file using the given url
        """
        filename = url.split('/')[-1].replace(' ', '_')
        full_path = ROOT_PATH + f"/Data/Odds/{league}/{filename}"
        wget.download(url, out=full_path)

    def run_one(self, league, current_only):  # Top Level
        """
        running the download process for one league, optionally for all years since 2007 or current only
        """
        # * obtaining year strs
        year_strs = self._year_strs()
        year_strs = year_strs[-2:] if current_only else year_strs

        # * creating url and downloading for every year str
        for year_str in year_strs:
            url = self._get_url(league, year_str)
            print(url)
            self._download_xlsx(url, league)

    def run_all(self, current_only):  # Run
        # * Performs downloads for all leagues (current years only or all years since 2007)
        self.create_folders()
        for league in self.leagues:
            self.run_one(league, current_only)


if __name__ == '__main__':
    x = SBRO_Scraper()
    self = x
    current_only = True
    x.run_all(current_only)
