from unittest import TestCase
from dynamo import MyBets
import pandas as pd


class TestMyBets(TestCase):
    def setUp(self):
        self.mb = MyBets()
        self.mb._load_local_data()

    def test_init(self):
        pass

    def test_load_local_data(self):
        self.assertIsInstance(self.mb.local_data, pd.DataFrame)
        self.assertIsInstance(self.mb.cols, list)
        self.assertTrue(self.mb.local_data.shape[0] > 0)
        self.assertTrue(self.mb.local_data.shape[1] > 0)

    def test_row_to_dict_item(self):
        row1 = self.mb.local_data.iloc[0, :]
        row1_value = {
            'Bettor': 'Dillon Koch',
            'Bet ID': 1,
            'Parlay No.': "NULL",
            'Bet Type': 'Spread',
            'Bet Date': '2019-09-22',
            'Gameday': '2019-09-22',
            'Bet': 5,
            'To Win': 4.55,
            'Home Team': 'San Francisco 49ers',
            'Home Record': '2-0, 0-0 Home',
            'Away Team': 'Pittsburgh Steelers',
            'Away Record': '0-2, 0-1 Away',
            'Pick': 'Pittsburgh Steelers',
            'Home Score': 24.0,
            'Away Score': 20.0,
            'Spread': 6.5,
            'Money Line': -110.0,
            'League': 'NFL',
            'Outcome': 'Win',
            'ESPN ID': 401127998}
        self.assertEqual(row1_value, self.mb._row_to_dict_item(row1))

    def test_insert_row_to_table(self):
        pass
