# ESPN Scrapers

## Files:
- espn_game_scraper.py
- espn_season_scraper.py
- team_stats_scraper.py
- merge_team.py
- date_converter.py
 
#### JSON config files:
- nfl.json
- nba.json
- ncaaf.json
- ncaab.json


## Overall Process:
    - Run espn_season_scraper.py for each league until all seasons are scraped
      - This will scrape main game information like home/away team, records, date, score, etc
      - This uses the espn_game_scraper, which gets game information for one game on espn
    - Run espn_stats_scraper.py to add team stats for each game like rebounds, first downs, etc
    - Run merge_team to combine each team's season csv's into one csv
      - before running, each team will have one csv per season, after each team has one csv with everything

    - note: date_converter.py was used to fix date formats in data previously scraped differently
  

## Descriptions of Each File:

### ESPN Game Scraper
