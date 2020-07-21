# ==============================================================================
# File: create_pdf.py
# Project: Results
# File Created: Sunday, 19th July 2020 5:26:27 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 20th July 2020 8:49:31 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File to create a PDF of bets and predictions for upcoming games in each league
# ==============================================================================

import datetime
import sys
from os.path import abspath, dirname

import pandas as pd
from fpdf import FPDF
import string

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class PDF:
    def __init__(self):
        self.date_str = datetime.date.today().strftime("%Y_%m_%d")
        self.pdf_path = ROOT_PATH + "/Results/PDFs/{}_Bets.pdf".format(self.date_str)

    def load_data(self, league):  # Global Helper
        df_path = ROOT_PATH + "/Results/{}_Results.csv".format(league)
        df = pd.read_csv(df_path)
        df['datetime'] = pd.to_datetime(df['datetime']).apply(lambda x: x.date())
        df = df.sort_values(by=["datetime", "Game_Time"])
        df['Home_Record'].fillna("0-0, 0-0 Home", inplace=True)
        df['Away_Record'].fillna("0-0, 0-0 Away", inplace=True)
        return df

    def get_game_link(self, league, ESPN_ID):  # Global Helper
        link_dict = {"NFL": "https://www.espn.com/nfl/game/_/gameId/{}"}
        link = link_dict[league].format(ESPN_ID)
        return link

    def get_team_link(self, league, team_name):  # Global Helper
        # low priority since you can click the game link, then team from there
        pass

    def create_recap_page(self, pdf):  # Top Level
        pass

    def create_bet_history_page(self, pdf):  # Top Level
        pass

    def _add_image(self, pdf, row, depth, league):  # Helping Helper _add_nfl_game (probably global helper later)
        # TODO add links to ESPN team page on the image!
        home_team = row['Home']
        home_img_path = ROOT_PATH + "/Results/Logos/{}/{}.gif".format(league, home_team)
        away_team = row['Away']
        away_img_path = ROOT_PATH + "/Results/Logos/{}/{}.gif".format(league, away_team)

        pdf.image(home_img_path, 5, depth, w=24, h=16)
        pdf.image(away_img_path, 40, depth, w=24, h=16)
        pdf.set_font('arial', size=10)
        pdf.set_xy(31, depth + 8)
        pdf.cell(w=5, txt="@")
        return pdf

    def _add_records(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_record = str(row['Home_Record'])
        away_record = str(row['Away_Record'])

        pdf.set_xy(5, depth + 16)
        pdf.cell(w=24, h=8, txt=away_record, border=0)
        pdf.set_xy(39, depth + 16)
        pdf.cell(w=24, h=8, txt=home_record, border=0)
        return pdf

    def _add_game_cell(self, pdf, depth):  # Helping Helper _add_nfl_game
        pdf.set_xy(75, depth - 3)
        pdf.cell(w=125, h=24, txt='', border=1)
        return pdf

    def _clean_gametime(self, game_time_str):  # Helping Helper _add_game_info
        hour, minute = game_time_str.split(":")
        hour = int(hour)
        if hour == 12:
            am_or_pm = "pm"
        elif hour > 12:
            hour -= 12
            am_or_pm = "pm"
        else:
            am_or_pm = "am"

        new_str = "{}:{} {}".format(hour, minute, am_or_pm)
        return new_str

    def _add_game_info(self, pdf, row, depth, league):  # Helping Helper _add_nfl_game
        game_date = row['datetime'].strftime("%B %d, %Y")
        game_time = row['Game_Time'].replace("CDT", "").strip()
        game_time = self._clean_gametime(game_time)
        title = row['Title']
        network = row['Network']
        game_str = "{} - {} ({}), {}".format(title, game_date, game_time, network)
        game_link = self.get_game_link(league, row['ESPN_ID'])
        pdf.set_xy(100, depth - 9)
        pdf.set_font('arial', size=9)
        pdf.set_text_color(r=51, g=153, b=255)
        pdf.cell(w=75, h=7, txt=game_str, border=0, align="C", link=game_link)
        pdf.set_font('arial', size=11)
        pdf.set_text_color(0, 0, 0)
        return pdf

    def _add_team_names(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_team = row['Home']
        away_team = row['Away']

        pdf.set_xy(75, depth - 3)
        pdf.cell(w=39, h=8, txt=home_team, border=1, align="C")
        pdf.set_xy(75, depth + 5)
        pdf.cell(w=39, h=8, txt=away_team, border=1, align="C")
        pdf.set_text_color(r=128, g=128, b=128)
        pdf.set_xy(75, depth + 13)
        pdf.cell(w=39, h=8, txt="AI-Predicted Lines", border=1, align="C")
        pdf.set_text_color(r=0, g=0, b=0)
        return pdf

    def _add_moneylines(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_ml = str(row['Home_ML_ESB'])
        away_ml = str(row['Away_ML_ESB'])
        home_ml = "+" + home_ml if home_ml[0] in string.digits else home_ml
        away_ml = "+" + away_ml if away_ml[0] in string.digits else away_ml
        # TODO add predicted ML's once I have a model for that

        pdf.set_xy(114, depth - 3)
        pdf.cell(w=12, h=8, txt=home_ml, border=1, align="C")
        pdf.set_xy(114, depth + 5)
        pdf.cell(w=12, h=8, txt=away_ml, border=1, align="C")
        return pdf

    def _add_moneyline_predictions(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_win_pct = row['Pred_Home_win']
        away_win_pct = 100 - home_win_pct
        home_win_pct = int(round(home_win_pct, 0))
        away_win_pct = int(round(away_win_pct, 0))
        home_win_pct = str(home_win_pct) + "%"
        away_win_pct = str(away_win_pct) + "%"

        pdf.set_xy(126, depth - 3)
        pdf.cell(w=10, h=8, txt=home_win_pct, border=1, align="C")
        pdf.set_xy(126, depth + 5)
        pdf.cell(w=10, h=8, txt=away_win_pct, border=1, align="C")
        return pdf

    def _add_nfl_game(self, pdf, row, num_games):  # Specific Helper create_nfl_page
        depth = (33 * num_games) - 15
        pdf = self._add_image(pdf, row, depth, "NFL")
        pdf = self._add_records(pdf, row, depth)
        pdf = self._add_game_cell(pdf, depth)
        pdf = self._add_game_info(pdf, row, depth, "NFL")
        pdf = self._add_team_names(pdf, row, depth)
        pdf = self._add_moneylines(pdf, row, depth)
        pdf = self._add_moneyline_predictions(pdf, row, depth)
        return pdf

    def create_nfl_page(self, pdf):  # Top Level
        pdf.add_page()
        df = self.load_data("NFL")
        num_games = 1
        for i, row in df.iterrows():
            pdf = self._add_nfl_game(pdf, row, num_games)
            num_games += 1
            if num_games == 9:
                pdf.add_page()
                num_games = 1

        return pdf

    def create_nba_page(self, pdf):  # Top Level
        pass

    def create_ncaaf_page(self, pdf):  # Top Level
        pass

    def create_ncaab_page(self, pdf):  # Top Level
        pass

    def save_pdf(self, pdf):  # Top Level
        pdf.output(self.pdf_path, 'F').encode('utf-8', 'ignore')

    def run(self):  # Run
        pdf = FPDF()
        pdf.add_page()
        pdf = self.create_nfl_page(pdf)
        self.save_pdf(pdf)
        return pdf


if __name__ == "__main__":
    x = PDF()
    self = x
    x.run()
