# ==============================================================================
# File: esb_parser.py
# Project: ESB
# File Created: Saturday, 17th October 2020 8:05:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 22nd October 2020 8:18:57 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Elite Sportsbook BeautifulSoup parser
# * BeautifulSoup sp is found in esb_navigator.py, passed to this class for parsing
# ==============================================================================

import os
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


def mfloat(val):
    if val is None:
        return None
    else:
        return float(val)


class ESB_Parser:
    def __init__(self):
        pass

    def _get_scrape_ts(self):  # Global Helper  Tested
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def detect_no_events_warning(self, sp):  # Global Helper  Tested
        """
        detects the presence of a no events warning
        """
        warning = sp.find_all('div', attrs={'class': 'alert alert-warning no-events'})
        has_warning = True if len(warning) > 0 else False
        return has_warning

    def _detect_game_titles(self, sp):  # Specific Helper detect_bet_types  Tested
        """
        detects whether the sp has game titles or not (Moneyline, Spread, Totals)
        """
        money_total = sp.find_all('div', attrs={'class': 'column money header-row pull-right'})
        spread = sp.find_all('div', attrs={'class': 'column spread header-row pull-right'})  # can also be used, isn't atm
        return True if len(money_total) == 2 else False

    def _detect_event_headings(self, sp):  # Specific Helper detect_bet_types  Tested
        """
        detects whether the sp has headers that show up above game props
        - "Rams vs Eagles | First Half Lines" for example
        """
        headings = sp.find_all('div', attrs={'class': 'row event eventheading'})
        return True if len(headings) > 0 else False

    def detect_bet_type(self, sp):  # Top Level  Tested
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

    def _game_lines_df(self):  # Specific Helper scrape_game_lines  Tested
        """
        creates empty game lines df
        """
        cols = ['Title', 'datetime', 'Game_Time', 'Home', 'Away',
                'Over_ESB', 'Over_ml_ESB', 'Under_ESB', 'Under_ml_ESB',
                'Home_Line_ESB', 'Home_Line_ml_ESB', 'Away_Line_ESB', 'Away_Line_ml_ESB',
                'Home_ML_ESB', 'Away_ML_ESB',
                'scraped_ts']
        return pd.DataFrame(columns=cols)

    def _get_date_events(self, sp):  # Specific Helper scrape_game_lines, scrape_game_props  Tested
        """
        finds the date_event items in the original sp
        - the item can either be a date (September 29, 2020) or an actual event (game)
        """
        event_sp = sp.find_all('div', attrs={'class': 'row event'})[0]
        date_events = event_sp.find_all('div', attrs={'class': ['row event', 'col-xs-12 date']})
        return date_events

    def _check_is_date(self, date_event, date):  # Specific Helper scrape_game_lines, scrape_game_props  Tested
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

    def _game_time(self, event):  # Helping Helper _date_event_to_row  Tested
        """
        finds the game time of an event
        """
        time = event.find_all('div', attrs={'id': 'time'})
        time = time[0].get_text()
        time_comp = re.compile(r"\d{2}:\d{2} C(S|D)T")
        match = re.search(time_comp, time)
        return match.group(0) if match is not None else None

    def _teams(self, event):  # Helping Helper _date_event_to_row  Tested
        """
        finds the home and away teams in an event
        """
        away = event.find_all('span', attrs={'id': ['firstTeamName', 'awayTeamName']})
        away = away[0].get_text()
        home = event.find_all('span', attrs={'id': ['secondTeamName', 'homeTeamName']})
        home = home[0].get_text()
        tie = event.find_all('span', attrs={'id': 'tie'})
        tie = tie[0].get_text() if len(tie) > 0 else None
        # TODO assert these are in valid league teams
        return home, away, tie

    def _moneylines_match(self, text):  # Helping Helper _moneylines  Tested
        ml_comp = re.compile(r"(((\+|-)\d+)|(even))")
        match = re.match(ml_comp, text)

        if match is None:
            print("No match for ", text)
            return None
        else:
            ml = match.group(1)
            return ml

    def _moneylines(self, event):  # Helping Helper _date_event_to_row  Tested
        """
        finds the home/away moneylines of an event
        - the html of ESB labels the totals as moneylines and moneylines as totals
        """
        moneylines = event.find_all('div', attrs={'class': 'column total pull-right'})
        ml_texts = [item.get_text().strip() for item in moneylines]
        away_text = ml_texts[0]
        home_text = ml_texts[1]
        tie_text = ml_texts[2] if len(ml_texts) >= 3 else None

        away_ml = self._moneylines_match(away_text)
        home_ml = self._moneylines_match(home_text)
        tie_ml = self._moneylines_match(tie_text) if tie_text is not None else None

        home_ml = '100' if home_ml == 'even' else home_ml
        away_ml = '100' if away_ml == 'even' else away_ml
        tie_ml = '100' if tie_ml == 'even' else tie_ml
        return mfloat(home_ml), mfloat(away_ml), mfloat(tie_ml)

    def _spreads_match(self, text):  # Helping Helper _spreads  Tested
        spread_comp = re.compile(r"^((\+|-)?\d+\.?\d?)\((((\+|-)\d+)|(even))\)$")
        match = re.match(spread_comp, text)
        if match is None:
            print("No match for ", text)
            return None, None
        else:
            spread = match.group(1)
            spread_ml = match.group(3)
            return spread, spread_ml

    def _spreads(self, event):  # Helping Helper _date_event_to_row  Tested
        """
        finds the home/away spread/spread_ml of an event
        """
        spreads = event.find_all('div', attrs={'class': 'column spread pull-right'})
        if len(spreads) == 0:
            return tuple([None] * 6)
        spreads_texts = [item.get_text().strip() for item in spreads]
        away_text = spreads_texts[0]
        home_text = spreads_texts[1]
        tie_text = spreads_texts[2] if len(spreads_texts) >= 3 else None

        away_spread, away_spread_ml = self._spreads_match(away_text)
        home_spread, home_spread_ml = self._spreads_match(home_text)
        tie_spread, tie_spread_ml = self._spreads_match(tie_text) if tie_text is not None else None, None

        home_spread_ml = '100' if home_spread_ml == 'even' else home_spread_ml
        away_spread_ml = '100' if away_spread_ml == 'even' else away_spread_ml
        tie_spread_ml = '100' if tie_spread_ml == 'even' else tie_spread_ml

        return (mfloat(home_spread), mfloat(home_spread_ml), mfloat(away_spread), mfloat(away_spread_ml),
                mfloat(tie_spread), mfloat(tie_spread_ml))

    def _totals_match(self, text):  # Helping Helper _totals  Tested
        total_comp = re.compile(r"(O|U) (\d+\.?\d?)\((((\+|-)\d+)|(even))\)")
        match = re.search(total_comp, text)
        if match is None:
            print("No match for ", text)
            return (None, None)
        else:
            total = match.group(2)
            ml = match.group(3)
            return total, ml

    def _totals(self, event):  # Helping Helper _date_event_to_row  Tested
        """
        finds the over/under totals for an event
        the html of ESB labels the totals as moneylines and moneylines as totals
        """
        totals = event.find_all('div', attrs={'class': 'column money pull-right'})
        totals_texts = [item.get_text().strip() for item in totals]
        over_text = totals_texts[0]
        under_text = totals_texts[1]
        tie_text = totals_texts[2] if len(totals_texts) >= 3 else None

        over, over_ml = self._totals_match(over_text)
        under, under_ml = self._totals_match(under_text)
        tie, tie_ml = (None, None) if tie_text is None else self._totals_match(tie_text)

        over_ml = '100' if over_ml == 'even' else over_ml
        under_ml = '100' if under_ml == 'even' else under_ml
        tie_ml = '100' if tie_ml == 'even' else tie_ml
        return mfloat(over), mfloat(over_ml), mfloat(under), mfloat(under_ml), mfloat(tie), mfloat(tie_ml)

    def _date_event_to_row(self, date_event, date):  # Specific Helper scrape_game_lines  Tested
        """
        transforms the HTML of a date_event into a new row in the game_lines df
        - also requires 'date', the day the event happens (not in the date_event HTML)
        """
        scraped_ts = self._get_scrape_ts()

        game_time = self._game_time(date_event)
        home, away, _ = self._teams(date_event)
        home_ml, away_ml, _ = self._moneylines(date_event)
        home_spread, home_spread_ml, away_spread, away_spread_ml, _, _ = self._spreads(date_event)
        over, over_ml, under, under_ml, _, _ = self._totals(date_event)

        row = ['Full Game', date, game_time, home, away,
               over, over_ml, under, under_ml,
               home_spread, home_spread_ml, away_spread, away_spread_ml,
               home_ml, away_ml,
               scraped_ts]
        return row

    def scrape_game_lines(self, sp):  # Top Level  Tested
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

    def _game_props_df(self):  # Specific Helper scrape_game_props  Tested
        """
        empty df for recording game props
        """
        cols = ['datetime', 'Game_Time', 'Home', 'Away', 'Title', 'Description', 'Bet',
                'Spread/overunder', 'Odds', 'scraped_ts']
        return pd.DataFrame(columns=cols)

    def _page_title(self, sp):  # Specific Helper scrape_game_props, scrape_futures  Tested
        """
        finds the title of game props and futures bets
        """
        title = sp.find_all('span', attrs={'class': 'titleLabel'})
        title = title[0].get_text()
        return title

    def _description(self, date_event):  # Helping Helper _update_game_prop_df  Tested
        """
        finds the description of a game prop
        """
        desc = date_event.find_all('div', attrs={'class': 'row event eventheading'})
        return desc[0].get_text().strip()

    def _update_game_prop_df(self, df, date_event, date, title):  # Specific Helper scrape_game_props  Tested
        """
        updates a running game_prop_df with new bets found in a date_event section in scrape_game_props
        """
        scraped_ts = self._get_scrape_ts()

        gt = self._game_time(date_event)
        desc = self._description(date_event)
        home, away, tie = self._teams(date_event)
        home_ml, away_ml, tie_ml = self._moneylines(date_event)
        home_spread, home_spread_ml, away_spread, away_spread_ml, tie_spread, tie_spread_ml = self._spreads(date_event)
        over, over_ml, under, under_ml, tie, tie_ml = self._totals(date_event)

        # add home/away ML
        home_ml_row = [date, gt, home, away, title, desc, home, None, home_ml, scraped_ts]
        away_ml_row = [date, gt, home, away, title, desc, away, None, away_ml, scraped_ts]
        tie_ml_row = [date, gt, home, away, title, desc, away, None, tie_ml, scraped_ts]

        # add home/away spread
        home_spread_row = [date, gt, home, away, title, desc, home, home_spread, home_spread_ml, scraped_ts]
        away_spread_row = [date, gt, home, away, title, desc, away, away_spread, away_spread_ml, scraped_ts]
        tie_spread_row = [date, gt, home, away, title, desc, away, tie_spread, tie_spread_ml, scraped_ts]

        # add over/under
        over_row = [date, gt, home, away, title, desc, "Over", over, over_ml, scraped_ts]
        under_row = [date, gt, home, away, title, desc, "Under", under, under_ml, scraped_ts]
        tie_total_row = [date, gt, home, away, title, desc, "Tie", tie, tie_ml, scraped_ts]

        for row in [home_ml_row, away_ml_row, tie_ml_row,
                    home_spread_row, away_spread_row, tie_spread_row,
                    over_row, under_row, tie_total_row]:
            df.loc[len(df)] = row

        return df  # ! pick it back up with this method :)

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

    def _futures_df(self):  # Specific Helper scrape_futures  Tested
        """
        empty dataframe for recording futures bets
        """
        cols = ['Title', 'Description', 'Bet', 'Odds', 'scraped_ts']
        return pd.DataFrame(columns=cols)

    def _get_futures_panels(self, sp):  # Specific Helper scrape_futures  Tested
        if self.detect_no_events_warning(sp):
            return []

        main = sp.find_all('div', attrs={'id': 'main-content'})[0]
        panels = main.find_all('div', attrs={'class': 'panel panel-primary'})
        return panels

    def _futures_description(self, panel):  # Specific Helper scrape_futures  Tested
        """
        finds the description for futures bets
        """
        desc = panel.find_all('div', attrs={'id': 'futureDescription'})
        desc = desc[0].get_text()
        desc = desc.replace('\t', '').replace('\n', '')
        return desc

    def _futures_bet_odds_pairs(self, panel):  # Specific Helper scrape_futures  Tested
        """
        finds the bet-odd pairs for futures bets (e.g. [("Vikings", 250), ("Jets", 500), ..])
        - sometimes "Selection" shows up as a bet so I get rid of that if it's there
        """
        bets = panel.find_all('span', attrs={'class': 'team'})
        bets = [item.get_text() for item in bets]
        bets = [item for item in bets if item != 'Selection']  # "Selection" shows up for bets sometimes

        odds = panel.find_all('div', attrs={'class': 'market'})
        odds = [item.get_text() for item in odds]
        odds = [100.0 if item == 'even' else mfloat(item) for item in odds]

        pairs = [(bet, odd) for bet, odd in zip(bets, odds)]
        return pairs

    def _futures_add_pairs(self, df, bet_odds_pairs, title, desc):  # Specific Helper scrape_futures  Tested
        """
        uses the df, title, and description to add all the bet_odds_pairs to the dataframe
        """
        scraped_ts = self._get_scrape_ts()

        for pair in bet_odds_pairs:
            bet, odd = pair
            new_row = [title, desc, bet, odd, scraped_ts]
            df.loc[len(df)] = new_row
        return df

    def scrape_futures(self, sp):  # Top Level  Tested
        """
        scrapes a futures bet from sp -> df
        """
        df = self._futures_df()
        panels = self._get_futures_panels(sp)
        for panel in panels:
            title = self._page_title(panel)
            desc = self._futures_description(panel)
            bet_odds_pairs = self._futures_bet_odds_pairs(panel)
            df = self._futures_add_pairs(df, bet_odds_pairs, title, desc)
        return df

    def _load_existing_df(self, bet_type, league):  # Specific Helper add_new_df
        """
        loads the existing df if it exists, or returns None if there isn't one
        - changes datetime to datetime type to help with removing repeats
        """
        path = ROOT_PATH + f"/ESB/Data/{league}/{bet_type}.csv"
        if os.path.isfile(path):
            df = pd.read_csv(path)
            if 'datetime' in list(df.columns):
                df['datetime'] = pd.to_datetime(df['datetime'])
            return df
        else:
            print(f"No existing df found for {path}, making a new one!")
            return None

    def _sort_df(self, df):
        cols = ['scraped_ts', 'datetime', 'Home', 'Away', 'Title', 'Description', 'Bet']
        sort_cols = [col for col in cols if col in list(df.columns)]
        df.sort_values(by=sort_cols, inplace=True)
        return df

    def add_new_df(self, df, bet_type, league):  # Top Level
        df_path = ROOT_PATH + f"/ESB/Data/{league}/{bet_type}.csv"
        existing_df = self._load_existing_df(bet_type, league)
        if existing_df is None:
            df.to_csv(df_path, index=None)
            return df

        all_drop_cols = ['Title', 'Description', 'Bet', 'Game_Time', 'Home', 'Away', 'datetime']
        drop_cols = [col for col in list(df.columns) if col in all_drop_cols]
        # odds_cols = [col for col in list(df.columns) if col != "scraped_ts"]
        full_df = merge_odds_dfs(existing_df, df, drop_cols)
        full_df = self._sort_df(full_df)
        full_df.to_csv(df_path, index=None)
        return full_df

    def run(self, sp, league):  # Run
        main = sp.find_all('div', attrs={'id': 'main-content'})[0]
        bet_type = self.detect_bet_type(main)
        print(bet_type)

        if bet_type == 'Game_Lines':
            df = self.scrape_game_lines(sp)
        elif bet_type == 'Game_Props':
            df = self.scrape_game_props(sp)
        elif bet_type == 'Futures':
            df = self.scrape_futures(sp)

        full_df = self.add_new_df(df, bet_type, league)
        print("Data saved!")
        return full_df


if __name__ == '__main__':
    league = "NFL"
    x = ESB_Parser()
    self = x
    # x.run()
    with open(ROOT_PATH + "/Tests/esb_sps.pickle", "rb") as f:
        sp_pairs = pickle.load(f)

    sps = [item[1] for item in sp_pairs]
    sp = sps[0]
    glsps = [sp[1] for sp in sp_pairs if x.detect_bet_type(sp[1]) == 'Game_Lines']
    gpsps = [sp[1] for sp in sp_pairs if x.detect_bet_type(sp[1]) == 'Game_Props']
