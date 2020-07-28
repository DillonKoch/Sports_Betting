# ==============================================================================
# File: create_pdf.py
# Project: Results
# File Created: Sunday, 19th July 2020 5:26:27 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 28th July 2020 9:43:10 am
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File to create a PDF of bets and predictions for upcoming games in each league
# ==============================================================================

import datetime
import smtplib
import ssl
import string
import sys
from email.message import EmailMessage
from os.path import abspath, dirname

import pandas as pd
from fpdf import FPDF

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
        ESPN_ID = str(int(ESPN_ID))
        link_dict = {"NFL": "https://www.espn.com/nfl/game/_/gameId/{}",
                     "NBA": "https://www.espn.com/nba/game?gameId={}"}
        link = link_dict[league].format(ESPN_ID)
        return link

    def create_recap_page(self, pdf):  # Top Level
        pass

    def create_bet_history_page(self, pdf):  # Top Level
        pass

    def _add_image(self, pdf, row, depth, league):  # Helping Helper _add_nfl_game (probably global helper later)
        home_team = row['Home']
        home_img_path = ROOT_PATH + "/Results/Logos/{}/{}.gif".format(league, home_team)
        away_team = row['Away']
        away_img_path = ROOT_PATH + "/Results/Logos/{}/{}.gif".format(league, away_team)

        pdf.image(home_img_path, 3, depth, w=24, h=16)
        pdf.image(away_img_path, 38, depth, w=24, h=16)
        pdf.set_font('arial', size=10)
        pdf.set_xy(29, depth + 8)
        pdf.cell(w=5, txt="@")
        return pdf

    def _add_records(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_record = str(row['Home_Record'])
        away_record = str(row['Away_Record'])

        pdf.set_xy(3, depth + 16)
        pdf.cell(w=24, h=8, txt=away_record, border=0, align="C")
        pdf.set_xy(37, depth + 16)
        pdf.cell(w=24, h=8, txt=home_record, border=0, align="C")
        return pdf

    def _add_game_cell(self, pdf, depth):  # Helping Helper _add_nfl_game
        pdf.set_xy(65, depth - 3)
        pdf.cell(w=141, h=24, txt='', border=1)
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
        pdf.set_xy(90, depth - 9)
        pdf.set_font('arial', size=9)
        pdf.set_text_color(r=51, g=153, b=255)
        pdf.cell(w=75, h=7, txt=game_str, border=0, align="C", link=game_link)
        pdf.set_font('arial', size=11)
        pdf.set_text_color(0, 0, 0)
        return pdf

    def _add_team_names(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_team = row['Home']
        away_team = row['Away']

        pdf.set_xy(65, depth - 3)
        pdf.cell(w=41, h=8, txt=home_team, border=1, align="C")
        pdf.set_xy(65, depth + 5)
        pdf.cell(w=41, h=8, txt=away_team, border=1, align="C")
        pdf.set_text_color(r=128, g=128, b=128)
        pdf.set_xy(65, depth + 13)
        pdf.cell(w=41, h=8, txt="AI-Predicted Lines", border=1, align="C")
        pdf.set_text_color(r=0, g=0, b=0)
        return pdf

    def _add_moneylines(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_ml = str(row['Home_ML_ESB'])
        away_ml = str(row['Away_ML_ESB'])
        home_ml = "+" + home_ml if home_ml[0] in string.digits else home_ml
        away_ml = "+" + away_ml if away_ml[0] in string.digits else away_ml

        home_win_pct = row['Pred_Home_ML_win']
        away_win_pct = 100 - home_win_pct
        home_win_pct = int(round(home_win_pct, 0))
        away_win_pct = int(round(away_win_pct, 0))
        home_win_pct = str(home_win_pct) + "%"
        away_win_pct = str(away_win_pct) + "%"

        home_ml_msg = home_ml + " [{}]".format(home_win_pct)
        away_ml_msg = away_ml + " [{}]".format(away_win_pct)

        pdf.set_xy(106, depth - 3)
        pdf.cell(w=22, h=8, txt=home_ml_msg, border=1, align="C")
        pdf.set_xy(106, depth + 5)
        pdf.cell(w=22, h=8, txt=away_ml_msg, border=1, align="C")
        return pdf

    def _add_lines(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_line = row['Home_Line_ESB']
        home_line_ml = int(round(row['Home_Line_ml_ESB'], 0))
        home_line_win_pct = int(round(row['Pred_Home_Line_win'], 0))
        away_line = row['Away_Line_ESB']
        away_line_ml = int(round(row['Away_Line_ml_ESB'], 0))
        away_line_win_pct = int(round(100 - home_line_win_pct, 0))
        home_line_msg = "{} ({}) [{}%]".format(home_line, home_line_ml, home_line_win_pct)
        away_line_msg = "{} ({}) [{}%]".format(away_line, away_line_ml, away_line_win_pct)
        home_line_msg = "+" + home_line_msg if home_line_msg[0] in string.digits else home_line_msg
        away_line_msg = "+" + away_line_msg if away_line_msg[0] in string.digits else away_line_msg

        pdf.set_xy(128, depth - 3)
        pdf.cell(w=33, h=8, txt=home_line_msg, border=1, align="C")
        pdf.set_xy(128, depth + 5)
        pdf.cell(w=33, h=8, txt=away_line_msg, border=1, align="C")
        return pdf

    def _add_over_unders(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        over = row['Over_ESB']
        over = int(over) if int(over) == over else over
        over_ml = int(round(row['Over_ml_ESB'], 0))
        over_win_pct = int(round(row['Pred_Over_win'], 0))
        under = row['Under_ESB']
        under = int(under) if int(under) == under else under
        under_ml = int(round(row['Under_ml_ESB'], 0))
        under_win_pct = int(round(100 - over_win_pct, 0))

        over_msg = f"O {over} ({over_ml}) [{over_win_pct}%]"
        under_msg = f"U {under} ({under_ml}) [{under_win_pct}%]"

        pdf.set_xy(161, depth - 3)
        pdf.cell(w=37, h=8, txt=over_msg, border=1, align="C")
        pdf.set_xy(161, depth + 5)
        pdf.cell(w=37, h=8, txt=under_msg, border=1, align="C")
        return pdf

    def _add_predicted_score(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        home_score = str(int(row['Pred_Home_Score']))
        away_score = str(int(row['Pred_Away_Score']))

        pdf.set_xy(198, depth - 3)
        pdf.cell(w=8, h=8, txt=home_score, border=1, align="C")
        pdf.set_xy(198, depth + 5)
        pdf.cell(w=8, h=8, txt=away_score, border=1, align="C")
        return pdf

    def _add_predicted_ml(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        # pred_home_ml = str(row['Pred_Home_ML'])
        # pred_home_ml = "+" + pred_home_ml if pred_home_ml[0] in string.digits else pred_home_ml
        # pred_away_ml = str(row['Pred_Away_ML'])
        # pred_away_ml = "+" + pred_away_ml if pred_away_ml[0] in string.digits else pred_away_ml
        # pred_ml_msg = f"{pred_home_ml}, {pred_away_ml}"

        pred_home_ml = row['Pred_Home_ML']
        pred_home_ml = pred_home_ml + 100 if pred_home_ml >= 0 else pred_home_ml - 100
        pred_home_ml = str(pred_home_ml)
        pred_home_ml = "+" + pred_home_ml if pred_home_ml[0] in string.digits else pred_home_ml
        pred_away_ml = row['Pred_Away_ML']
        pred_away_ml = pred_away_ml + 100 if pred_away_ml >= 0 else pred_away_ml - 100
        pred_away_ml = str(pred_away_ml)
        pred_away_ml = "+" + pred_away_ml if pred_away_ml[0] in string.digits else pred_away_ml
        pred_ml_msg = f"{pred_home_ml}, {pred_away_ml}"

        pdf.set_text_color(r=128, g=128, b=128)
        pdf.set_xy(106, depth + 13)
        pdf.cell(w=22, h=8, txt=pred_ml_msg, border=1, align="C")
        pdf.set_text_color(r=0, g=0, b=0)
        return pdf

    def _add_predicted_lines(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        pred_home_line = row['Pred_Home_Line']
        pred_away_line = row['Pred_Away_Line']
        line_msg = f"{pred_home_line}, {pred_away_line}"

        pdf.set_text_color(r=128, g=128, b=128)
        pdf.set_xy(128, depth + 13)
        pdf.cell(w=33, h=8, txt=line_msg, border=1, align="C")
        pdf.set_text_color(r=0, g=0, b=0)
        return pdf

    def _add_predicted_over_under(self, pdf, row, depth):  # Helping Helper _add_nfl_game
        pred_over_under = row['Pred_SB_Over_Under']
        pred_over_under = round(pred_over_under * 2) / 2  # rounding to nearest 0.5
        pred_over_under = int(pred_over_under) if int(pred_over_under) == pred_over_under else pred_over_under
        msg = f"O/U {pred_over_under}"

        pdf.set_text_color(r=128, g=128, b=128)
        pdf.set_xy(161, depth + 13)
        pdf.cell(w=37, h=8, txt=msg, border=1, align="C")
        pdf.set_text_color(r=0, g=0, b=0)
        return pdf

    def _add_nfl_game(self, pdf, row, num_games):  # Specific Helper create_nfl_page
        depth = (33 * num_games) - 15
        pdf = self._add_image(pdf, row, depth, "NFL")
        pdf = self._add_records(pdf, row, depth)
        pdf = self._add_game_cell(pdf, depth)
        pdf = self._add_game_info(pdf, row, depth, "NFL")
        pdf = self._add_team_names(pdf, row, depth)
        pdf = self._add_moneylines(pdf, row, depth)
        pdf = self._add_lines(pdf, row, depth)
        pdf = self._add_over_unders(pdf, row, depth)
        pdf = self._add_predicted_score(pdf, row, depth)
        pdf = self._add_predicted_ml(pdf, row, depth)
        pdf = self._add_predicted_lines(pdf, row, depth)
        pdf = self._add_predicted_over_under(pdf, row, depth)
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

    def _add_nba_game(self, pdf, row, num_games):  # Specific Helper create_nba_page
        depth = (33 * num_games) - 15
        pdf = self._add_image(pdf, row, depth, "NBA")
        pdf = self._add_records(pdf, row, depth)
        pdf = self._add_game_cell(pdf, depth)
        pdf = self._add_game_info(pdf, row, depth, "NBA")
        pdf = self._add_team_names(pdf, row, depth)
        pdf = self._add_moneylines(pdf, row, depth)
        pdf = self._add_lines(pdf, row, depth)
        pdf = self._add_over_unders(pdf, row, depth)
        pdf = self._add_predicted_score(pdf, row, depth)
        pdf = self._add_predicted_ml(pdf, row, depth)
        pdf = self._add_predicted_lines(pdf, row, depth)
        pdf = self._add_predicted_over_under(pdf, row, depth)
        return pdf

    def create_nba_page(self, pdf):  # Top Level
        pdf.add_page()
        df = self.load_data("NBA")
        num_games = 1
        for i, row in df.iterrows():
            pdf = self._add_nba_game(pdf, row, num_games)
            num_games += 1
            if num_games == 9:
                pdf.add_page()
                num_games = 1
        return pdf

    def create_ncaaf_page(self, pdf):  # Top Level
        pass

    def create_ncaab_page(self, pdf):  # Top Level
        pass

    def save_pdf(self, pdf):  # Top Level
        pdf.output(self.pdf_path, 'F').encode('utf-8', 'ignore')

    def email_pdf(self):  # Top Level
        msg = EmailMessage()
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        msg['Subject'] = f"{date_str} Betting Lines"
        msg['From'] = 'emailsfrompython3@gmail.com'
        msg['To'] = ['dillonk428@gmail.com']
        msg.set_content("Today's Betting PDF")

        with open(self.pdf_path, 'rb') as f:
            file_data = f.read()
            file_name = f.name
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        port = 465
        smtp_server = "smtp.gmail.com"
        sender_email = "emailsfrompython3@gmail.com"
        password = "QBface!$"
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(msg)

        print("Email sent!")

    def run(self):  # Run
        pdf = FPDF()
        pdf.add_page()
        pdf = self.create_nba_page(pdf)
        pdf = self.create_nfl_page(pdf)
        self.save_pdf(pdf)
        # self.email_pdf()
        return pdf


if __name__ == "__main__":
    x = PDF()
    self = x
    x.run()
