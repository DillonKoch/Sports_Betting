# ==============================================================================
# File: wh_perform_scrapes.py
# Project: Data
# File Created: Saturday, 29th August 2020 5:00:06 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 29th August 2020 5:01:01 pm
# Modified By: Dillon Koch
# -----
#
# -----
# file for running all william hill scrapers according to json files for each league
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class WH_Perform_Scrapes:
    def __init__(self):
        pass

    def run(self):  # Run
        pass


if __name__ == "__main__":
    x = WH_Perform_Scrapes()
    self = x
    x.run()
