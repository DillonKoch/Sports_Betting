##############
import tkinter as tk


class Bet:
    def __init__(self):
        self.root = tk.Tk()
        self.person = tk.StringVar()
        self.bet_type = None
        self.amount = None
        self.league = None
        self.ml = None

        self.bettors = ['Dillon', 'Colin', 'Todd', 'Clay', 'Sal']
        self.bet_types = ['Money Line', 'Spread', 'Prop']

    def create_bettor_radio_buttons(self, root, name):
        button = tk.Radiobutton(root, text=name, padx=20, variable=self.person, value=name)
        button.pack(anchor=tk.W)

    def create_bettor_button(self, root, name_var):
        button = tk.Button(root, text=name_var, width=15, command=lambda: self.store_person(name_var))
        button.pack(side=tk.LEFT)

    def store_person(self, name_var):
        self.person = name_var
        print(self.person)

    def create_bet_type_button(self, root, bet_type):
        button = tk.Button(root, text=bet_type, width=25, command=lambda: self.store_bet_type(bet_type))
        button.pack(side=tk.RIGHT)

    def store_bet_type(self, bet_type):
        self.bet_type = bet_type
        print(bet_type)

    def create_buttons(self, root):
        # bettor buttons
        for bettor in self.bettors:
            self.create_bettor_button(root, bettor)

        # bet type buttons
        for bet_type in self.bet_types:
            self.create_bet_type_button(root, bet_type)

    def run_tk(self):
        self.create_buttons(self.root)
        self.root.mainloop()


if __name__ == '__main__':
    x = Bet()
    x.run_tk()
