#!/bin/sh

conda activate bet

cd ESPN

# ---------------------------------------------------
# update game results for each league
# ---------------------------------------------------
# echo "Updating NFL Game Results..."
python espn_update_results_scraper.py --league=NFL
echo "Updating NBA Game Results..."
python espn_update_results_scraper.py --league=NBA
# echo "Updating NCAAF Game Results..."
# python espn_update_results_scraper.py --league=NCAAF
# echo "Updating NCAAB Game Results..."
#python espn_update_results_scraper.py --league=NCAAB

# WILL UN-COMMENT THESE ONCE I MANUALLY INSERT MISSING TEAM STATS
# ---------------------------------------------------
# update team stats for each league
# ---------------------------------------------------
#python team_stats_scraper.py --league=NFL --cmd=update
echo "Updating NBA Team Stats..."
# python team_stats_scraper.py --league=NBA --cmd=update
#python team_stats_scraper.py --league=NCAAF --cmd=update
#python team_stats_scraper.py --league=NCAAB --cmd=update

# ---------------------------------------------------
# # Updating prod tables...
# ---------------------------------------------------
# cd ../PROD
# python prod_table.py --league=NBA
# cd ..

# ---------------------------------------------------
# Updating ML tables...
# ---------------------------------------------------
cd ..
