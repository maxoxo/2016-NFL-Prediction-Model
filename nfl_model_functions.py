# functions.py

# load libraries
import pandas as pd
import numpy as np
import math


### Necessary functions & values
# - prob_win
# - simulate_game
# - k value
# - Expectation function (E)
# - mov_multiplier
# - update_ratings
# - divisions and conferences


### prob_win function ----------------------------------------------------------------------------------------------------
def prob_win(elo, elo_opponent):
    
    elo_diff = elo - elo_opponent    
    prob = 1 / (10**(-elo_diff/400.) + 1)
    return prob


### simulate_game function ----------------------------------------------------------------------------------------------------
def simulate_game(ratings, home, away):
    
    # Pull in necessary data
    home_elo = ratings['ratings'][home]
    away_elo = ratings['ratings'][away]
    home_spread = -1 * round( 2* ((home_elo + 65) - away_elo)/25. ) / 2.
    
    # Simulate the game
    result_minus_spread = np.random.normal(loc=0, scale=13.8, size=1)

    # Who won the game?
    result = result_minus_spread + home_spread
    
    if result < 0:
        winner = home
    else:
        winner = away
    

    return (winner, result[0]) 


### simulate_game function ----------------------------------------------------------------------------------------------------
def simulate_neutral_game(ratings, home, away):
    
    # Pull in necessary data
    home_elo = ratings['ratings'][home]
    away_elo = ratings['ratings'][away]
    home_spread = -1 * round( 2* (home_elo - away_elo)/25. ) / 2.
    
    # Simulate the game
    result_minus_spread = np.random.normal(loc=0, scale=13.8, size=1)

    # Who won the game?
    result = result_minus_spread + home_spread
    
    if result < 0:
        winner = home
    else:
        winner = away
    

    return (winner, result[0])   

### k value -------------------------------------------------------------------------------------------------------------------------- 
k = 20


### Expectation Functions ------------------------------------------------------------------------------------------------------------
def E(R1, R2):
    return float(R1) / (R1 + R2)


### mov_multiplier function ----------------------------------------------------------------------------------------------------------
def mov_mult(mov, elo_w, elo_l):
    return math.log(abs(mov) + 1) * (2.2 / ((elo_w - elo_l) * 0.001 + 2.2))


### update_ratings function ----------------------------------------------------------------------------------------------------------
def update_ratings(ratings, home, away, mov):
    
    elo_home = ratings['ratings'][home]
    elo_away = ratings['ratings'][away]

    R_home = 10**(elo_home/400)
    R_away = 10**(elo_away/400)
        
    if mov < 0:
        
        S_home = 1
        S_away = 0
        
        E_home = E(R_home, R_away)
        elo_w = elo_home + 65
        elo_l = elo_away
        mult = mov_mult(mov, elo_w, elo_l)
        change = k * mult * (S_home - E_home)
        
        elo_home_new = elo_home + change
        elo_away_new = elo_away - change
        
    else:
        
        S_home = 0
        S_away = 1
        
        E_away = E(R_away, R_home)
        elo_w = elo_away
        elo_l = elo_home + 65
        mult = mov_mult(mov, elo_w, elo_l)
        change = k * mult * (S_away - E_away)
    
        elo_home_new = elo_home - change
        elo_away_new = elo_away + change
         
    ratings['ratings'][home] = round(elo_home_new, 0)
    ratings['ratings'][away] = round(elo_away_new, 0)


### Group every team by division and conference -----------------------------------------------------------------------

afc_east = ['Buffalo Bills', 'Miami Dolphins', 'New England Patriots', 'New York Jets']
afc_west = ['Denver Broncos', 'Kansas City Chiefs', 'Oakland Raiders', 'San Diego Chargers']
afc_north = ['Baltimore Ravens', 'Cincinnati Bengals', 'Cleveland Browns', 'Pittsburgh Steelers']
afc_south = ['Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Tennessee Titans']

nfc_east = ['Dallas Cowboys', 'New York Giants', 'Philadelphia Eagles', 'Washington Redskins']
nfc_west = ['Arizona Cardinals', 'Los Angeles Rams', 'San Francisco 49ers', 'Seattle Seahawks']
nfc_north = ['Chicago Bears', 'Detroit Lions', 'Green Bay Packers', 'Minnesota Vikings']
nfc_south = ['Atlanta Falcons', 'Carolina Panthers', 'New Orleans Saints', 'Tampa Bay Buccaneers']

afc = afc_east + afc_west + afc_north + afc_south
nfc = nfc_east + nfc_west + nfc_north + nfc_south