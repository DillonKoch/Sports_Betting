from bs4 import BeautifulSoup as soup
import datetime
import urllib
import re


class NBA:
    def __init__(self):
        pass

    def getsp1(self, url):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

        headers = {'User-Agent': user_agent, }

        request = urllib.request.Request(url, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)

        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        return sp

    def _get_link(self, day_to_scrape=False):
        """
        _get_link returns the link of a specific day's games to scrape

        Args:
            day_to_scrape (bool, optional): Specific day to get games for, if not today's. Defaults to False.
        """
        self.link_base = "https://www.espn.com/nba/scoreboard/_/date/"

        if not day_to_scrape:
            today = datetime.date.today()
            self.year = str(today.year)
            self.month = str(today.month) if len(str(today.month)) == 2 else '0' + str(today.month)
            self.day = str(today.day) if len(str(today.day)) == 2 else '0' + str(today.day)
            self.full_link = self.link_base + self.year + self.month + self.day
        else:
            self.year = day_to_scrape[:4]
            self.month = day_to_scrape[4:6]
            self.day = day_to_scrape[6:]
            self.full_link = self.link_base + day_to_scrape

    def team_game_links(self, team):
        base_link = "https://www.espn.com/nba/team/schedule/_/name/"
        full_link = base_link + team
        sp = self.getsp1(full_link)
        table_tds = sp.find_all('td', attrs={'class': 'Table__TD'})
        game_strs = [str(td) for td in table_tds if 'http://www.espn.com/nba/game?gameId=' in str(td)]

        link_comp = re.compile(r'href="http://www.espn.com/nba/game\?gameId=\d+')
        game_links = [link_comp.findall(game_str) for game_str in game_strs]
        game_links = [item[0].replace('href="', '') for item in game_links]

        return game_links


if __name__ == "__main__":
    x = NBA()
    x._get_link()
    heat = x.team_game_links('mia')
