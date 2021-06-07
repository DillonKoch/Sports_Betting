#!/bin/sh

conda activate bet

cd ESPN


# ---------------------------------------------------
# NFL
echo "Updating NFL Game Results..."
python espn_game_update_scraper.py --league=NFL
echo "Updating NFL Team Stats..."
python espn_team_stats_update_scraper.py --league=NFL
# ---------------------------------------------------

# ---------------------------------------------------
# NBA
echo "Updating NBA Game Results..."
python espn_game_update_scraper.py --league=NBA
echo "Updating NBA Team Stats..."
python espn_team_stats_update_scraper.py --league=NBA
python espn_change_team_name.py --league=NBA --old_name="LA Clippers" --new_name="Los Angeles Clippers"
# ---------------------------------------------------

# ---------------------------------------------------
# NCAAF
echo "Updating NCAAF Game Results..."
python espn_game_update_scraper.py --league=NCAAF
echo "Updating NCAAF Team Stats..."
python espn_team_stats_update_scraper.py --league=NCAAF
# ---------------------------------------------------

# ---------------------------------------------------
# NCAAB
# echo "Updating NCAAB Game Results..."
# python espn_game_update_scraper.py --league=NCAAB
# echo "Updating NCAAB Team Stats..."
# python espn_team_stats_update_scraper.py --league=NCAAB
# ---------------------------------------------------


cd ..


