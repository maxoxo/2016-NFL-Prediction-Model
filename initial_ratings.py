# initial_ratings.py

# Load all the necessary library
import pandas as pd
import numpy as np
import math as math
import random
import settings
from functions import *
import csv
import os





def ratings_dict(data):
    '''
        Generate a empty dictionary to be filled with ratings for all 32 teams from 2000
        to present. All team teams except for the Houston Texans will start with an 
        initial rating of 1500 for week 1 of the 2000 NFL season. The Texans rating will 
        be initialize at 1500 for week 1 of the 2002 NFL season, the year they were enfranchised.
    '''

    ratings = {}
    for team in teams:
        ratings[team] = {}
        if team != 'Houston Texans':
            ratings[team][1] = 1500
            for i in range(2, data['week_id'].max() + 2):
                ratings[team][i] = None
        else:
            ratings[team][43] = 1500
            for i in range(44, data['week_id'].max() + 2):
                ratings[team][i] = None
    return ratings

def hist_ratings(data, ratings):
    
    season_prev = 2000 
        
    for i in range(data.shape[0]):
        
        # Store data to variables
        home = data['home'][i]
        away = data['away'][i]
        home_pts = data['home_pts'][i]
        away_pts = data['away_pts'][i]
        week_id = data['week_id'][i]
        week = data['week'][i]
        season = data['season'][i]
        
        
        
        ### HOME RATINGS ###
        if ratings[home][week_id]:
            home_elo = ratings[home][week_id]
        
        elif ratings[home][(week_id-1)]:
            ratings[home][week_id] = ratings[home][(week_id-1)]
            home_elo = ratings[home][week_id]
        
        elif ratings[home][(week_id-2)]:
            ratings[home][week_id] = ratings[home][(week_id-2)]
            ratings[home][(week_id-1)] = ratings[home][(week_id-2)]
            home_elo = ratings[home][week_id]
        
        elif ratings[home][(week_id-3)]:
            ratings[home][week_id] = ratings[home][(week_id-3)]
            ratings[home][(week_id-1)] = ratings[home][(week_id-3)]
            ratings[home][(week_id-2)] = ratings[home][(week_id-3)]
            home_elo = ratings[home][week_id]   
        
        elif ratings[home][(week_id-4)]:
            ratings[home][week_id] = ratings[home][(week_id-4)]
            ratings[home][(week_id-1)] = ratings[home][(week_id-4)]
            ratings[home][(week_id-2)] = ratings[home][(week_id-4)]
            ratings[home][(week_id-3)] = ratings[home][(week_id-4)]
            home_elo = ratings[home][week_id] 
        
        else:
            ratings[home][week_id] = ratings[home][(week_id-5)]
            ratings[home][(week_id-1)] = ratings[home][(week_id-5)]
            ratings[home][(week_id-2)] = ratings[home][(week_id-5)]
            ratings[home][(week_id-3)] = ratings[home][(week_id-5)]
            ratings[home][(week_id-4)] = ratings[home][(week_id-5)]
            home_elo = ratings[home][week_id] 
        
        
        ### AWAY RATINGS ###
        if ratings[away][week_id]:
            away_elo = ratings[away][week_id]
        
        elif ratings[away][(week_id-1)]:
            ratings[away][week_id] = ratings[away][(week_id-1)]
            away_elo = ratings[away][week_id]
        
        elif ratings[away][(week_id-2)]:
            ratings[away][week_id] = ratings[away][(week_id-2)]
            ratings[away][(week_id-1)] = ratings[away][(week_id-2)]
            away_elo = ratings[away][week_id]
        
        elif ratings[away][(week_id-3)]:
            ratings[away][week_id] = ratings[away][(week_id-3)]
            ratings[away][(week_id-1)] = ratings[away][(week_id-3)]
            ratings[away][(week_id-2)] = ratings[away][(week_id-3)]
            away_elo = ratings[away][week_id]   
        
        elif ratings[away][(week_id-4)]:
            ratings[away][week_id] = ratings[away][(week_id-4)]
            ratings[away][(week_id-1)] = ratings[away][(week_id-4)]
            ratings[away][(week_id-2)] = ratings[away][(week_id-4)]
            ratings[away][(week_id-3)] = ratings[away][(week_id-4)]
            ratings[away][(week_id-3)] = ratings[away][(week_id-4)]
            away_elo = ratings[away][week_id] 
        
        

        home_new, away_new = update_ratings(week, home_elo, home_pts, away_elo, away_pts)

        # Update ratings dictioary
        ratings[home][(week_id+1)] = home_new
        ratings[away][(week_id+1)] = away_new
        
        
        
        #### If it is the end of the season fill in all the None type values
        if week_id in open_week_ids and season != season_prev:
            
            for team in ratings:

                for i in ratings[team]:

                    if i > week_id:
                        continue

                    if ratings[team][i]:
                        continue

                    elif ratings[team][(i-1)]:
                        ratings[team][i] = ratings[team][(i-1)]

                    elif ratings[team][(i-2)]:
                        ratings[team][i] = ratings[team][(i-2)]
                        ratings[team][(i-1)] = ratings[team][(i-1)]

                    elif ratings[team(i-3)]:
                        ratings[team][i] = ratings[team][(i-3)]
                        ratings[team][(i-1)] = ratings[team][(i-3)]
                        ratings[team][(i-2)] = ratings[team][(i-3)]

                    elif ratings[team(i-4)]:
                        ratings[team][i] = ratings[team][(i-4)]
                        ratings[team][(i-1)] = ratings[team][(i-4)]
                        ratings[team][(i-2)] = ratings[team][(i-4)]
                        ratings[team][(i-2)] = ratings[team][(i-4)]

            for team in teams:
                if week_id in ratings[team]:
                    ratings[team][week_id] = revert2mean(ratings[team][week_id])
        
        season_prev = season
    
    return ratings

