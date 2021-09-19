# Sports Betting

This project compares the effectiveness of multiple AI algorithms to predict the outcomes of football and basketball bets.
The algorithms are trained on a database of team stats and odds for each game dating back to 2007.

## Contents

[1. Data Collection](#Data-Collection)

[2. Data Cleaning](#Data-Cleaning)

[3. Modeling](#Modeling)

[4. Results](#Results)

[5. Using this Repository](#Using-this-Repository)


## 1. Data Collection
The data for this project has already been scraped. 
However, there will be new data as more games are played.

### Team Names (ESPN)
Different data sources often refer to the same team with different names, like "LA Lakers" and "Los Angeles Lakers".
To merge these sources together, it's necessary for each dataset to use the same name.

The [espn_teams.py](Scrapers/espn_teams.py) file scrapes the team names in each league from ESPN.
These are treated as the official names in this project, and different names from other sources are adapted to match the ESPN names.

```
$ python Scrapers/espn_teams.py
```

The official ESPN names are stored in JSON files in [Data/Teams](https://github.com/DillonKoch/Sports_Betting/tree/master/Data/Teams).
This program also scrapes ESPN links to the teams' schedules, statistics, rosters, and depth charts.

### Season Schedules (ESPN)


```
$ python Scrapers/espn_schedule.py
```
The schedule data is stored in [NFL](Data/ESPN/NFL/Games.csv), [NBA](Data/ESPN/NBA/Games.csv), [NCAAF](Data/ESPN/NCAAF/Games.csv), and [NCAAB](Data/ESPN/NCAAB/Games.csv).

### Game Results (ESPN)
As games are played throughout the season, the [espn_game.py](Scrapers/espn_game.py) file can be used to scrape the results of the game.

```
$ python Scrapers/espn_game.py
```

### Odds (Sportsbook Reviews Online)

```
$ python Scrapers/sbo_odds.py
```


## 2. Data Cleaning

### Team Names
```
$ python Data_Cleaning/match_team.py
```


### ESPN


### Odds


### Merging ESPN and Odds


### Removing Data Leakage


## 3. Modeling



## 4. Results



## 5. Using this Repository
- mention a conda environment file I need to upload


## Tests
testingggg!
[top](#Contents)
