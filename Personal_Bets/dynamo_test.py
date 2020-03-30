import warnings
from unittest import TestCase

import boto3
import pandas as pd

from dynamo import MyBets


class TestMyBets(TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore")
        self.mb = MyBets()
        self.mb._load_local_data()

    def test_init(self):
        pass

    def test_load_table_data(self):
        data1 = self.mb._load_table_data()

        self.assertIsInstance(data1, list)
        for item in data1:
            self.assertIsInstance(item, dict)

    def test_load_local_data(self):
        self.assertIsInstance(self.mb.local_data, pd.DataFrame)
        self.assertIsInstance(self.mb.cols, list)
        self.assertTrue(self.mb.local_data.shape[0] > 0)
        self.assertTrue(self.mb.local_data.shape[1] > 0)

    def test_row_to_dict_item(self):
        row1 = self.mb.local_data.iloc[0, :]
        row1_value = {
            'Bettor': 'Dillon Koch',
            'Bet ID': '1',
            'Parlay No.': "NULL",
            'Bet Type': 'Spread',
            'Bet Date': '2019-09-22',
            'Gameday': '2019-09-22',
            'Bet': '5',
            'To Win': '4.55',
            'Home Team': 'San Francisco 49ers',
            'Home Record': '2-0, 0-0 Home',
            'Away Team': 'Pittsburgh Steelers',
            'Away Record': '0-2, 0-1 Away',
            'Pick': 'Pittsburgh Steelers',
            'Home Score': '24',
            'Away Score': '20',
            'Spread': '6.5',
            'Money Line': '-110.0',
            'League': 'NFL',
            'Outcome': 'Win',
            'ESPN_ID': '401127998'}
        self.assertEqual(row1_value, self.mb._row_to_dict_item(row1))

    def test_insert_and_delete_item(self):
        # going to insert the fake item, then delete it to confirm both work
        data1 = self.mb._load_table_data()
        num_items1 = len(data1)

        fake_value = {
            'Bettor': 'Dillon Koch',
            'Bet ID': '1',
            'Parlay No.': "NULL",
            'Bet Type': 'Spread',
            'Bet Date': '2019-09-22',
            'Gameday': '2019-09-22',
            'Bet': '5',
            'To Win': '4.55',
            'Home Team': 'San Francisco 49ers',
            'Home Record': '2-0, 0-0 Home',
            'Away Team': 'Pittsburgh Steelers',
            'Away Record': '0-2, 0-1 Away',
            'Pick': 'Pittsburgh Steelers',
            'Home Score': '24',
            'Away Score': '20',
            'Spread': '6.5',
            'Money Line': '-110.0',
            'League': 'NFL',
            'Outcome': 'Win',
            'ESPN_ID': '999999999'}  # notice this won't interfere
        self.mb.insert_row_to_table(fake_value)

        data2 = self.mb._load_table_data()
        num_items2 = len(data2)
        self.assertEqual(num_items2, num_items1 + 1)

        self.mb._delete_item("999999999")

        data3 = self.mb._load_table_data()
        num_items3 = len(data3)
        self.assertEqual(num_items1, num_items3)

    def test_is_row_in_table(self):
        pass
