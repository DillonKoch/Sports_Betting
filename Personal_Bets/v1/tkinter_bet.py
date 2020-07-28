import tkinter as tk

import pandas as pd


class Tkinter_Bet:
    def __init__(self):
        self.root = tk.Tk()
        self.font = 'bitstream charter'
        self.font_size = 18

        # vars about the current bet
        self.person = tk.StringVar()
        self.person.set('nobody')
        self.bet_type = tk.StringVar()
        self.bet_type.set('no bet')
        self.bet_amount = tk.DoubleVar()
        self.bet_amount.set(0.0)
        self.to_win_amount = tk.DoubleVar()
        self.to_win_amount.set(0.0)
        self.league = tk.StringVar()
        self.league.set('no league')
        self.spread = tk.DoubleVar()
        self.spread.set(100.0)

        # lists
        self.bettors = ['Dillon']
        self.bet_types = ['Money Line', 'Spread', 'Prop']
        self.bet_amounts = [float(item) for item in [5, 10, 25, 50, 75, 100, 125,
                                                     150, 175, 200, 225, 250, 300, 400, 500, 600]]
        self.to_win_amounts = [float(item) for item in [4.55, 25, 50, 75, 100, 125,
                                                        150, 175, 200, 225, 250, 300, 400, 500, 600, 1000]]
        self.leagues = ['NFL', 'NCAAF', 'NBA', 'NCAAB', 'XFL', 'MLB', 'NHL', 'Soccer']
        positive_spreads = [2, 2.5, 3, 3.5, 4, 6, 6.5, 7, 10]
        self.spreads = sorted(list(set([float(-item) for item in positive_spreads] + positive_spreads)))

    def create_bettors_radio(self, bettor, row):
        button = tk.Radiobutton(self.root, text=bettor, padx=10, pady=12, font=(
            self.font, self.font_size, 'bold'), variable=self.person, value=bettor, indicatoron=0, width=7)
        button.grid(row=row, column=0)

    def create_bet_type_radio(self, bet_type, row):
        button = tk.Radiobutton(self.root, text=bet_type, padx=10, pady=12, font=(self.font, self.font_size, 'bold'),
                                variable=self.bet_type, value=bet_type, indicatoron=0, width=10)
        button.grid(row=row, column=1)

    def create_bet_amount_buttons(self, amount, row):
        amount_value = int(amount) if amount == int(amount) else float(amount)
        amount_value = '$' + str(amount_value)
        button = tk.Radiobutton(self.root, text=amount_value, padx=10, pady=12, font=(self.font, self.font_size, 'bold'),
                                variable=self.bet_amount, value=amount, indicatoron=0, width=7)
        button.grid(row=row, column=2)

    def create_to_win_amount_buttons(self, amount, row):
        amount_value = int(amount) if amount == int(amount) else float(amount)
        amount_value = '$' + str(amount_value)
        button = tk.Radiobutton(self.root, text=amount_value, padx=10, pady=12, font=(self.font, self.font_size, 'bold'),
                                variable=self.to_win_amount, value=amount, indicatoron=0, width=7)
        button.grid(row=row, column=3)

    def create_league_buttons(self, league, row):
        button = tk.Radiobutton(self.root, text=league, padx=10, pady=12, font=(self.font, self.font_size, 'bold'),
                                variable=self.league, value=league, indicatoron=0, width=7)
        button.grid(row=row, column=4)

    def create_spread_buttons(self, spread, row):
        spread_value = int(spread) if spread == int(spread) else float(spread)

        button = tk.Radiobutton(self.root, text=spread_value, padx=10, pady=12, font=(
                                self.font, self.font_size, 'bold'), variable=self.spread, value=spread, indicatoron=0, width=7)
        button.grid(row=row, column=5)

    def create_all_buttons(self):
        # populate bettors
        for i, bettor in enumerate(self.bettors):
            self.create_bettors_radio(bettor, i)
        # populate bet types
        for i, bet_type in enumerate(self.bet_types):
            self.create_bet_type_radio(bet_type, i)
        # bet amounts
        for i, bet_amount in enumerate(self.bet_amounts):
            self.create_bet_amount_buttons(bet_amount, i)
        # to win amounts
        for i, to_win_amount in enumerate(self.to_win_amounts):
            self.create_to_win_amount_buttons(to_win_amount, i)
        # leagues
        for i, league in enumerate(self.leagues):
            self.create_league_buttons(league, i)
        # spread
        for i, spread in enumerate(self.spreads):
            self.create_spread_buttons(spread, i)

    def export_bet(self):
        df = pd.DataFrame(columns=['Person', 'Bet_Type', 'Amount', 'To_Win', 'League'])
        df.loc[len(df)] = [self.person.get(), self.bet_type.get(),
                           self.bet_amount.get(), self.to_win_amount.get(), self.league.get()]
        return df

    def run(self):
        self.create_all_buttons()
        self.root.mainloop()
        print(self.person.get())
        print(self.bet_type.get())
        print(self.bet_amount.get())
        print(self.to_win_amount.get())
        print(self.league.get())
        df = self.export_bet()
        return df

    def test_fonts(self):
        fonts = ['fangsong ti', 'fixed', 'clearlyu alternate glyphs', 'courier 10 pitch',
                 'open look glyph', 'bitstream charter', 'song ti', 'open look cursor', 'newspaper',
                 'clearlyu ligature', 'mincho', 'clearlyu devangari extra', 'clearlyu pua',
                 'clearlyu', 'clean', 'nil', 'clearlyu arabic', 'clearlyu devanagari', 'gothic',
                 'clearlyu arabic extra']
        root = tk.Tk()
        for i, font in enumerate(fonts):
            label = tk.Label(root, text="$5 " + str(font), font=(font, 18, 'bold'))
            label.grid(row=i, column=0)
        root.mainloop()


if __name__ == '__main__':
    x = Tkinter_Bet()
    df = x.run()
