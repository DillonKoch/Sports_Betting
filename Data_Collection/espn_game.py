# ==============================================================================
# File: espn_game.py
# Project: allison
# File Created: Saturday, 26th November 2022 2:32:29 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 26th November 2022 2:32:29 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping game data from ESPN
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Scrape_ESPN_Game:
    def __init__(self):
        pass

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = Scrape_ESPN_Game()
    self = x
    x.run()
