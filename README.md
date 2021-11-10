# Sports Betting
This project evaluates multiple AI algorithms' effectiveness in predicting the outcome of football and basketball bets.
The algorithms are trained on a database of team stats and odds for each game dating back to 2007.

## Contents

[1. Data Collection](#Data-Collection)\
[2. Data Cleaning](#Data-Cleaning)\
[3. Modeling](#Modeling)\
[4. Results](#Results)\
[5. Using this Repository](#Using-this-Repository)


<a name="Data-Collection"></a>

## 1. Data Collection
This project focuses on four leagues: NFL, NBA, NCAAF, NCAAB. The following sections describe how the data was collected.

### ESPN
- [espn_teams.py](/Scrapers/espn_teams.py) scrapes team names/information and saves to one JSON file per league in [/Data/Teams/](/Data/Teams/).
- [espn_schedule.py](/Scrapers/espn_schedule.py) scrapes information about each team's upcoming games from ESPN, saved to a Games.csv file for each league in [/Data/ESPN/](/Data/ESPN/).
- [espn_rosters.py](/Scrapers/espn_rosters.py) scrapes each team's roster from ESPN, saved to Roser.csv files in [/Data/ESPN/](/Data/ESPN/).
- [espn_players.py](/Scrapers/espn_players.py) scrapes information about every player from their bio on ESPN, saves to Players.csv files in [/Data/ESPN/](/Data/ESPN/).
- [espn_game.py](/Scrapers/espn_game.py) scrapes game statistics from ESPN for completed games, saves to Games.csv files in [/Data/ESPN/](/Data/ESPN/).
- [espn_player_stats.py](/Scrapers/espn_player_stats.py) scrapes each individual player's stats from every game they play in, saved to Player_Stats.csv files in [/Data/ESPN/](/Data/ESPN/).


### Sportsbook Reviews Online
- [sbo_odds.py](/Scrapers/sbo_odds.py) downloads .xlsx files from [Sportsbook Reviews Online](https://www.sportsbookreviewsonline.com/), saves to [/Data/Odds/](/Data/Odds/).


### Elite Sportsbook
- [esb_odds.py](/Scrapers/esb_odds.py) scrapes live betting odds from [Elite Sportsbook](https://www.elitesportsbook.com/sports/home.sbk), saved to [/Data/ESB/](/Data/ESB/).


### Covers.com
- [covers_injuries.py](/Scrapers/covers_injuries.py) scrapes the latest injury reports from [Covers.com](https://www.covers.com/), saved to [/Data/Covers/](/Data/Covers/).


<a name="Data-Cleaning"></a>

## 2. Data Cleaning


### Match Teams


### Clean ESPN
- [/Data_Cleaning/clean_espn.py](/Data_Cleaning/clean_espn.py) cleans fields in the Games.csv files with dashes and times to be strictly numeric.

### Clean Sportsbook Reviews Online Odds
- [/Data_Cleaning/clean_sbo.py]


### Merge Datasets


### Player Data

<!-- ### Team Names
As mentioned earlier, team names may vary from one data source to another. 
Teams also move, like the San Diego Chargers moving to Los Angeles.

For these reasons, we treat the team names from ESPN as the official names, and adapt other names to the ESPN ones with [match_team.py](Data_Cleaning/match_team.py).
This script will take user input to save unofficial names for each team in the [Data/Teams](https://github.com/DillonKoch/Sports_Betting/tree/master/Data/Teams) JSON files.
These unofficial names are saved in the "Other" section for each team.

For example, the "Other" section for the Iowa Hawkeyes may include "Iowa", "IowaHawkeyes", "UIowa", or any other slightly different name referring to Iowa.

```
$ python Data_Cleaning/match_team.py
```

### ESPN
Steps for cleaning raw ESPN data into new dataset:
- Load raw data from league folders in [/Data/ESPN/](https://github.com/DillonKoch/Sports_Betting/tree/master/Data/ESPN).
- Copy columns to new dataset that don't require cleaning
- Clean raw team names using [Data/Teams](https://github.com/DillonKoch/Sports_Betting/tree/master/Data/Teams) JSON files
- Clean stats with dashes (e.g. 13-16 Free Throws Made-Att) into multiple integer columns (e.g. 13 FT made, 16 FT attempted)
- Clean time-related stats into pure seconds ("27:30" is cleaned to 1650)

```
$ python Data_Cleaning/clean_espn.py
```

### Odds
Steps for cleaning raw Odds data into new dataset:
- stuff
- stuff
- more stuff

```
$ python Data_Cleaning/clean_sbo.py
```

### Merging ESPN and Odds
```
$ python Data_Cleaning/merge_datasets.py
```

### Removing Data Leakage -->



<a name="Modeling"></a>

## 3. Modeling


### Logistic Regression


### SVM


### Deep Learning



<a name="Results"></a>

## 4. Results

### Win Percentage


### Expected Value


### Performance Relative to Confidence




<a name="Using-this-Repository"></a>

## 5. Using This Repository


### Creating an Environment


### Running Web Scrapers


### Training Models
