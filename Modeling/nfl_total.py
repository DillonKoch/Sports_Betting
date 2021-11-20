# ==============================================================================
# File: nfl_total.py
# Project: allison
# File Created: Saturday, 23rd October 2021 10:14:51 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 23rd October 2021 10:14:52 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Modeling NFL total bets
# ==============================================================================

import sys
from os.path import abspath, dirname

from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Total_Parent


class NFL_Total(Total_Parent):
    def __init__(self):
        super().__init__()
        self.league = "NFL"

    # def model_baseline_avg_points(self, avg_df_home_away_date, raw_df):  # Top Level
    #     # * left merge avg_df and the Home_Line_Close
    #     raw_df_home_line = raw_df[['Home', 'Away', 'Date', 'OU_Close']]
    #     df = pd.merge(avg_df_home_away_date, raw_df_home_line, how='left', on=['Home', 'Away', 'Date'])

    #     # * make predictions, evaluate
    #     labels = df['Over_Covered']
    #     home_pts = df['Home_Final']
    #     away_pts = df['Away_Final']
    #     total_pts = home_pts + away_pts
    #     preds = total_pts > df['OU_Close']

    #     self.plot_confusion_matrix(preds, labels, 'NBA Line')
    #     self.evaluation_metrics(preds, labels)
    #     self.spread_total_expected_return(preds, labels)

    def model_baseline(self):  # Top Level
        pass

    def model_logistic_regression(self, train_X, val_X, train_y, val_y):  # Top Level
        model = LogisticRegression(random_state=18, max_iter=10000)
        model.fit(train_X, train_y)
        preds = model.predict_proba(val_X)
        for thresh in [0.5, 0.55, 0.6, 0.65]:
            self.expected_return(preds, val_y, thresh)

        # self.plot_confusion_matrix(preds, val_y, self.confusion_matrix_title)
        # self.evaluation_metrics(preds, val_y)
        # self.spread_total_expected_return(preds, val_y)
        return model, ""

    def model_random_forest(self, train_X, val_X, train_y, val_y):  # Top Level
        model = RandomForestClassifier(max_depth=10, random_state=18, n_estimators=100)
        model.fit(train_X, train_y)
        preds = model.predict_proba(val_X)
        for thresh in [0.5, 0.55, 0.6, 0.65]:
            self.expected_return(preds, val_y, thresh)

        return model, ""

    def model_svm(self, train_X, val_X, train_y, val_y):  # Top Level
        model = svm.SVC(probability=True, kernel='linear')
        model.fit(train_X, train_y)
        preds = model.predict_proba(val_X)
        for thresh in [0.5, 0.55, 0.6, 0.65]:
            self.expected_return(preds, val_y, thresh)

        return model, ""

    def model_neural_net(self, train_X, val_X, train_y, val_y):  # Top Level
        pass

    def run(self, alg, past_games=10, player_stats=False):
        ps_str = "with" if player_stats else "no"
        dataset_desc = f"avg {past_games} past games, {ps_str} player stats"
        df = self.load_df(past_games=10, player_stats=False)
        finished_games_df, upcoming_games_df = self.split_finished_upcoming_games(df)
        balanced_df = self.balance_classes(finished_games_df)
        X, y, scaler = self.scaled_X_y(balanced_df)
        train_X, val_X, train_y, val_y = self.split_train_test(X, y)

        # * choose modeling technique, training
        model_method = self.model_method_dict[alg]
        model, model_desc = model_method(train_X, val_X, train_y, val_y)

        # * making predictions on upcoming_games_df, saving somewhere
        upcoming_games_X, _, _ = self.scaled_X_y(upcoming_games_df, scaler=scaler)
        self.make_preds(model, upcoming_games_df, upcoming_games_X, alg, model_desc, dataset_desc)

    def run_all(self):
        """
        runs all the algorithms and makes predictions to /Data/Predictions/
        """
        # algs = ['logistic regression', 'svm', 'random forest', 'neural net']
        algs = ['logistic regression', 'random forest', 'svm']
        for alg in algs:
            print(f"Running {alg}...")
            self.run(alg)


if __name__ == '__main__':
    x = NFL_Total()
    self = x
    x.run_all()
