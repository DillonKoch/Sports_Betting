#!/bin/sh

python download_data.py
python clean_new_odds.py
# python merge_league_data.py

cd ../Tests
pytest -k odds_qa_test -v  # TODO
cd ../Odds
