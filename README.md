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
One issue with using multiple data sources is that they may use different names to refer to the same team.
For example, one source may use "LA Lakers" and another could use "Los Angeles Lakers".
To merge these datasets together, it's necessary to use the same name.

The [espn_teams.py](Scrapers/espn_teams.py) file scrapes the team names in each league from ESPN.
These names are treated as the official names in this project, and different names from other sources are adapted to match the name from ESPN.



### Sportsbook Reviews Online
Explanation


#### Flow
For ESPN, first the team names are scraped, then schedules, then games. 

The odds from SBO are scraped periodically.


## Web Scraping


#### espn_game.py
Sentence explanation

#### espn_schedule.py

#### espn_teams.py

#### sbo_odds.py


## 2. Data Cleaning



## 3. Modeling



## 4. Results



## 5. Using this Repository
- mention a conda environment file I need to upload


## Tests
testingggg!
[top](#Contents)
