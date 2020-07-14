#!/bin/sh

conda activate bet

cd ESPN_Scrapers

# update game results for each league
echo "Updating NFL Game Results..."
python espn_update_results.py --league=NFL
echo "Updating NBA Game Results..."
python espn_update_results.py --league=NBA
echo "Updating NCAAF Game Results..."
python espn_update_results.py --league=NCAAF
#python espn_update_results.py --league=NCAAB

# WILL UN-COMMENT THESE ONCE I MANUALLY INSERT MISSING TEAM STATS
# update team stats for each league
#python team_stats_scraper.py --league=NFL --cmd=update
#python team_stats_scraper.py --league=NBA --cmd=update
#python team_stats_scraper.py --league=NCAAF --cmd=update
#python team_stats_scraper.py --league=NCAAB --cmd=update

cd ..
