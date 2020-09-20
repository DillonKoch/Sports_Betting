# ==============================================================================
# File: esb_general_scraper.py
# Project: ESB
# File Created: Friday, 18th September 2020 3:00:34 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 19th September 2020 8:01:36 pm
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

try:
    print(hp)
except BaseException:
    with open('esb_sp_list.pickle', 'rb') as f:
        data = pickle.load(f)

    sps = [item[2] for item in data]

    titles = [item[0] for item in data]
    events = [item[1] for item in data]

    for i, (title, event) in enumerate(zip(titles, events)):
        print(f"{i} - {title} - {event}")


class ESB_General_Scraper:
    def __init__(self, league, sp):
        self.leauge = league
        self.sp = sp

    def _get_scrape_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def detect_no_events_warning(self, sp):  # Global Helper
        """
        detects the presence of a no events warning
        """
        warning = sp.find_all('div', attrs={'class': 'alert alert-warning no-events'})
        return True if len(warning) > 0 else False

    def detect_game_titles(self, sp):  # Specific Helper detect_bet_types
        """
        detects whether the sp has game titles or not (Moneyline, Spread, Totals)
        """
        money_total = sp.find_all('div', attrs={'class': 'column money header-row pull-right'})
        spread = sp.find_all('div', attrs={'class': 'column spread header-row pull-right'})
        return True if len(money_total) == 2 else False

    def detect_event_headings(self, sp):  # Specific Helper detect_bet_types
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
        """
        if self.detect_game_titles(sp):
            if self.detect_event_headings(sp):
                return 'Game_Props'
            else:
                return 'Game_Lines'
        else:
            return 'Futures'

    def game_lines_df(self):  # Specific Helper scrape_game_lines
        """
        creates empty game lines df
        """
        cols = ['Title', 'datetime', 'Game_Time', 'Home', 'Away',
                'Over_ESB', 'Over_ml_ESB', 'Under_ESB', 'Under_ml_ESB',
                'Home_Line_ESB', 'Home_Line_ml_ESB', 'Away_Line_ESB', 'Away_Line_ml_ESB',
                'Home_ML_ESB', 'Away_ML_ESB',
                'scraped_ts']
        return pd.DataFrame(columns=cols)

    def _is_date(self, full_text):  # Specific Helper scrape_game_lines
        """
        checks if the text of a date_event object is a date
        - returns True if date, False otherwise
        """
        date_comp = re.compile(
            r"^(January|February|March|April|June|July|August|September|October|November|December|) \d{1,2}, \d{4}$")
        match = re.match(date_comp, full_text)
        return True if match else False

    def _game_time(self, event):  # Specific Helper scrape_game_lines
        """
        finds the game time of an event
        """
        time = event.find_all('div', attrs={'id': 'time'})
        time = time[0].get_text()
        return time

    def _teams(self, event):  # Specific Helper scrape_game_lines
        """
        finds the home and away teams in an event
        """
        away = event.find_all('span', attrs={'id': 'firstTeamName'})
        away = away[0].get_text()
        home = event.find_all('span', attrs={'id': 'secondTeamName'})
        home = home[0].get_text()
        # TODO assert these are in valid league teams
        return home, away

    def _moneylines(self, event):  # Specific Helper scrape_game_lines
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

        return home_ml, away_ml

    def _spreads(self, event):  # Specific Helper scrape_game_lines
        """
        finds the home/away spread/spread_ml of an event
        """
        spreads = event.find_all('div', attrs={'class': 'column spread pull-right'})
        away_text, home_text = [item.get_text().strip() for item in spreads]
        print(away_text)
        print(home_text)
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

        return home_spread, home_spread_ml, away_spread, away_spread_ml

    def _totals(self, event):  # Specific Helper scrape_game_lines
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

        return over, over_ml, under, under_ml

    def _get_date_events(self, sp):  # Specific Helper scrape_game_lines
        """
        finds the date_event items in the original sp
        - the item can either be a date (September 29, 2020) or an actual event (game)
        """
        event_sp = sp.find_all('div', attrs={'class': 'row event'})[0]
        date_events = event_sp.find_all('div', attrs={'class': ['row event', 'col-xs-12 date']})
        return date_events

    def _check_is_date(self, date_event, date):  # Specific Helper scrape_game_lines
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

    def _date_event_to_row(self, date_event, date):  # Specific Helper scrape_game_lines
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
        df = self.game_lines_df()
        date_events = self._get_date_events(sp)

        date = None
        for date_event in date_events:
            # if date_event is a date, update 'date' and move to next iteration
            date, found_date = self._check_is_date(date_event, date)
            if found_date:
                continue

            row = self._date_event_to_row(date_event, date)
            df.loc[len(df)] = row
        return df

    def game_props_df(self):  # Helping Helper _update_game_prop_df
        cols = ['datetime', 'game_time', 'Home', 'Away', 'Title', 'Description', 'Bet',
                'spread/overunder', 'Odds', 'scraped_ts']
        return pd.DataFrame(columns=cols)

    def _description(self, date_event):  # Helping Helper _update_game_prop_df
        desc = date_event.find_all('div', attrs={'class': 'row event eventheading'})
        return desc[0].get_text().strip()

    def _update_game_prop_df(self, df, date_event, date, title):  # Specific Helper scrape_game_props
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

    def _page_title(self, sp):  # Specific Helper scrape_game_props
        title = sp.find_all('span', attrs={'class': 'titleLabel'})
        title = title[0].get_text()
        return title

    def scrape_game_props(self, sp):  # Top Level
        df = self.game_props_df()
        date_events = self._get_date_events(sp)
        title = self._page_title(sp)

        date = None
        for date_event in date_events:
            date, found_date = self._check_is_date(date_event, date)
            if found_date:
                continue

            df = self._update_game_prop_df(df, date_event, date, title)
        df = df.loc[df['Odds'].notnull()]
        return df

    def futures_df(self):  # Specific Helper scrape_futures
        cols = []
        return pd.DataFrame(columns=cols)

    def scrape_futures(self):  # Top Level
        pass

    def run(self):  # Run
        main = self.sp.find_all('div', attrs={'id': 'main-content'})[0]

        bet_type = self.detect_bet_type(main)
        print(bet_type)

        panels = main.find_all('div', attrs={'class': 'panel panel-primary'})

        for panel in panels:
            title = panel.find_all('div', attrs={'id': 'eventTitleBar'})
            title = title[0].get_text().strip()
            future_desc = panel.find_all('div', attrs={'id': 'futureDescription'})
            if len(future_desc) > 0:
                desc = future_desc[0].get_text().strip()


if __name__ == '__main__':
    x = ESB_General_Scraper("NFL", sps[0])
    self = x
    hp = True
    # x.run()


# future_descs = []
# titles = []
# all_panels = []
# for sp in sps:
#     main = sp.find_all('div', attrs={'id': 'main-content'})[0]
#     panels = main.find_all('div', attrs={'class': 'panel panel-primary'})
#     for panel in panels:
#         all_panels.append(panel)
#         title = panel.find_all('div', attrs={'id': 'eventTitleBar'})
#         title = title[0].get_text().strip()
#         titles.append(title)
#         future_desc = panel.find_all('div', attrs={'id': 'futureDescription'})
#         if len(future_desc) > 0:
#             desc = future_desc[0].get_text().strip()
#             print(desc)
#             future_descs.append(desc)
