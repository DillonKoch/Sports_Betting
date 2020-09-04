#!/bin/sh

cd WH

echo "Scraping NBA..."
python wh_game_scraper.py --league=NBA

echo "Scraping NFL..."
python wh_game_scraper.py --league=NFL

echo "Scraping NCAAF..."
python wh_game_scraper.py --league=NCAAF

echo "Scraping NCAAB..."
python wh_game_scraper.py --league=NCAAB

cd ..