def fill_gaps(ratings):
    '''
    There will be gaps in the ratings dictionary for teams who did not play due to having a bye
    week or not qualifying for a particular round of the playoffs.
    '''
    for team in ratings:

        for i in ratings[team]:

            if ratings[team][i]:
                continue

            elif ratings[team][(i-1)]:
                ratings[team][i] = ratings[team][(i-1)]

            elif ratings[team][(i-2)]:
                ratings[team][i] = ratings[team][(i-2)]
                ratings[team][(i-1)] = ratings[team][(i-1)]

            elif ratings[team(i-3)]:
                ratings[team][i] = ratings[team][(i-3)]
                ratings[team][(i-1)] = ratings[team][(i-3)]
                ratings[team][(i-2)] = ratings[team][(i-3)]

            elif ratings[team(i-4)]:
                ratings[team][i] = ratings[team][(i-4)]
                ratings[team][(i-1)] = ratings[team][(i-4)]
                ratings[team][(i-2)] = ratings[team][(i-4)]
                ratings[team][(i-2)] = ratings[team][(i-4)]
    return ratings

def revert_current(ratings):
    for team in ratings:
        ratings[team][337] = revert2mean(ratings[team][337])
    return ratings

def write_hist_ratings():
    f = open(os.path.join(settings.PROCESSED_DATA_DIR, 'historical_ratings.csv'), 'wb')
    csv_out = csv.writer(f)
    csv_out.writerow(['team', 'week_id', 'rating'])

    for team in ratings:
        for i in ratings[team]:
            csv_out.writerow([team, i, ratings[team][i]])

    f.close()

def write_2016_init_ratings():
    f = open(os.path.join(settings.PROCESSED_DATA_DIR, 'initial_ratings_2016.csv'), 'wb')
    csv_out = csv.writer(f)
    csv_out.writerow(['team', 'ratings'])

    for team in ratings:
        csv_out.writerow([team, ratings[team][337]])
    f.close()



if __name__ == "__main__":
    
    # Read the processed game data file into Python.
    results_df = pd.read_csv(os.path.join(settings.DATA_DIR, 'all_game_results.csv'))

    # Save the names of all 32 NFL teams to an array.
    teams = results_df.home.unique()

    # Save the week_ids of each opening game week to an array
    
    open_week_ids = [(21*n+1) for n in range(1,17)]
    ratings = ratings_dict(results_df)
    ratings = hist_ratings(results_df, ratings)
    ratings = fill_gaps(ratings)
    ratings = revert_current(ratings)
    write_hist_ratings()
    write_2016_init_ratings()
