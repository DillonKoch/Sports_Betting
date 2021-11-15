# Sports Betting
This project evaluates multiple AI algorithms' effectiveness in predicting the outcome of football and basketball bets.
The algorithms are trained on a database of team stats and odds for each game dating back to 2007.

## Contents

[1. Data Collection](#Data-Collection)\
[2. Data Cleaning](#Data-Cleaning)\
[3. Modeling](#Modeling)\
[4. Performance](#Performance)\
[5. Using this Repository](#Using-this-Repository)


<a name="Data-Collection"></a>

<!-- TODO link to the specific scraping README, do the same for other sections -->
## 1. Data Collection  
This project focuses on four leagues: NFL, NBA, NCAAF, NCAAB. The following sections describe how the data was collected.

### ESPN
- [espn_teams.py](/Scrapers/espn_teams.py) scrapes each team's name, basic information, and links to their data on ESPN.
- [espn_schedule.py](/Scrapers/espn_schedule.py) scrapes every team's upcoming schedule.
- [espn_rosters.py](/Scrapers/espn_rosters.py) scrapes every team's roster.
- [espn_players.py](/Scrapers/espn_players.py) scrapes information about every player from their bio page on ESPN.
- [espn_game.py](/Scrapers/espn_game.py) scrapes game results and team statistics for every completed game.
- [espn_player_stats.py](/Scrapers/espn_player_stats.py) scrapes each individual player's stats from every game they play in.
- All ESPN data is stored in [/Data/ESPN/](/Data/ESPN/) except for the team information, which is saved to [/Data/Teams/](/Data/Teams/).


### Sportsbook Reviews Online
- [sbo_odds.py](/Scrapers/sbo_odds.py) downloads Excel files from [Sportsbook Reviews Online](https://www.sportsbookreviewsonline.com/) and saves them to [/Data/Odds/](/Data/Odds/).


### Elite Sportsbook
- [esb_odds.py](/Scrapers/esb_odds.py) scrapes live betting odds from [Elite Sportsbook](https://www.elitesportsbook.com/sports/home.sbk) and saves them to [/Data/ESB/](/Data/ESB/).


### Covers.com
- [covers_injuries.py](/Scrapers/covers_injuries.py) scrapes the latest injury reports from [Covers.com](https://www.covers.com/) and saves them to [/Data/Covers/](/Data/Covers/).


<a name="Data-Cleaning"></a>

## 2. Data Cleaning


### Match Teams
- [/Data_Cleaning/match_team.py](/Data/Cleaning/match_team.py) takes user input to match team names to their corresponding ESPN team name for consistency (e.g. "LA Chargers" to "Los Angeles Chargers")

### Clean ESPN
- [/Data_Cleaning/clean_espn.py](/Data_Cleaning/clean_espn.py) cleans fields in the Games.csv files with dashes and times to be strictly numeric.

### Clean Sportsbook Reviews Online Odds
- [/Data_Cleaning/clean_sbo.py](/Data_Cleaning/clean_sbo.py) cleans the Excel files from Sportsbook Reviews Online into clean csv files.


### Merge Datasets
- [/Data_Cleaning/merge_datasets.py](/Data_Cleaning/merge_datasets.py) combines the game results and team statistics data from ESPN with the betting odds data from Sportsbook Reviews Online.

### Player Data
- [/Data_Cleaning/player_data.py](/Data_Cleaning/player_data.py)


<a name="Modeling"></a>

## 3. Modeling


### Logistic Regression
Explanation


### SVM
Explanation


### Deep Learning
Explanation

### Files
Each league has three modeling files, one for each bet type (4 leagues * 3 bet types = 12 files). 
These files train each algorithm listed above for the particular bet.

### Outputs



<a name="Performance"></a>

## 4. Performance

### Win Percentage


### Expected Value


### Performance Relative to Confidence


### Production Performance




<a name="Using-this-Repository"></a>

## 5. Using This Repository


### Creating an Environment


### Running Web Scrapers


### Training Models
