# Data Collection
Every file used to collect data belongs in this folder.

### ESPN
- [espn_teams.py](/Data_Collection/espn_teams.py) scrapes each team's name, basic information, and links to their data on ESPN.
- [espn_schedule.py](/Data_Collection/espn_schedule.py) scrapes every team's upcoming schedule.
- [espn_rosters.py](/Data_Collection/espn_rosters.py) scrapes every team's roster.
- [espn_players.py](/Data_Collection/espn_players.py) scrapes information about every player from their bio page on ESPN.
- [espn_game.py](/Data_Collection/espn_game.py) scrapes game results and team statistics for every completed game.
- [espn_player_stats.py](/Data_Collection/espn_player_stats.py) scrapes each individual player's stats from every game they play in.
- All ESPN data is stored in [/Data/ESPN/](/Data/ESPN/) except for the team information, which is saved to [/Data/Teams/](/Data/Teams/).

### Sportsbook Reviews Online
- [sbo_odds.py](/Data_Collection/sbo_odds.py) downloads Excel files from [Sportsbook Reviews Online](https://www.sportsbookreviewsonline.com/) and saves them to [/Data/Odds/](/Data/Odds/).

### Elite Sportsbook
- [esb_odds.py](/Data_Collection/esb_odds.py) scrapes live betting odds from [Elite Sportsbook](https://www.elitesportsbook.com/sports/home.sbk) and saves them to [/Data/ESB/](/Data/ESB/).

### Covers
- [covers_injuries.py](/Data_Collection/covers_injuries.py) scrapes the latest injury reports from [Covers.com](https://www.covers.com/) and saves them to [/Data/Covers/](/Data/Covers/).


### Cron Schedule
