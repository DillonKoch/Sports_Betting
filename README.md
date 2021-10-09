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
This project focuses on four leagues: NFL, NBA, NCAAF, NCAAB. 

The following sections describe how the data was scraped, and how to continue scraping new data as more games are played.

### Team Names (ESPN)
Different data sources often refer to the same team with different names, like "LA Lakers" and "Los Angeles Lakers".
To merge these sources together, it's necessary for each dataset to use the same name.

The [espn_teams.py](Scrapers/espn_teams.py) file scrapes team names from ESPN.
These are treated as the official names in this project, and different names from other sources are adapted to match the ESPN names.

```
$ python Scrapers/espn_teams.py
```

The official ESPN names are stored in JSON files in [Data/Teams](https://github.com/DillonKoch/Sports_Betting/tree/master/Data/Teams).
This program also scrapes ESPN links to the teams' schedules, statistics, rosters, and depth charts.

### Season Schedules (ESPN)
Before scraping game data, we have to scrape the schedules with [espn_schedule.py](Scrapers/espn_schedule.py).
This just collects the date of the game, teams playing, and other basic game information.
The following script will scrape every schedule since 2007, including future games not yet played.
```
$ python Scrapers/espn_schedule.py
```
The schedule data is stored in [NFL](Data/ESPN/NFL/Games.csv), [NBA](Data/ESPN/NBA/Games.csv), [NCAAF](Data/ESPN/NCAAF/Games.csv), and [NCAAB](Data/ESPN/NCAAB/Games.csv).

### Game Results (ESPN)
Once the games are played, [espn_game.py](Scrapers/espn_game.py) will scrape statistics from the games.

```
# league options are NFL, NBA, NCAAF, NCAAB
$ python Scrapers/espn_game.py --league=NFL
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

### Removing Data Leakage



<a name="Modeling"></a>

## 3. Modeling






<a name="Results"></a>

## 4. Results



<a name="Using-this-Repository"></a>

## 5. Using this Repository
- mention a conda environment file I need to upload


### Tests
