#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 10:25:29 2019

@author: allison
"""

import urllib
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup
from dataclasses import dataclass


def getsp1(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    
    headers={'User-Agent':user_agent,} 
    
    request=urllib.request.Request(url,None,headers) #The assembled request
    response = urllib.request.urlopen(request)
    
    a = response.read().decode('utf-8', 'ignore')
    sp = soup(a, 'html.parser')
    return sp



def outcome_info(game_id, league):
    """Using data from ESPN.com to update the final score, winner of the game"""
    
    if league == 'NFL':
        base_link = 'https://www.espn.com/nfl/game/_/gameId/'
    elif league == 'NCAAF':
        base_link = 'https://www.espn.com/college-football/game/_/gameId/'
    elif league == 'MLB':
        base_link = 'https://www.espn.com/mlb/game?gameId='
    
    link = base_link + str(game_id)
        
    sp1 = getsp1(link)
    
    # checking if the game is over or not
    is_final = sp1.find_all('span', attrs={'class':'game-time status-detail'})
    if is_final == []:
        is_final = None
    else:
        is_final = is_final[0].get_text()
    
    
    #if is_final != 'Final':
    if 'Final' not in str(is_final):
        raise ValueError('Game is not final.')
    
    # getting the final score of the game
    away_score = sp1.find_all('div', attrs={'class':'score icon-font-after'})
    away_score = away_score[0].get_text()
    if len(away_score) == 0:
        away_score = None
    
    home_score = sp1.find_all('div', attrs={'class':'score icon-font-before'})
    home_score = home_score[0].get_text()
    if len(home_score) == 0:
        home_score = None

    return away_score, home_score




def update(df):
    num_rows = df.shape[0]
    
    for i in range(num_rows):
        if df.Outcome.isnull()[i] == True or df['Home Score'].isnull()[i] == True:
            if df['ESPN ID'][i] != 'False':
                try:
                    away_score, home_score = outcome_info(df['ESPN ID'][i], df.League[i])
                    df.loc[i, 'Away Score'] = away_score
                    df.loc[i, 'Home Score'] = home_score
                    
                    if df['Bet Type'][i] == 'Money Line':
                        if int(home_score) > int(away_score):
                            winner = df['Home Team'][i]
                        else:
                            winner = df['Away Team'][i]
                        
                        if winner == df.Pick[i]:
                            df.Outcome[i] = 'Win'
                        else: 
                            df.Outcome[i] = 'Loss'
                    
                    elif df['Bet Type'][i] == 'Spread':
                        if df['Away Team'][i] == df['Pick'][i]:
                            picked_team = 'away'
                        else:
                            picked_team = 'home'
                        
                        if picked_team == 'home':
                            if int(home_score) + df['Spread'][i] > int(away_score):
                                win_spread = True
                            else:
                                win_spread = False
                        
                        if picked_team == 'away':
                            if int(away_score) + df['Spread'][i] > int(home_score):
                                win_spread = True
                            else:
                                win_spread = False
                        
                        if win_spread:
                            df.Outcome[i] = 'Win'
                        else:
                            df.Outcome[i] = 'Loss'
                            
                    elif df['Bet Type'][i] == 'Prop':
                        pick = df['Pick'][i]
                        if '&' in pick and df['ESPN ID'][i] != False:
                            for item in pick.split():
                                try:
                                    total = float(item)
                                except:
                                    print('{} not a number'.format(item))
                            
                            if 'under' in pick.split():
                                over_under = 'under'
                            else:
                                over_under = 'over'
                            print(over_under, total)
                            
                            
                            if int(df['Home Score'][i]) + int(df['Away Score'][i]) > total:
                                if over_under == 'over':
                                    df.Outcome[i] = 'Win'
                                else:
                                    df.Outcome[i] = 'Loss'
                                
                            else:
                                if over_under == 'over':
                                    df.Outcome[i] = 'Loss'
                                else:
                                    df.Outcome[i] = 'Win'

                except ValueError:
                    print("{} vs {} has not ended yet.".format(df['Home Team'][i], df['Away Team'][i]))
    
    return df

