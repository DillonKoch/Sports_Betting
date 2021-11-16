# Data Cleaning
All files in this folder are used to clean the raw data gathered in the [Data_Collection](/Data_Collection/) phase.



### Match Teams
- [/Data_Cleaning/match_team.py](/Data/Cleaning/match_team.py) takes user input to match team names to their corresponding ESPN team name for consistency (e.g. "LA Chargers" to "Los Angeles Chargers"). For each team without a match, the program will offer the 10 closest matches. It's then up to the user to decide which one the correct match is, or input "O" for "Other".

### Clean ESPN
- [/Data_Cleaning/clean_espn.py](/Data_Cleaning/clean_espn.py) cleans fields in the Games.csv files with dashes and times to be strictly numeric.

### Clean Sportsbook Reviews Online Odds
- [/Data_Cleaning/clean_sbo.py](/Data_Cleaning/clean_sbo.py) cleans the Excel files from Sportsbook Reviews Online into clean csv files.


### Merge Datasets
- [/Data_Cleaning/merge_datasets.py](/Data_Cleaning/merge_datasets.py) combines the game results and team statistics data from ESPN with the betting odds data from Sportsbook Reviews Online.

### Player Data
- [/Data_Cleaning/player_data.py](/Data_Cleaning/player_data.py)
