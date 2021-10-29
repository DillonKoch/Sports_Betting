# ==============================================================================
# File: nfl_decision_tree_wl.py
# Project: allison
# File Created: Thursday, 19th August 2021 10:17:10 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 19th August 2021 10:17:10 pm
# Modified By: Dillon Koch
# -----
#
# -----
# using Decision Trees to model the winner of NFL games
# ==============================================================================


import sys
from os.path import abspath, dirname

from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Data_Cleaning.model_data import Model_Data


class NFL_DT_WL:
    def __init__(self):
        self.model_data = Model_Data("NFL")

        self.football_stats = ['1st_Downs', 'Passing_1st_downs', 'Rushing_1st_downs', '1st_downs_from_penalties',
                               '3rd_down_efficiency', '4th_down_efficiency', 'Total_Plays', 'Total_Yards', 'Total_Drives',
                               'Yards_per_Play', 'Passing', 'Comp_Att', 'Yards_per_pass', 'Interceptions_thrown',
                               'Sacks_Yards_Lost', 'Rushing', 'Rushing_Attempts', 'Yards_per_rush', 'Red_Zone_Made_Att',
                               'Penalties', 'Turnovers', 'Fumbles_lost', 'Defensive_Special_Teams_TDs',
                               'Possession']

        self.cols = ['Home_1st_Downs',
                     'Away_1st_Downs',
                     'Home_Passing_1st_downs',
                     'Away_Passing_1st_downs',
                     'Home_Rushing_1st_downs',
                     'Away_Rushing_1st_downs',
                     'Home_1st_downs_from_penalties',
                     'Away_1st_downs_from_penalties',
                     'Home_Total_Plays',
                     'Away_Total_Plays',
                     'Home_Total_Yards',
                     'Away_Total_Yards',
                     'Home_Total_Drives',
                     'Away_Total_Drives',
                     'Home_Yards_per_Play',
                     'Away_Yards_per_Play',
                     'Home_Passing',
                     'Away_Passing',
                     'Home_Yards_per_pass',
                     'Away_Yards_per_pass',
                     'Home_Interceptions_thrown',
                     'Away_Interceptions_thrown',
                     'Home_Rushing',
                     'Away_Rushing',
                     'Home_Rushing_Attempts',
                     'Away_Rushing_Attempts',
                     'Home_Yards_per_rush',
                     'Away_Yards_per_rush',
                     'Home_Turnovers',
                     'Away_Turnovers',
                     'Home_Fumbles_lost',
                     'Away_Fumbles_lost',
                     'Home_3rd_downs_converted',
                     'Home_3rd_downs_total',
                     'Away_3rd_downs_converted',
                     'Away_3rd_downs_total',
                     'Home_4th_downs_converted',
                     'Home_4th_downs_total',
                     'Away_4th_downs_converted',
                     'Away_4th_downs_total',
                     'Home_Passes_completed',
                     'Home_Passes_attempted',
                     'Away_Passes_completed',
                     'Away_Passes_attempted',
                     'Home_Sacks',
                     'Home_Sacks_Yards_Lost',
                     'Away_Sacks',
                     'Away_Sacks_Yards_Lost',
                     'Home_Red_Zone_Conversions',
                     'Home_Red_Zone_Trips',
                     'Away_Red_Zone_Conversions',
                     'Away_Red_Zone_Trips',
                     'Home_Penalties',
                     'Home_Penalty_Yards',
                     'Away_Penalties',
                     'Away_Penalty_Yards',
                     'Home_Possession',
                     'Away_Possession']

    def run(self):  # Run
        training_data = self.model_data.training_data(self.cols, ['Home_ML'])
        X = training_data[self.cols]
        y = training_data['Home_ML']
        train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=18)
        # my_imputer = SimpleImputer()
        # train_X = pd.DataFrame(my_imputer.fit_transform(train_X))
        # val_X = pd.DataFrame(my_imputer.transform(val_X))
        my_scaler = StandardScaler()
        train_X = pd.DataFrame(my_scaler.fit_transform(train_X))
        val_X = pd.DataFrame(my_scaler.transform(val_X))
        for n in range(100, 5000, 100):
            model = XGBRegressor(n_estimators=n)
            model.fit(train_X, train_y)
            preds = model.predict(val_X)
            mae = mean_absolute_error(preds, val_y)
            print(n, mae)
        return preds


if __name__ == '__main__':
    x = NFL_DT_WL()
    self = x
    preds = x.run()
