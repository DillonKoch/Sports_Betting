# Elite Sportsbook

- The objective of this module is to scrape betting data from Elite Sportsbook
- The following leagues are included: NFL, NBA, NCAAF, NCAAB


## Files
- esb_navigator.py clicks through the website to find HTML of relevant bets
- esb_parser.py uses the HTML from esb_navigator.py to find new bets and add them to the Data folder

## Folders
- The Data folder includes three categories of bets for the four leageus: Game Lines, Game Props, Futures
- v1 includes old code that has since been replaced
- Logs includes daily logs describing the scraping taking place
