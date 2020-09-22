# ==============================================================================
# File: esb_general_scraper.py
# Project: ESB
# File Created: Friday, 18th September 2020 3:00:34 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 22nd September 2020 4:31:16 pm
# Modified By: Dillon Koch
# -----
#
# -----
# ESB scraper that operates in such a general way it can scrape all types of bets
# ==============================================================================


import datetime
import pickle
import re
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.merge_odds_dfs import merge_odds_dfs

# try:
#     print(hp)
# except BaseException:
#     with open('esb_sp_list.pickle', 'rb') as f:
#         data = pickle.load(f)

#     sps = [item[2] for item in data]

#     titles = [item[0] for item in data]
#     events = [item[1] for item in data]

#     for i, (title, event) in enumerate(zip(titles, events)):
#         print(f"{i} - {title} - {event}")


def mfloat(val):
    if val is None:
        return None
    else:
        return float(val)


class ESB_General_Scraper:
    def __init__(self, league):
        self.league = league

    def _get_scrape_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def detect_no_events_warning(self, sp):  # Global Helper
        """
        detects the presence of a no events warning
        """
        warning = sp.find_all('div', attrs={'class': 'alert alert-warning no-events'})
        return True if len(warning) > 0 else False

    def _detect_game_titles(self, sp):  # Specific Helper detect_bet_types
        """
        detects whether the sp has game titles or not (Moneyline, Spread, Totals)
        """
        money_total = sp.find_all('div', attrs={'class': 'column money header-row pull-right'})
        spread = sp.find_all('div', attrs={'class': 'column spread header-row pull-right'})  # can also be used, isn't atm
        return True if len(money_total) == 2 else False

    def _detect_event_headings(self, sp):  # Specific Helper detect_bet_types
        """
        detects whether the sp has headers that show up above game props
        - "Rams vs Eagles | First Half Lines" for example
        """
        headings = sp.find_all('div', attrs={'class': 'row event eventheading'})
        return True if len(headings) > 0 else False

    def detect_bet_type(self, sp):  # Top Level
        """
        detects the type of bet the sp is for (Game_Lines, Game_Props, Futures) to decide
        which scraping code to use
        - if the bet has no events, it'll be shown as a future (even if it's not when bets are populated)
        """
        if self._detect_game_titles(sp):
            if self._detect_event_headings(sp):
                return 'Game_Props'
            else:
                return 'Game_Lines'
        else:
            return 'Futures'

    def _game_lines_df(self):  # Specific Helper scrape_game_lines
        """
        creates empty game lines df
        """
        cols = ['Title', 'datetime', 'Game_Time', 'Home', 'Away',
                'Over_ESB', 'Over_ml_ESB', 'Under_ESB', 'Under_ml_ESB',
                'Home_Line_ESB', 'Home_Line_ml_ESB', 'Away_Line_ESB', 'Away_Line_ml_ESB',
                'Home_ML_ESB', 'Away_ML_ESB',
                'scraped_ts']
        return pd.DataFrame(columns=cols)

    def _get_date_events(self, sp):  # Specific Helper scrape_game_lines, scrape_game_props
        """
        finds the date_event items in the original sp
        - the item can either be a date (September 29, 2020) or an actual event (game)
        """
        event_sp = sp.find_all('div', attrs={'class': 'row event'})[0]
        date_events = event_sp.find_all('div', attrs={'class': ['row event', 'col-xs-12 date']})
        return date_events

    def _check_is_date(self, date_event, date):  # Specific Helper scrape_game_lines, scrape_game_props
        found_date = False
        date_comp = re.compile(
            r"^(January|February|March|April|June|July|August|September|October|November|December|) \d{1,2}, \d{4}$")

        full_text = date_event.get_text()
        match = re.match(date_comp, full_text)
        if match:
            date = datetime.datetime.strptime(full_text, "%B %d, %Y")
            found_date = True

        if date is None:
            raise ValueError("Did not find a date before games!")

        return date, found_date

    def _game_time(self, event):  # Helping Helper _date_event_to_row
        """
        finds the game time of an event
        """
        time = event.find_all('div', attrs={'id': 'time'})
        time = time[0].get_text()
        return time

    def _teams(self, event):  # Helping Helper _date_event_to_row
        """
        finds the home and away teams in an event
        """
        away = event.find_all('span', attrs={'id': 'firstTeamName'})
        away = away[0].get_text()
        home = event.find_all('span', attrs={'id': 'secondTeamName'})
        home = home[0].get_text()
        # TODO assert these are in valid league teams
        return home, away

    def _moneylines(self, event):  # Helping Helper _date_event_to_row
        """
        finds the home/away moneylines of an event
        - the html of ESB labels the totals as moneylines and moneylines as totals
        """
        moneylines = event.find_all('div', attrs={'class': 'column total pull-right'})
        away_text, home_text = [item.get_text().strip() for item in moneylines]
        ml_comp = re.compile(r"(((\+|-)\d+)|(even))")

        away_match = re.match(ml_comp, away_text)
        away_ml = away_match.group(1) if away_match is not None else None

        home_match = re.match(ml_comp, home_text)
        home_ml = home_match.group(1) if home_match is not None else None

        home_ml = '100' if home_ml == 'even' else home_ml
        away_ml = '100' if away_ml == 'even' else away_ml

        return mfloat(home_ml), mfloat(away_ml)

    def _spreads(self, event):  # Helping Helper _date_event_to_row
        """
        finds the home/away spread/spread_ml of an event
        """
        spreads = event.find_all('div', attrs={'class': 'column spread pull-right'})
        away_text, home_text = [item.get_text().strip() for item in spreads]
        spread_comp = re.compile(r"^((\+|-)?\d+\.?\d?)\((((\+|-)\d+)|(even))\)$")

        away_match = re.match(spread_comp, away_text)
        if away_match is None:
            print(f"No spread match for {away_text}")
            away_spread = None
            away_spread_ml = None
        else:
            away_spread = away_match.group(1)
            away_spread_ml = away_match.group(3)

        home_match = re.match(spread_comp, home_text)
        if home_match is None:
            print(f"No spread match for {home_text}")
            home_spread = None
            home_spread_ml = None
        else:
            home_spread = home_match.group(1)
            home_spread_ml = home_match.group(3)

        home_spread_ml = '100' if home_spread_ml == 'even' else home_spread_ml
        away_spread_ml = '100' if away_spread_ml == 'even' else away_spread_ml

        return mfloat(home_spread), mfloat(home_spread_ml), mfloat(away_spread), mfloat(away_spread_ml)

    def _totals(self, event):  # Helping Helper _date_event_to_row
        """
        finds the over/under totals for an event
        the html of ESB labels the totals as moneylines and moneylines as totals
        """
        totals = event.find_all('div', attrs={'class': 'column money pull-right'})
        over_text, under_text = [item.get_text().strip() for item in totals]
        total_comp = re.compile(r"(O|U) (\d+\.?\d?)\((((\+|-)\d+)|(even))\)")

        over_match = re.match(total_comp, over_text)
        if over_match is None:
            print(f"No over match for {over_text}")
            over = None
            over_ml = None
        else:
            over = over_match.group(2)
            over_ml = over_match.group(3)

        under_match = re.match(total_comp, under_text)
        if under_match is None:
            print(f"No under match for {under_text}")
            under = None
            under_ml = None
        else:
            under = under_match.group(2)
            under_ml = under_match.group(3)

        over_ml = '100' if over_ml == 'even' else over_ml
        under_ml = '100' if under_ml == 'even' else under_ml

        return mfloat(over), mfloat(over_ml), mfloat(under), mfloat(under_ml)

    def _date_event_to_row(self, date_event, date):  # Specific Helper scrape_game_lines
        """
        transforms the HTML of a date_event into a new row in the game_lines df
        - also requires 'date', the day the event happens (not in the date_event HTML)
        """
        scraped_ts = self._get_scrape_ts()

        game_time = self._game_time(date_event)
        home, away = self._teams(date_event)
        home_ml, away_ml = self._moneylines(date_event)
        home_spread, home_spread_ml, away_spread, away_spread_ml = self._spreads(date_event)
        over, over_ml, under, under_ml = self._totals(date_event)

        row = ['Full Game', date, game_time, home, away,
               over, over_ml, under, under_ml,
               home_spread, home_spread_ml, away_spread, away_spread_ml,
               home_ml, away_ml,
               scraped_ts]
        return row

    def scrape_game_lines(self, sp):  # Top Level
        """
        scrapes the game lines of a game line event's sp
        - whole process from sp -> df
        """
        df = self._game_lines_df()
        date_events = self._get_date_events(sp)

        date = None
        for date_event in date_events:
            # if date_event is a date, update 'date' and move to next iteration
            date, found_date = self._check_is_date(date_event, date)
            if found_date:
                continue

            row = self._date_event_to_row(date_event, date)
            df.loc[len(df)] = row
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df

    def _game_props_df(self):  # Specific Helper scrape_game_props
        """
        empty df for recording game props
        """
        cols = ['datetime', 'Game_Time', 'Home', 'Away', 'Title', 'Description', 'Bet',
                'Spread/overunder', 'Odds', 'scraped_ts']
        return pd.DataFrame(columns=cols)

    def _page_title(self, sp):  # Specific Helper scrape_game_props, scrape_futures
        """
        finds the title of game props and futures bets
        """
        title = sp.find_all('span', attrs={'class': 'titleLabel'})
        title = title[0].get_text()
        return title

    def _description(self, date_event):  # Helping Helper _update_game_prop_df
        """
        finds the description of a game prop
        """
        desc = date_event.find_all('div', attrs={'class': 'row event eventheading'})
        return desc[0].get_text().strip()

    def _update_game_prop_df(self, df, date_event, date, title):  # Specific Helper scrape_game_props
        """
        updates a running game_prop_df with new bets found in a date_event section in scrape_game_props
        """
        scraped_ts = self._get_scrape_ts()

        gt = self._game_time(date_event)
        desc = self._description(date_event)
        home, away = self._teams(date_event)
        home_ml, away_ml = self._moneylines(date_event)
        home_spread, home_spread_ml, away_spread, away_spread_ml = self._spreads(date_event)
        over, over_ml, under, under_ml = self._totals(date_event)

        # add home/away ML
        home_ml_row = [date, gt, home, away, title, desc, home, None, home_ml, scraped_ts]
        away_ml_row = [date, gt, home, away, title, desc, away, None, away_ml, scraped_ts]

        # add home/away spread
        home_spread_row = [date, gt, home, away, title, desc, home, home_spread, home_spread_ml, scraped_ts]
        away_spread_row = [date, gt, home, away, title, desc, away, away_spread, away_spread_ml, scraped_ts]

        # add over/under
        over_row = [date, gt, home, away, title, desc, "Over", over, over_ml, scraped_ts]
        under_row = [date, gt, home, away, title, desc, "Under", under, under_ml, scraped_ts]

        for row in [home_ml_row, away_ml_row, home_spread_row, away_spread_row, over_row, under_row]:
            df.loc[len(df)] = row

        return df

    def scrape_game_props(self, sp):  # Top Level
        """
        scrapes all the game props on an ESB page from sp -> df
        """
        df = self._game_props_df()
        date_events = self._get_date_events(sp)
        title = self._page_title(sp)

        date = None
        for date_event in date_events:
            date, found_date = self._check_is_date(date_event, date)
            if found_date:
                continue

            df = self._update_game_prop_df(df, date_event, date, title)
        df = df.loc[df['Odds'].notnull()]
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df

    def _futures_df(self):  # Specific Helper scrape_futures
        """
        empty dataframe for recording futures bets
        """
        cols = ['Title', 'Description', 'Bet', 'Odds', 'scraped_ts']
        return pd.DataFrame(columns=cols)

    def _futures_description(self, sp):  # Specific Helper scrape_futures
        """
        finds the description for futures bets
        """
        desc = sp.find_all('div', attrs={'id': 'futureDescription'})
        desc = desc[0].get_text()
        desc = desc.replace('\t', '').replace('\n', '')
        return desc

    def _futures_bet_odds_pairs(self, sp):  # Specific Helper scrape_futures
        """
        finds the bet-odd pairs for futures bets (e.g. [("Vikings", 250), ("Jets", 500), ..])
        - sometimes "Selection" shows up as a bet so I get rid of that if it's there
        """
        bets = sp.find_all('span', attrs={'class': 'team'})
        bets = [item.get_text() for item in bets]
        bets = [item for item in bets if item != 'Selection']  # "Selection" shows up for bets sometimes

        odds = sp.find_all('div', attrs={'class': 'market'})
        odds = [item.get_text() for item in odds]
        odds = [100 if item == 'even' else mfloat(item) for item in odds]

        pairs = [(bet, odd) for bet, odd in zip(bets, odds)]
        return pairs

    def _futures_add_pairs(self, df, bet_odds_pairs, title, desc):  # Specific Helper scrape_futures
        """
        uses the df, title, and description to add all the bet_odds_pairs to the dataframe
        """
        scraped_ts = self._get_scrape_ts()

        for pair in bet_odds_pairs:
            bet, odd = pair
            new_row = [title, desc, bet, odd, scraped_ts]
            df.loc[len(df)] = new_row
        return df

    def scrape_futures(self, sp):  # Top Level
        """
        scrapes a futures bet from sp -> df
        """
        df = self._futures_df()
        main = sp.find_all('div', attrs={'id': 'main-content'})[0]

        panels = main.find_all('div', attrs={'class': 'panel panel-primary'})
        for panel in panels:
            if self.detect_no_events_warning(panel):
                continue

            title = self._page_title(panel)
            desc = self._futures_description(panel)
            bet_odds_pairs = self._futures_bet_odds_pairs(panel)
            df = self._futures_add_pairs(df, bet_odds_pairs, title, desc)
        return df

    def _load_existing_df(self, bet_type):  # Specific Helper add_new_df
        """
        loads the existing df if it exists, or returns None if there isn't one
        - changes Odds to be a float and datetime to datetime type to help with removing repeats
        """
        path = ROOT_PATH + f"/ESB/Data/{self.league}/{bet_type}.csv"
        try:
            df = pd.read_csv(path)
            if 'Odds' in list(df.columns):
                df['Odds'] = df['Odds'].astype(float)
            if 'datetime' in list(df.columns):
                df['datetime'] = pd.to_datetime(df['datetime'])
        except FileNotFoundError:
            print(f"No existing df found for {path}, making a new one!")
            return None
        return df

    def add_new_df(self, df, bet_type):  # Top Level
        """
        adds the newly scraped df to the existing one and saves it
        - or saves the newly scraped df if one doesn't exist yet
        """
        df_path = ROOT_PATH + f"/ESB/Data/{self.league}/{bet_type}.csv"
        existing_df = self._load_existing_df(bet_type)
        if existing_df is None:
            df.to_csv(df_path, index=None)
            return df

        all_drop_cols = ['Title', 'Description', 'Bet', 'Game_Time', 'Home', 'Away', 'datetime']
        drop_cols = [col for col in list(df.columns) if col in all_drop_cols]
        odds_cols = [col for col in list(df.columns) if col != "scraped_ts"]
        full_df = merge_odds_dfs(existing_df, df, drop_cols, odds_cols)
        full_df.to_csv(df_path, index=None)
        return full_df

    def run(self, sp):  # Run
        main = sp.find_all('div', attrs={'id': 'main-content'})[0]
        bet_type = self.detect_bet_type(main)
        print(bet_type)

        if bet_type == 'Game_Lines':
            df = self.scrape_game_lines(sp)
        elif bet_type == 'Game_Props':
            df = self.scrape_game_props(sp)
        elif bet_type == 'Futures':
            df = self.scrape_futures(sp)
        else:
            raise ValueError("Unknown bet_type: {}".format(bet_type))

        full_df = self.add_new_df(df, bet_type)
        print("Data saved!")
        return full_df


if __name__ == '__main__':
    x = ESB_General_Scraper("NFL")
    self = x
    hp = True
    # x.run()

    # for sp in sps:
    #     x.run(sp)
