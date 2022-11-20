# ==============================================================================
# File: download_data.py
# Project: Odds
# File Created: Sunday, 25th October 2020 10:39:36 am
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 25th October 2020 1:06:53 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Downloads the newest .xlsx files from the odds website
# ==============================================================================

import datetime
import os
import sys
from os.path import abspath, dirname

import wget

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Download_Data:
    def __init__(self):
        self.link_base = "https://www.sportsbookreviewsonline.com/scoresoddsarchives/"

    def _get_year_strs(self):  # Global Helper  Tested
        """
        producing this year and last year's year strings in format 2020-21
        - these are used in creating the urls
        """
        current_year = datetime.date.today().year
        current_year_str = str(current_year) + '-' + str(current_year + 1)[2:]

        last_year = current_year - 1
        last_year_str = str(last_year) + '-' + str(last_year + 1)[2:]
        return current_year_str, last_year_str

    def get_ncaa_urls(self, league):  # Top Level  Tested
        """
        getting the paths to this year and last year's ncaa urls for an ncaa league
        - ncaa urls are formatted differently than pro urls
        - I'm doing this for both years because either df could be updated depending on the
          time of year (updating last 2020-21 in Jan '21, but updating 21-22 in Oct '21)
        """
        league = 'ncaa football' if league == 'NCAAF' else 'ncaa basketball'
        no_space_league = league.replace(' ', '')
        current_year_str, last_year_str = self._get_year_strs()
        url1 = self.link_base + f"{no_space_league}/{league} {current_year_str}.xlsx"
        url2 = self.link_base + f"{no_space_league}/{league} {last_year_str}.xlsx"
        return [url1, url2]

    def get_pro_urls(self, league):  # Top Level  Tested
        """
        getting the paths to this year and last year's pro urls for NFL, NBA
        - ncaa urls are formatted differently than pro urls
        - I'm doing this for both years because either df could be updated depending on the
          time of year (updating last 2020-21 in Jan '21, but updating 21-22 in Oct '21)
        """
        league = league.lower()
        current_year_str, last_year_str = self._get_year_strs()
        url1 = self.link_base + f"{league}/{league} odds {current_year_str}.xlsx"
        url2 = self.link_base + f"{league}/{league} odds {last_year_str}.xlsx"
        return [url1, url2]

    def remove_old_file(self, url, league):  # Top Level  Tested
        """
        Deletes the old .xlsx file that is about to be replaced with a newly downloaded one
        """
        filename = url.split('/')[-1]
        full_path = ROOT_PATH + f"/Odds/{league}/{filename}"
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            print(f"{filename} does not exist")

    def download_file(self, url, league):  # Top Level  Tested
        """
        downloads the df from the url and saves in the 'league' folder
        """
        filename = url.split('/')[-1]
        output_dir = ROOT_PATH + f"/Odds/{league}/{filename}"
        try:
            wget.download(url, out=output_dir)
        except BaseException:
            print(f"{filename} does not exist")

    def run(self, league):  # Run
        if 'NCAA' in league:
            urls = self.get_ncaa_urls(league)
        else:
            urls = self.get_pro_urls(league)

        for url in urls:
            self.remove_old_file(url, league)
            self.download_file(url, league)


if __name__ == '__main__':
    x = Download_Data()
    self = x
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x.run(league)
