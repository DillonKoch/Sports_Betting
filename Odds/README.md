# Odds

- The objective of this module is to gather historical odds data (NFL/NBA/NCAAF/NCAAB)
- Data is downloaded from https://www.sportsbookreviewsonline.com/scoresoddsarchives/scoresoddsarchives.htm 
- Data goes back to 2007 in all four sports and is still being updated periodically

## Folders
- One folder per league, including .xlsx files for each season (how the data is downloaded originally) and .csv files that I create from them

## Files
- download_data.py
- clean_new_odds.py converts raw .xlsx files from the website to clean .csv's in the league folders
- merge_league_data.py
- {league}.csv is a csv including all data from that league formatted nicely
- run_odds.sh is a shell script that runs all odds-related processes (described below)


## run_odds.sh process
- runs download_data.py, which downloads the latest .xlsx files from the odds website
- runs clean_new_odds.py for each league to create .csv files in the league folders
- runs merge_league_data.py for each league to create the final {league}.csv files
- runs odds_data_qa_test.py to test the quality of the data
