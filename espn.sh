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


