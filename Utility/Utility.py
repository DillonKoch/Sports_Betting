# ==============================================================================
# File: Utility.py
# Project: Sports_Betting
# File Created: Friday, 10th April 2020 10:47:51 am
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 18th April 2020 3:54:17 pm
# Modified By: Dillon Koch
# -----
#
#
# -----
# Utility functions to be used in many places
# ==============================================================================

import datetime
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


def null_if_error(return_num):
    def null_if_error(orig_func):
        def wrapper_func(*args, **kwargs):
            try:
                return orig_func(*args, **kwargs)
            except BaseException:
                if return_num == 1:
                    return "NULL"
                elif return_num == 2:
                    return "NULL", "NULL"
                elif return_num == 3:
                    return "NULL", "NULL", "NULL"
        return wrapper_func
    return null_if_error


@null_if_error(1)
def dt_from_date_str(date, year=None):
    month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9,
                  "Oct": 10, "Nov": 11, "Dec": 12}
    days = [str(i) for i in range(1, 32, 1)]

    month = [month_dict[item] for item in month_dict.keys() if item in date][0]
    day = [item for item in days if item in date][-1]
    day = '0' + day if len(day) == 1 else day  # need leading 0 if single digit

    year = datetime.datetime.today().year if year is None else year

    return datetime.datetime(year, month, int(day))