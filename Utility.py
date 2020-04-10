# ==============================================================================
# File: Utility.py
# Project: Sports_Betting
# File Created: Friday, 10th April 2020 10:47:51 am
# Author: Dillon Koch
# -----
# Last Modified: Friday, 10th April 2020 10:47:54 am
# Modified By: Dillon Koch
# -----
#
#
# -----
# Utility functions to be used in many places
# ==============================================================================

import urllib.request
from bs4 import BeautifulSoup as soup


def get_sp1(link):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(link, None, headers)  # The assembled request
    response = urllib.request.urlopen(request)

    a = response.read().decode('utf-8', 'ignore')
    sp = soup(a, 'html.parser')
    return sp

# sp = get_sp1("https://www.espn.com/nfl/game/_/gameId/401128044")
