# ==============================================================================
# File: create_pdf.py
# Project: Results
# File Created: Sunday, 19th July 2020 5:26:27 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 19th July 2020 7:12:08 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File to create a PDF of bets and predictions for upcoming games in each league
# ==============================================================================

from os.path import abspath, dirname
import sys
import datetime

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from fpdf import FPDF


class PDF:
    def __init__(self):
        self.date_str = datetime.date.today().strftime("%Y_%m_%d")
        self.pdf_path = ROOT_PATH + "/Results/PDFs/{}_Bets.pdf".format(self.date_str)

    def create_recap_page(self, pdf):  # Top Level
        pass

    def create_bet_history_page(self, pdf):  # Top Level
        pass

    def create_nfl_page(self, pdf):  # Top Level
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
