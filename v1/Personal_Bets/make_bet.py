# ==============================================================================
# File: make_bet.py
# Project: Personal_Bets
# File Created: Tuesday, 28th July 2020 8:25:14 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 29th July 2020 8:00:26 am
# Modified By: Dillon Koch
# -----
#
# -----
# File for making a bet, used under the hood of make_bet_jn jupyter notebook
# ==============================================================================


from os.path import abspath, dirname
import sys
import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Make_Bet:
    def __init__(self, bettor):
        self.bettor = bettor.replace(" ", "_")
        self.df_path = ROOT_PATH + "/Personal_Bets/Data/{}.csv".format(self.bettor)

    def _load_existing_data(self):  # Specific Helper load_data
        """
        loads the existing dataframe for the bettor, or returns None if no df exists
        """
        try:
            df = pd.read_csv(self.df_path)
        except BaseException:
            print("No Data found for {}".format(self.bettor))
            df = None
        return df

    def _create_new_df(self):  # Specific Helper load_data
        """
        creates a new blank betting df
        """
        print("Creating new dataframe for {}".format(self.bettor))
        cols = ["Bettor", "Bet_ID", "Parlay_No", "Bet_type", "Sportsbook", "Bet_made_dt", "Bet_result_dt", "Bet_amount",
                "To_win_amount", "Home", "Away"]
        df = pd.DataFrame(columns=cols)
        return df

    def load_data(self):  # Top Level
        """
        loads existing df or creates new one for the bettor
        """
        df = self._load_existing_data()
        df = self._create_new_df() if df is None else df
        return df

    def _new_bet_id(self, df):  # Specific Helper
        """
        returns a bet ID for a new bet in the given dataframe
        """
        if len(df) == 0:
            return 1
        else:
            bet_ids = list(df['Bet_ID'])
            return bet_ids[-1] + 1

    def run(self):  # Run
        df = self.load_data()
        return df


if __name__ == "__main__":
    x = Make_Bet("Dillon Koch")
    self = x
    df = x.run()
