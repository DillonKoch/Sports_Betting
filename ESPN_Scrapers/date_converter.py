# ==============================================================================
# File: date_converter.py
# Project: ESPN_Scrapers
# File Created: Friday, 19th June 2020 8:59:03 am
# Author: Dillon Koch
# -----
# Last Modified: Friday, 19th June 2020 9:26:23 am
# Modified By: Dillon Koch
# -----
#
# -----
# super quick file to convert date types to all be the same in ESPN_Data
# ==============================================================================

import datetime
import os
import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


league = "NBA"
teams = os.listdir(ROOT_PATH + "/ESPN_Data/{}/".format(league))
print("{} {} teams".format(len(teams), league))

df_paths = []
for team in teams:
    team_df_paths = os.listdir(ROOT_PATH + "/ESPN_Data/{}/{}/".format(league, team))
    team_df_paths = [ROOT_PATH + "/ESPN_Data/{}/{}/{}".format(league, team, item) for item in team_df_paths]
    df_paths += team_df_paths

print("{} {} paths, {} per team".format(len(df_paths), league, (len(df_paths) / len(teams))))

all_dfs = [pd.read_csv(path) for path in tqdm(df_paths)]

print("Loaded all {} paths to dfs".format(len(all_dfs)))


# Converting the date now

def change_date(row):
    season_year = row['Season']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_to_num = {item: i + 1 for i, item in enumerate(months)}
    row_month = [item for item in months if item in row['Date']][0]
    row_month = month_to_num[row_month]
    date_words = row['Date'].replace(',', '').split(' ')
    row_day = [item for item in date_words if len(item) <= 2][0]
    year = season_year if row_month > 7 else season_year + 1
    dt = datetime.date(int(year), int(row_month), int(row_day))
    return datetime.date.strftime(dt, "%B %d, %Y")


df = all_dfs[0]
df['Date'] = df.apply(lambda row: change_date(row), axis=1)


for df, path in tqdm(zip(all_dfs, df_paths)):
    df['Date'] = df.apply(lambda row: change_date(row), axis=1)
