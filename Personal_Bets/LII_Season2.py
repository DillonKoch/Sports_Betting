#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 10:28:19 2019

@author: allison

web scraping for lock it in data
"""

import urllib
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup
from dataclasses import dataclass
import datetime

def d(month, day):
    return datetime.date(2019, month, day)

def getsp1(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    
    headers={'User-Agent':user_agent,} 
    
    request=urllib.request.Request(url,None,headers) #The assembled request
    response = urllib.request.urlopen(request)
    
    a = response.read().decode('utf-8', 'ignore')
    sp = soup(a, 'html.parser')
    return sp


def hockey_info(game_id):
    """Acts like the game_info() function, but for hockey since their HTML is different"""
    link = 'https://www.espn.com/nhl/game/_/gameId/' + str(game_id)
    sp1 = getsp1(link)
    
    team_names = sp1.find_all('div', attrs={'class':'ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db'})
    away_full, home_full = [item.get_text() for item in team_names]
    
    records = sp1.find_all('div', attrs={'class':'Gamestrip__Record db n10 clr-gray-04'})
    away_record, home_record = [item.get_text() for item in records]
    
    return home_full, away_full, home_record, away_record, 'NHL'

def hockey_outcome_info(game_id):
    """Acts like the outcome_info() function, but for hockey since their HTML is different"""
    link = 'https://www.espn.com/nhl/game/_/gameId/' + str(game_id)
    sp1 = getsp1(link)
    
    scores = sp1.find_all('div', attrs={'class':'Gamestrip__Score relative tc w-100 fw-heavy h2 clr-gray-01'})
    away_score, home_score = [item.get_text() for item in scores]
    
    return away_score, home_score

def game_info(game_id, league='NFL'):
    """Using data from ESPN.com to fill in game info, instead of typing it out"""
    
    if league == 'NFL':
        base_link = 'https://www.espn.com/nfl/game/_/gameId/'
    elif league == 'NCAAF':
        base_link = 'https://www.espn.com/college-football/game/_/gameId/'
    elif league == 'MLB':
        base_link = 'https://www.espn.com/mlb/game?gameId='
    elif league == 'NHL':
        return hockey_info(game_id)
    
    link = base_link + str(game_id)
        
    sp1 = getsp1(link)
    
    # Getting home and away team locations and team names:
        # locations
    home_away_loc = sp1.find_all('span', attrs={'class':'long-name'})
    home_loc = home_away_loc[1].get_text()
    away_loc = home_away_loc[0].get_text()
        # team names
    home_away_name = sp1.find_all('span', attrs={'class':'short-name'})
    home_name = home_away_name[1].get_text()
    away_name = home_away_name[0].get_text()
        # locations + names
    home_full = home_loc + ' ' + home_name
    away_full = away_loc + ' ' + away_name
    
    
    # records
    record_info = sp1.find_all('div', attrs={'class':'record'})
    
    away_record = record_info[0].get_text()
    home_record = record_info[1].get_text()
    
    return home_full, away_full, home_record, away_record, league


def outcome_info(game_id, league):
    """Using data from ESPN.com to update the final score, winner of the game"""
    
    if league == 'NFL':
        base_link = 'https://www.espn.com/nfl/game/_/gameId/'
    elif league == 'NCAAF':
        base_link = 'https://www.espn.com/college-football/game/_/gameId/'
    elif league == 'MLB':
        base_link = 'https://www.espn.com/mlb/game?gameId='
    elif league == 'NHL':
        return hockey_outcome_info(game_id)
    
    link = base_link + str(game_id)
        
    sp1 = getsp1(link)
    
    # checking if the game is over or not
    is_final = sp1.find_all('span', attrs={'class':'game-time status-detail'})
    if is_final == []:
        is_final = None
    else:
        is_final = is_final[0].get_text()
    
    if is_final != 'Final':
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






@dataclass
class Bettor:
    name: str
    job: str
    
    def __post_init__(self):
        self.numBets = 0
        self.allBets = pd.DataFrame(columns = ['Bettor', 'Bet ID', 'Parlay No.', 'Bet Type', 'Bet Date', 'Gameday',
                                               'Bet', 'To Win', 'Home Team', 'Home Record', 'Away Team', 'Away Record',
                                               'Pick', 'Home Score', 'Away Score', 'Spread', 'Money Line', 'League', 'Outcome', 'ESPN ID'])

    
    
    def betSpread(self, bet_date, game_date, bet, to_win, pick, spread, espn_id, isParlay=False, parlayNo=None, league='NFL', moneyLine=None, 
                  home_name=None, away_name=None, home_record=None, away_record=None):
        if not isParlay:
            self.numBets += 1
        
        if espn_id != False:
            home_name, away_name, home_record, away_record, league = game_info(espn_id, league)
        
        if pick == 1:
            pick = home_name
        else:
            pick = away_name
        
        newRow = [self.name, self.numBets, parlayNo, 'Spread', bet_date, game_date, bet, to_win, home_name, home_record, away_name, away_record,
                  pick, None, None, spread, moneyLine, league, None, espn_id]
        
        self.allBets.loc[len(self.allBets)] = newRow
        
        
    def betMoneyLine(self, bet_date, game_date, bet, to_win, pick, moneyLine, espn_id, isParlay=False, parlayNo=None, league='NFL', home_name=None, 
                     away_name=None, home_record=None, away_record=None):
        if not isParlay:
            self.numBets += 1
        
        if espn_id != False:
            home_name, away_name, home_record, away_record, league = game_info(espn_id, league)
        
        if pick == 1:
            pick = home_name
        else:
            pick = away_name
        
        newRow = [self.name, self.numBets, parlayNo, 'Money Line', bet_date, game_date, bet, to_win, home_name, home_record, away_name, away_record,
                  pick, None, None, None, moneyLine, league, None, espn_id]   
        
        self.allBets.loc[len(self.allBets)] = newRow
        

    def betProp(self, bet_date, game_date, bet, to_win, pick, moneyLine, espn_id=False, outcome=None, isParlay=False, parlayNo=None, league='NFL',
                home_name=None, away_name=None, home_record=None, away_record=None):
        if not isParlay:
            self.numBets += 1

        if espn_id != False:
            home_name, away_name, home_record, away_record, league = game_info(espn_id, league)
        
        newRow = [self.name, self.numBets, parlayNo, 'Prop', bet_date, game_date, bet, to_win, home_name, home_record, away_name, away_record,
                  pick, None, None, None, moneyLine, league, outcome, espn_id]
        
        self.allBets.loc[len(self.allBets)] = newRow
        
    
    def betParlay(self, *args):
        """Insert one list for every bet in the parlay. The first element of the list should be the type of bet (prop/money line/spread).
        The second element of the list should be the arguments that could be used in one of the corresponding methods for the bet type.
        
        
        Spread: ['Spread', [bet_date, game_date, bet, to_win, pick, spread, espn_id, league='NFL', moneyLine=None]]
        
        Money Line: ['Money Line', [bet_date, game_date, bet, to_win, pick, moneyLine, espn_id, league='NFL']]
        
        Prop: ['Prop', [bet_date, game_date, bet, to_win, pick, moneyLine, espn_id, league='NFL']]
        
        """
        self.numBets += 1
        
        bet = 1
        total = len(args)
        for arg in args:
            arg[1] += [True, str(bet) + '/' + str(total)]
            if arg[0] == 'Spread':
                self.betSpread(*arg[1])
            elif arg[0] == 'Money Line':
                self.betMoneyLine(*arg[1])
            elif arg[0] == 'Prop':
                self.betProp(*arg[1])
            else:
                raise ValueError("Incorrect input!")
            
            bet += 1


    def update(self):
        num_rows = self.allBets.shape[0]
        
        for i in range(num_rows):
            if self.allBets.Outcome[i] == None or self.allBets['Home Score'][i] == None:
                if self.allBets['ESPN ID'][i] != False:
                    try:
                        away_score, home_score = outcome_info(self.allBets['ESPN ID'][i], self.allBets.League[i])
                        self.allBets.loc[i, 'Away Score'] = away_score
                        self.allBets.loc[i, 'Home Score'] = home_score
                        
                        if self.allBets['Bet Type'][i] == 'Money Line':
                            if int(home_score) > int(away_score):
                                winner = self.allBets['Home Team'][i]
                            else:
                                winner = self.allBets['Away Team'][i]
                            
                            if winner == self.allBets.Pick[i]:
                                self.allBets.Outcome[i] = 'Win'
                            else: 
                                self.allBets.Outcome[i] = 'Loss'
                        
                        elif self.allBets['Bet Type'][i] == 'Spread':
                            if self.allBets['Away Team'][i] == self.allBets['Pick'][i]:
                                picked_team = 'away'
                            else:
                                picked_team = 'home'
                            
                            if picked_team == 'home':
                                if int(home_score) + self.allBets['Spread'][i] > int(away_score):
                                    win_spread = True
                                else:
                                    win_spread = False
                            
                            if picked_team == 'away':
                                if int(away_score) + self.allBets['Spread'][i] > int(home_score):
                                    win_spread = True
                                else:
                                    win_spread = False
                            
                            if win_spread:
                                self.allBets.Outcome[i] = 'Win'
                            else:
                                self.allBets.Outcome[i] = 'Loss'
                                
                        elif self.allBets['Bet Type'][i] == 'Prop':
                            pick = self.allBets['Pick'][i]
                            if '&' in pick and self.allBets['ESPN ID'][i] != False:
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
                                
                                
                                if int(self.allBets['Home Score'][i]) + int(self.allBets['Away Score'][i]) > total:
                                    if over_under == 'over':
                                        self.allBets.Outcome[i] = 'Win'
                                    else:
                                        self.allBets.Outcome[i] = 'Loss'
                                    
                                else:
                                    if over_under == 'over':
                                        self.allBets.Outcome[i] = 'Loss'
                                    else:
                                        self.allBets.Outcome[i] = 'Win'
                                
                        
                        
                        
                                            
                    except ValueError:
                        print("{} vs {} has not ended yet.".format(self.allBets['Home Team'][i], self.allBets['Away Team'][i]))






