#!/bin/sh

python download_data.py --all
python clean_new_odds.py --all
python merge_league_data.py --all

cd ..
pytest -k odds_qa_test -v
cd Odds
