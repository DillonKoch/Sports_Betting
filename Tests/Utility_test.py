from unittest import TestCase

from bs4 import BeautifulSoup as soup

from Utility.Utility import get_sp1


class TestUtility(TestCase):
    def setUp(self):
        pass

    def test_get_sp1(self):
        sp = get_sp1("https://www.espn.com/nfl/game/_/gameId/401128044")

        self.assertIsInstance(sp, soup)
