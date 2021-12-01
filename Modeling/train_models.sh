#!/bin/sh

python modeling_data.py

# NFL
python nfl_ml.py
python nfl_spread.py
python nfl_total.py

# NBA
python nba_ml.py
python nba_spread.py
python nba_total.py

# NCAAF
python ncaaf_ml.py
python ncaaf_spread.py
python ncaaf_total.py

# NCAAB
python ncaab_ml.py
python ncaab_spread.py
python ncaab_total.py

python evaluate_predictions.py
