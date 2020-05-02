import datetime
import re
import urllib

import pandas as pd
from bs4 import BeautifulSoup as soup
from tqdm import tqdm


class NBA:
    def __init__(self):
        self.teams = ['atl', 'bos', 'bkn', 'cha', 'chi', 'cle', 'dal', 'den', 'det', 'gs', 'hou', 'ind', 'lac', 'lal',
                      'mem', 'mia', 'mil', 'min', 'no', 'ny', 'okc', 'orl', 'phi', 'phx', 'por', 'sac', 'sa', 'tor',
                      'utah', 'wsh']

    def _get_sp1(self, url):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

        headers = {'User-Agent': user_agent, }

        request = urllib.request.Request(url, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)

        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        return sp

    # def _get_link(self, day_to_scrape=False):
    #     """
    #     _get_link returns the link of a specific day's games to scrape

    #     Args:
    #         day_to_scrape (bool, optional): Specific day to get games for, if not today's. Defaults to False.
    #     """
    #     self.link_base = "https://www.espn.com/nba/scoreboard/_/date/"

    #     if not day_to_scrape:
    #         today = datetime.date.today()
    #         self.year = str(today.year)
    #         self.month = str(today.month) if len(str(today.month)) == 2 else '0' + str(today.month)
    #         self.day = str(today.day) if len(str(today.day)) == 2 else '0' + str(today.day)
    #         self.full_link = self.link_base + self.year + self.month + self.day
    #     else:
    #         self.year = day_to_scrape[:4]
    #         self.month = day_to_scrape[4:6]
    #         self.day = day_to_scrape[6:]
    #         self.full_link = self.link_base + day_to_scrape

    def team_game_links(self, team):
        base_link = "https://www.espn.com/nba/team/schedule/_/name/"
        full_link = base_link + team
        sp = self._get_sp1(full_link)
        table_tds = sp.find_all('td', attrs={'class': 'Table__TD'})
        game_strs = [str(td) for td in table_tds if 'http://www.espn.com/nba/game?gameId=' in str(td)]

        link_comp = re.compile(r'href="http://www.espn.com/nba/game\?gameId=\d+')
        game_links = [link_comp.findall(game_str) for game_str in game_strs]
        game_links = [item[0].replace('href="', '') for item in game_links]

        return game_links

    def game_info(self, link):
        sp = self._get_sp1(link)
        date = self.game_date(link)

        # Getting home and away team locations and team names:
        # locations
        home_away_loc = sp.find_all('span', attrs={'class': 'long-name'})
        home_loc = home_away_loc[1].get_text()
        away_loc = home_away_loc[0].get_text()
        # team names
        home_away_name = sp.find_all('span', attrs={'class': 'short-name'})
        home_name = home_away_name[1].get_text()
        away_name = home_away_name[0].get_text()
        # locations + names
        home_full = home_loc + ' ' + home_name
        away_full = away_loc + ' ' + away_name
        # records
        record_info = sp.find_all('div', attrs={'class': 'record'})
        away_record = record_info[0].get_text()
        home_record = record_info[1].get_text()
        # is the game final
        game_status = sp.find_all('span', attrs={'class': 'game-time status-detail'})
        # score
        if game_status == []:
            away_score = None
            home_score = None
            game_status = 'Not played yet'
        else:
            game_status = game_status[0].get_text()
            # getting the final score of the game
            away_score = sp.find_all('div', attrs={'class': 'score icon-font-after'})
            away_score = away_score[0].get_text()
            if len(away_score) == 0:
                away_score = None

            home_score = sp.find_all('div', attrs={'class': 'score icon-font-before'})
            home_score = home_score[0].get_text()
            if len(home_score) == 0:
                home_score = None

        return date, home_full, home_record, home_score, away_full, away_record, away_score, game_status

    def game_date(self, link):
        try:
            sp = self._get_sp1(link)
            date = sp.find_all('span', attrs={'data-behavior': 'date_time'})
            return date[1].get_text()
        except BaseException:
            print('error!')
            return None

    def team_df(self, team):
        cols = ['Date', 'Home Team', 'Home Record', 'Home Score', 'Away Team', 'Away Record',
                'Away Score', 'Game Status']
        df = pd.DataFrame(columns=cols)
        for link in tqdm(self.team_game_links(team)):
            new_col = list(self.game_info(link))
            df.loc[len(df)] = new_col

        return df


if __name__ == "__main__":
    x = NBA()
    heat = x.team_game_links('mia')
    df = x.team_df('mia')
    date = x.game_date(heat[0])
