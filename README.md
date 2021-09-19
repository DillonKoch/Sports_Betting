# Sports Betting

This project compares the effectiveness of multiple AI algorithms to predict the outcomes of football and basketball bets.
The algorithms are trained on a database of team stats and odds for each game dating back to 2007.

## Contents

[1. Data Collection](#Data-Collection)\
[2. Data Cleaning](#Data-Cleaning)\
[3. Modeling](#Modeling)\
[4. Results](#Results)\
[5. Using this Repository](#Using-this-Repository)


<a name="Data-Collection"></a>

## 1. Data Collection
This project focuses on four leagues: NFL, NBA, NCAAF, NCAAB. 

The following sections describe how the data was scraped, and how to continue scraping new data as it becomes available.

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
To scrape game data, first we must scrape the schedules for each league with [espn_schedule.py](Scrapers/espn_schedule.py).
This just collects the date of the game, teams playing, and other basic game information.
The following script will scrape every schedule since 2007, including future games not yet played.
```
$ python Scrapers/espn_schedule.py
```
The schedule data is stored in [NFL](Data/ESPN/NFL/Games.csv), [NBA](Data/ESPN/NBA/Games.csv), [NCAAF](Data/ESPN/NCAAF/Games.csv), and [NCAAB](Data/ESPN/NCAAB/Games.csv).

### Game Results (ESPN)
Once the schedule is scraped and the games are played, [espn_game.py](Scrapers/espn_game.py) will scrape statistics from the games.

```
$ python Scrapers/espn_game.py
```
This data is stored in the same files as the schedule: [NFL](Data/ESPN/NFL/Games.csv), [NBA](Data/ESPN/NBA/Games.csv), [NCAAF](Data/ESPN/NCAAF/Games.csv), and [NCAAB](Data/ESPN/NCAAB/Games.csv).


### Odds (Sportsbook Reviews Online)
In addition to team names and game statistics, betting odds are also scraped with [sbo_odds.py](Scrapers/sbo_odds.py).
This data includes the odds for the three most popular bets: the [moneyline, spread, and over/under](https://www.mytopsportsbooks.com/guide/single-bets/).

```
$ python Scrapers/sbo_odds.py
```
This script scrapes individual .xlsx files for each season, and saves them in folders for each league in the [Data/Odds](https://github.com/DillonKoch/Sports_Betting/tree/master/Data/Odds) folder.

The files are merged and cleaned in the next section.


<a name="Data-Cleaning"></a>

## 2. Data Cleaning

### Team Names

```
$ python Data_Cleaning/match_team.py
```


### ESPN
```
$ python Data_Cleaning/clean_espn.py
```


### Odds

```
$ python Data_Cleaning/clean_sbo.py
```

### Merging ESPN and Odds
```
$ python Data_Cleaning/merge_datasets.py
```

### Removing Data Leakage



<a name="Modeling"></a>

## 3. Modeling






<a name="Results"></a>

## 4. Results



<a name="Using-this-Repository"></a>

## 5. Using this Repository
- mention a conda environment file I need to upload


### Tests
