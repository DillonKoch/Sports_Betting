# import re
# leagues = ['NFL', 'NBA', 'NCAAF', 'NCAAB']

# dfs = []
# for league in leagues:
#     path = ROOT_PATH + f"/ESB/Data/{league}/Futures.csv"
#     df = pd.read_csv(path)

#     odds_comp = re.compile(r"((O|U) \d{1,2}\.{0,1}\d{0,1})\(((\+|-){0,1}\d{3})\)")
#     odds = list(df['Odds'].astype(str))
#     odds = [odd.replace('even', '100') for odd in odds]
#     bets = list(df['Bet'])
#     new_odds = []
#     new_bets = []
#     for bet, odd in zip(bets, odds):
#         match = re.match(odds_comp, odd)
#         if match is not None:
#             print(match.group(1))
#             new_bet = match.group(1)
#             new_odd = match.group(3)
#         else:
#             new_odd = odd
#             new_bet = bet

#         new_odds.append(new_odd)
#         new_bets.append(new_bet)

#     df['Odds'] = pd.Series(new_odds)
#     df['Bet'] = pd.Series(new_bets)
#     df.to_csv(path)

# ----------------------------------------------------------------------------------
leagues = ['NFL', 'NBA', 'NCAAF', 'NCAAB']

dfs = []
for league in leagues:
    path = ROOT_PATH + f"/ESB/Data/{league}/Futures.csv"
    df = pd.read_csv(path)

    cols = ['Title', 'Description', 'Bet']
    for col in cols:
        df[col] = df[col].astype(str)
        vals = list(df[col])
        new_vals = [val.replace('\n', '').replace('\t', '') for val in vals]
        df[col] = pd.Series(new_vals)
    df.to_csv(path, index=False)
