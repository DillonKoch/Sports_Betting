# ==============================================================================
# File: sbo_odds.py
# Project: Scrapers
# File Created: Sunday, 6th June 2021 8:40:49 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 6th June 2021 8:40:50 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping the NFL, NBA, NCAAF, NCAAB odds from www.sportsbookreviewsonline.com
# ==============================================================================


import datetime
import os
import sys
from os.path import abspath, dirname

import pandas as pd
import wget

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Sbo_Odds:
    def __init__(self):
        self.current_year = datetime.datetime.now().year
        self.last_year = self.current_year - 1

    def year_strs(self):  # Top Level
        """
        creates strings of the season start/end years for all seasons since 2007-08
        """
        year_strs = []
        for year in range(2007, self.current_year + 1):  # +1 makes it search for 2021-22 in late 2021
            next_yr_abbrev = str(int(year) + 1)[2:]
            year_str = f"{year}-{next_yr_abbrev}"
            year_strs.append(year_str)
        return year_strs

    def get_url(self, league, year_str):  # Top Level
        """
        given a league and year_str, this will return the proper url for SBO
        """
        url_base = "https://www.sportsbookreviewsonline.com/scoresoddsarchives/"
        if league in ["NFL", "NBA"]:
            url = url_base + f"{league.replace(' ', '')}/{league} odds {year_str}.xlsx"
        else:
            long_league = "ncaa football" if league == "NCAAF" else "ncaa basketball"
            url = url_base + f"{long_league.replace(' ', '')}/{long_league} {year_str}.xlsx"
        return url

    def download_past_yr(self, league, url):  # Top Level
        """
        downloads the excel file from a past year to /Data/Odds/league/
        """
        filename = url.split('/')[-1]
        output_path = ROOT_PATH + f"/Data/Odds/{league}/{filename}"
        if not os.path.exists(output_path):
            wget.download(url, out=output_path)

    def _download_temp_df(self, url):  # Helping Helper _update_current_year
        """
        downloads the .xlsx file from the url to a temporary file
        - used to update the existing file, then we delete the temp
        """
        temp_path = ROOT_PATH + f"/Data/Odds/temp.xlsx"
        wget.download(url, temp_path)
        return temp_path

    def _merge_current_temp(self, current_df, temp_df):  # Specific Helper _update_current_year
        """
        merges the currently downloaded df and new temp df based on # rows
        """
        current_len = len(current_df)
        temp_len = len(temp_df)
        if temp_len > current_len:
            return pd.concat([current_df, temp_df.iloc[current_len:, :]])
        else:
            return current_df

    def _update_current_year(self, url, full_path):  # Specific Helper download_current_yr
        """
        loads the current year's .xlsx file, downloads the same file from the internet,
        and merges the two to ensure the downloaded file is up to date
        """
        current_df = pd.read_excel(full_path)
        temp_path = self._download_temp_df(url)
        temp_df = pd.read_excel(temp_path)
        merged_df = self._merge_current_temp(current_df, temp_df)
        merged_df.to_excel(full_path, index=False)
        os.remove(temp_path)
        print(f"{full_path.split('/')[-1]}: {len(merged_df) - len(current_df)} new rows")

    def _download_new(self, url, full_path):  # Specific Helper download_current_yr
        """
        attempts to download the new .xlsx file for the current season if it exists yet
        """
        try:
            wget.download(url, out=full_path)
            print(f"Downloaded new .xlsx file from {url}")
        except BaseException:
            print(f"{full_path.split('/')[-1]} does not exist")

    def download_current_yr(self, league, url):  # Top Level
        """
        downloads a new file for the current year or updates the existing one
        """
        filename = url.split('/')[-1]
        full_path = ROOT_PATH + f"/Data/Odds/{league}/{filename}"
        file_exists = os.path.exists(full_path)
        if file_exists:
            self._update_current_year(url, full_path)
        else:
            self._download_new(url, full_path)

    def run(self, league):  # Run
        for year_str in self.year_strs():
            url = self.get_url(league, year_str)
            is_current_year = ((str(self.current_year) in url) or (str(self.last_year) in url))
            _ = self.download_current_yr(league, url) if is_current_year else self.download_past_yr(league, url)

    def run_all(self):  # Run
        print('-' * 50)
        print(datetime.datetime.now())
        print('-' * 50)
        for league in ["NFL", "NCAAF", "NBA", "NCAAB"]:
            print(league)
            self.run(league)


if __name__ == '__main__':
    x = Sbo_Odds()
    self = x
    x.run_all()
