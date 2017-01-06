# load necessary libraries
import pandas as pd
import numpy as np
import math, os, sys, csv
import settings
from nfl_model_functions import *
from collections import Counter



# Pull in the current ratings, update them, and save the initial
def ratings_dict_init():
    ratings_df = pd.read_csv(os.path.join(settings.PROCESSED_DATA_DIR, 'initial_ratings_2016.csv'))
    ratings = ratings_df.set_index('team').to_dict()
    ratings['ratings']['Los Angeles Rams'] = ratings['ratings']['St. Louis Rams']
    del ratings['ratings']['St. Louis Rams']
    return ratings

def season_results_dict_init():
    season_results = {}
    for team in teams:
        season_results[team] = {}
        for sim in range(1, (settings.SIMULATIONS+1)):
            season_results[team][sim] = 0
    return season_results
        
def pt_diff_dict_init():
    pt_diff = {}
    for team in teams:
        pt_diff[team] = {}
        for sim in range(1, (settings.SIMULATIONS+1)):
            pt_diff[team][sim] = 0
    return pt_diff

def current_record_init():
    current_record = {}
    for team in teams:
        current_record[team] = {}
        current_record[team]['w'] = 0
        current_record[team]['l'] = 0
        current_record[team]['t'] = 0
    return current_record

def loop_thru_results(pt_diff, season_results, current_record, ratings):
    
    for i in range(results.shape[0]):

        # Store data to variables
        home = results['home'][i]
        away = results['away'][i]
        home_pts = results['home_pts'][i]
        away_pts = results['away_pts'][i]
        week = results['week'][i]

        mov = away_pts - home_pts

        # Update the point differential dictionary for each simulation.
        for sim in range(1, (settings.SIMULATIONS+1)):
            pt_diff[home][sim] += -1 * mov
            pt_diff[away][sim] += mov

        # Update the game results dictionary for each simulation
        
        # HOME WIN 
        if mov < 0:
            current_record[home]['w'] += 1
            current_record[away]['l'] += 1
            for sim in range(1, (settings.SIMULATIONS+1)):
                season_results[home][sim] += 1
        # TIE GAME
        elif mov == 0:
            current_record[home]['t'] += 1
            current_record[away]['t'] += 1
            for sim in range(1, (settings.SIMULATIONS+1)):
                season_results[home][sim] += 0.5
                season_results[away][sim] += 0.5
        # AWAY WIN
        else:
            current_record[home]['l'] += 1
            current_record[away]['w'] += 1
            for sim in range(1, (settings.SIMULATIONS+1)):
                season_results[away][sim] += 1

        # Update the ratings dicitonary
        update_ratings(ratings, home, away, mov)

    return ratings, current_record, season_results, pt_diff

def weekly_predictions():
    
    #This function will generate probabilistic predictions and point spreads
    #estimates for each game for the upcoming week and write the results to
    #a csv file.


    current_week = data[data.week == int(Week)]

    home_probs = []
    away_probs = []
    home_spreads = []
    away_spreads = []
    home_ratings = [ratings['ratings'][team] for team in current_week.home]
    away_ratings = [ratings['ratings'][team] for team in current_week.away]

    for i in range(current_week.shape[0]):
        
        home = current_week.home[i]
        away = current_week.away[i]
        
        home_elo = ratings['ratings'][home]
        away_elo = ratings['ratings'][away]

        home_prob = prob_win(home_elo + 65, away_elo)
        away_prob = prob_win(away_elo, home_elo + 65)
        
        home_spread = -1 * round( 2* ((home_elo + 65) - away_elo)/25. ) / 2.
        away_spread = -1 * round( 2 * (away_elo - (home_elo + 65))/25.) / 2.
        
        home_probs.append(home_prob)
        away_probs.append(away_prob)
        home_spreads.append(home_spread)
        away_spreads.append(away_spread)
        

    ### Add point spreads and win probabilities
    current_week['home_prob'] = home_probs
    current_week['home_spread'] = home_spreads
    current_week['home_elo'] = home_ratings
    current_week['away_prob'] = away_probs
    current_week['away_spread'] = away_spreads
    current_week['away_elo'] = away_ratings

    # Write to csv
    current_week.to_csv(os.path.join(settings.PROCESSED_DATA_DIR, week_dir, 'weekly_predictions.csv'))

def run_simulations():
    i = 1
    teams = data.home.unique()
    division_winners = []
    playoffs = []
    bye_round = []
    super_bowl = []
    champs = []

    while i <= settings.SIMULATIONS:
        
        
        # Re-set ratings dictionary after each simulation.
        ratings = {}
        ratings['ratings'] = {}
        for team in ratings_0['ratings']:
            ratings['ratings'][team] = ratings_0['ratings'][team]
        
        
        winners = []
        for j in range(data.shape[0]):

            home = data.home[j]
            away = data.away[j]
            home_elo = ratings['ratings'][home]
            away_elo = ratings['ratings'][away]
     
            winner, mov = simulate_game(ratings, home, away)
            winners.append(winner)
            
            update_ratings(ratings, home, away, mov)
            pt_diff[home][i] += (-1 * mov)
            pt_diff[away][i] += mov
        
        
        # Count up each team's win total
        team_wins = dict(Counter(winners))
           
        for team in teams:
            if team not in team_wins:
                team_wins[team] = 0
            team_wins[team] += season_results[team][i]
        

        for team in teams:
            season_results[team][i] = team_wins[team]
        
        ##################################
        # Divide teams by their division # ------------------------------------------------------------------------
        ##################################
        
        # AFC East
        afc_east_d = {key:value for key,value in team_wins.items() if key in afc_east}
        afc_east_df = pd.DataFrame([[key, value] for key,value in afc_east_d.iteritems()], columns=['team', 'wins'])
        
        # AFC West 
        afc_west_d = {key:value for key,value in team_wins.items() if key in afc_west}
        afc_west_df = pd.DataFrame([[key, value] for key,value in afc_west_d.iteritems()], columns=['team', 'wins'])
        
        # AFC North
        afc_north_d = {key:value for key,value in team_wins.items() if key in afc_north}
        afc_north_df = pd.DataFrame([[key, value] for key,value in afc_north_d.iteritems()], columns=['team', 'wins'])
        
        # AFC South
        afc_south_d = {key:value for key,value in team_wins.items() if key in afc_south}
        afc_south_df = pd.DataFrame([[key, value] for key,value in afc_south_d.iteritems()], columns=['team', 'wins'])
        
        # NFC East
        nfc_east_d = {key:value for key,value in team_wins.items() if key in nfc_east}
        nfc_east_df = pd.DataFrame([[key, value] for key,value in nfc_east_d.iteritems()], columns=['team', 'wins'])
        
        # NFC West
        nfc_west_d = {key:value for key,value in team_wins.items() if key in nfc_west}
        nfc_west_df = pd.DataFrame([[key, value] for key,value in nfc_west_d.iteritems()], columns=['team', 'wins'])
        
        # NFC North
        nfc_north_d = {key:value for key,value in team_wins.items() if key in nfc_north}
        nfc_north_df = pd.DataFrame([[key, value] for key,value in nfc_north_d.iteritems()], columns=['team', 'wins'])
        
        # NFC South
        nfc_south_d = {key:value for key,value in team_wins.items() if key in nfc_south}
        nfc_south_df = pd.DataFrame([[key, value] for key,value in nfc_south_d.iteritems()], columns=['team', 'wins'])
        
        
        ############################
        ##### Division Winners ##### --------------------------------------------------------------------------
        ############################

        nfc_north_champs = np.random.choice(pd.Series(nfc_north_df.loc[nfc_north_df.wins == max(nfc_north_df.wins), 'team']))
        nfc_south_champs = np.random.choice(pd.Series(nfc_south_df.loc[nfc_south_df.wins == max(nfc_south_df.wins), 'team']))
        nfc_east_champs = np.random.choice(pd.Series(nfc_east_df.loc[nfc_east_df.wins == max(nfc_east_df.wins), 'team']))
        nfc_west_champs = np.random.choice(pd.Series(nfc_west_df.loc[nfc_west_df.wins == max(nfc_west_df.wins), 'team']))
        afc_north_champs = np.random.choice(pd.Series(afc_north_df.loc[afc_north_df.wins == max(afc_north_df.wins), 'team']))
        afc_south_champs = np.random.choice(pd.Series(afc_south_df.loc[afc_south_df.wins == max(afc_south_df.wins), 'team']))
        afc_east_champs = np.random.choice(pd.Series(afc_east_df.loc[afc_east_df.wins == max(afc_east_df.wins), 'team']))
        afc_west_champs = np.random.choice(pd.Series(afc_west_df.loc[afc_west_df.wins == max(afc_west_df.wins), 'team']))
        

        ################################################
        ##### Assign seeds to the division winners #####
        ################################################
        
        nfc_div_winners_d = {key:value for key,value in team_wins.items() if key in [nfc_north_champs, nfc_south_champs, nfc_east_champs, nfc_west_champs]}
        nfc_div_winners_df = pd.DataFrame([[key, value] for key,value in nfc_div_winners_d.iteritems()], columns=['team', 'wins'])
        afc_div_winners_d = {key:value for key,value in team_wins.items() if key in [afc_north_champs, afc_south_champs, afc_east_champs, afc_west_champs]}
        afc_div_winners_df = pd.DataFrame([[key, value] for key,value in afc_div_winners_d.iteritems()], columns=['team', 'wins'])
        
        ### NFC Seeding
        nfc_seed1 = np.random.choice(pd.Series(nfc_div_winners_df.loc[nfc_div_winners_df.wins == max(nfc_div_winners_df.wins), 'team']))
        nfc_div_winners_df = nfc_div_winners_df[nfc_div_winners_df['team'] != nfc_seed1]
        nfc_seed2 = np.random.choice(pd.Series(nfc_div_winners_df.loc[nfc_div_winners_df.wins == max(nfc_div_winners_df.wins), 'team']))
        nfc_div_winners_df = nfc_div_winners_df[nfc_div_winners_df['team'] != nfc_seed2]
        nfc_seed3 = np.random.choice(pd.Series(nfc_div_winners_df.loc[nfc_div_winners_df.wins == max(nfc_div_winners_df.wins), 'team']))
        nfc_div_winners_df = nfc_div_winners_df[nfc_div_winners_df['team'] != nfc_seed3]
        nfc_seed4 = np.random.choice(pd.Series(nfc_div_winners_df.loc[nfc_div_winners_df.wins == max(nfc_div_winners_df.wins), 'team']))

        ### AFC Seeding
        afc_seed1 = np.random.choice(pd.Series(afc_div_winners_df.loc[afc_div_winners_df.wins == max(afc_div_winners_df.wins), 'team']))
        afc_div_winners_df = afc_div_winners_df[afc_div_winners_df['team'] != afc_seed1]
        afc_seed2 = np.random.choice(pd.Series(afc_div_winners_df.loc[afc_div_winners_df.wins == max(afc_div_winners_df.wins), 'team']))
        afc_div_winners_df = afc_div_winners_df[afc_div_winners_df['team'] != afc_seed2]
        afc_seed3 = np.random.choice(pd.Series(afc_div_winners_df.loc[afc_div_winners_df.wins == max(afc_div_winners_df.wins), 'team']))
        afc_div_winners_df = afc_div_winners_df[afc_div_winners_df['team'] != afc_seed3]
        afc_seed4 = np.random.choice(pd.Series(afc_div_winners_df.loc[afc_div_winners_df.wins == max(afc_div_winners_df.wins), 'team']))

        ###########################
        ##### Wild Card Teams #####
        ###########################
        
        # Which teams did not win their division?
        afc_remain = [x for x in afc if x not in [afc_south_champs, afc_north_champs, afc_east_champs, afc_west_champs]]
        nfc_remain = [x for x in nfc if x not in [nfc_south_champs, nfc_north_champs, nfc_east_champs, nfc_west_champs]]
        
        # NFC Remain DF
        nfc_remain_d = {key:value for key,value in team_wins.items() if key in nfc_remain}
        nfc_remain_df = pd.DataFrame([[key, value] for key,value in nfc_remain_d.iteritems()], columns=['team', 'wins'])
        
        # Select 5 & 6 seeds for NFC
        nfc_seed5 = np.random.choice(pd.Series(nfc_remain_df.loc[nfc_remain_df.wins == max(nfc_remain_df.wins), 'team']))
        nfc_remain_df = nfc_remain_df[nfc_remain_df['team'] != nfc_seed5]
        nfc_seed6 = np.random.choice(pd.Series(nfc_remain_df.loc[nfc_remain_df.wins == max(nfc_remain_df.wins), 'team']))
        
        # AFC Remain DF
        afc_remain_d = {key:value for key,value in team_wins.items() if key in afc_remain}
        afc_remain_df = pd.DataFrame([[key, value] for key,value in afc_remain_d.iteritems()], columns=['team', 'wins'])
        
        # Select 5 & 6 seeds for afc
        afc_seed5 = np.random.choice(pd.Series(afc_remain_df.loc[afc_remain_df.wins == max(afc_remain_df.wins), 'team']))
        afc_remain_df = afc_remain_df[afc_remain_df['team'] != afc_seed5]
        afc_seed6 = np.random.choice(pd.Series(afc_remain_df.loc[afc_remain_df.wins == max(afc_remain_df.wins), 'team']))
        
        ################################    
        ### Playoff Seeds Dictionary ###
        ################################
        
        #For setting up games in simulations of the playoffs
        
        seeds_dict = {
                        afc_seed1 : 1, afc_seed2 : 2, afc_seed3 : 3, afc_seed4 : 4, afc_seed5 : 5, afc_seed6 : 6,
                        nfc_seed1 : 1, nfc_seed2 : 2, nfc_seed3 : 3, nfc_seed4 : 4, nfc_seed5 : 5, nfc_seed6 : 6,
                     }
        
        
        #################################
        #####                       #####
        ##### Simulate the Playoffs #####
        #####                       #####
        #################################
        
        ### Simulate WC round
        
        ##### Game 1
        afc_wc1, mov = simulate_game(ratings, afc_seed3, afc_seed6)
        update_ratings(ratings, afc_seed3, afc_seed6, mov)

        ##### Game 2
        afc_wc2, mov = simulate_game(ratings, afc_seed4, afc_seed5)
        update_ratings(ratings, afc_seed4, afc_seed5, mov)
        
        ##### Game 3
        nfc_wc1, mov = simulate_game(ratings, nfc_seed3, nfc_seed6)
        update_ratings(ratings, nfc_seed3, nfc_seed6, mov)
        
        ##### Game 4
        nfc_wc2, mov = simulate_game(ratings, nfc_seed4, nfc_seed5)
        update_ratings(ratings, nfc_seed4, nfc_seed5, mov)
        
        
        
        ### Simulate Divisional Round
        if afc_wc1 == afc_seed6:
            afc_div1, mov = simulate_game(ratings, afc_seed1, afc_wc1)
            update_ratings(ratings, afc_seed1, afc_wc1, mov)
            afc_div2, mov = simulate_game(ratings, afc_seed2, afc_wc2)
            update_ratings(ratings, afc_seed2, afc_wc2, mov)
            
        else:
            afc_div1, mov = simulate_game(ratings, afc_seed1, afc_wc2)
            update_ratings(ratings, afc_seed1, afc_wc2, mov)
            afc_div2, mov = simulate_game(ratings, afc_seed2, afc_wc1)
            update_ratings(ratings, afc_seed2, afc_wc1, mov)
            
        if nfc_wc1 == nfc_seed6:
            nfc_div1, mov = simulate_game(ratings, nfc_seed1, nfc_wc1)
            update_ratings(ratings, nfc_seed1, nfc_wc1, mov)
            nfc_div2, mov = simulate_game(ratings, nfc_seed2, nfc_wc2)
            update_ratings(ratings, nfc_seed2, nfc_wc2, mov)
        else:
            nfc_div1, mov = simulate_game(ratings, nfc_seed1, nfc_wc2)
            update_ratings(ratings, nfc_seed1, nfc_wc2, mov)
            nfc_div2, mov = simulate_game(ratings, nfc_seed2, nfc_wc1)
            update_ratings(ratings, nfc_seed2, nfc_wc1, mov)
            
        ### Simulate Conference Championship Games
        if seeds_dict[afc_div1] < seeds_dict[afc_div2]:
            afc_cc, mov = simulate_game(ratings, afc_div1, afc_div2)
            update_ratings(ratings, afc_div1, afc_div2, mov)
        else:
            afc_cc, mov = simulate_game(ratings, afc_div2, afc_div1)
            update_ratings(ratings, afc_div2, afc_div1, mov)
        
        if seeds_dict[nfc_div1] < seeds_dict[nfc_div2]:
            nfc_cc, mov = simulate_game(ratings, nfc_div1, nfc_div2)
            update_ratings(ratings, nfc_div1, nfc_div2, mov)
        else:
            nfc_cc, mov = simulate_game(ratings, nfc_div2, nfc_div1)
            update_ratings(ratings, nfc_div2, nfc_div1, mov)
        
        # Simulate Super Bowl
        sb, mov = simulate_neutral_game(ratings, afc_cc, nfc_cc)
        
        ##################################################
        #####                                        #####
        ##### Store various info for each simulation #####
        #####                                        #####
        ##################################################
        
        ### Division Winners
        division_winners.extend([
                                nfc_north_champs, 
                                nfc_south_champs,
                                nfc_east_champs,
                                nfc_west_champs,
                                afc_north_champs,
                                afc_south_champs,
                                afc_east_champs,
                                afc_west_champs
                               ])
        
        ### Playoffs 
        playoffs.extend([
                            nfc_seed1, nfc_seed2, nfc_seed3, nfc_seed4, nfc_seed5, nfc_seed6,
                            afc_seed1, afc_seed2, afc_seed3, afc_seed4, afc_seed5, afc_seed6
                        ])
        
        ### First-round bye
        bye_round.extend([nfc_seed1, nfc_seed2,afc_seed1, afc_seed2])
        
        ### Super Bowl
        super_bowl.extend([afc_cc, nfc_cc])
        
        ### Super Bowl Champs
        champs.append(sb)
        
        if i in range(0, (settings.SIMULATIONS + 1), 500):
            print "Completing simulation # " + str(i) + " ..."
        
        i += 1
    return playoffs, division_winners, bye_round, super_bowl, champs

def final_sim_results(playoffs, division_winners, bye_round, super_bowl, champs):

    # Store result in dictionaries
    all_playoffs = dict(Counter(playoffs))
    all_div_winners = dict(Counter(division_winners))
    all_bye = dict(Counter(bye_round))
    all_sb = dict(Counter(super_bowl))
    all_champs = dict(Counter(champs))


    final_results_dict = {}
    for team in teams:
        final_results_dict[team] = {}
        final_results_dict[team]['elo'] = ratings_0['ratings'][team]
        final_results_dict[team]['wins'] = float(sum(season_results[team][i] for i in season_results[team])) / settings.SIMULATIONS
        final_results_dict[team]['pt_diff'] = float(sum(pt_diff[team][i] for i in pt_diff[team])) / settings.SIMULATIONS
        
        # MAKE PLAYOFFS
        try:
            final_results_dict[team]['playoffs'] = float(all_playoffs[team])/settings.SIMULATIONS
        except:
            final_results_dict[team]['playoffs'] = 0.0
        
        # WIN DIVISION
        try:
            final_results_dict[team]['win_division'] = float(all_div_winners[team])/settings.SIMULATIONS
        except:
            final_results_dict[team]['win_division'] = 0.0
            
        # FIRST ROUND BYE
        try:
            final_results_dict[team]['round_one_bye'] = float(all_bye[team])/settings.SIMULATIONS
        except:
            final_results_dict[team]['round_one_bye'] = 0.0
        
        # MAKE SUBER BOWL
        try:
            final_results_dict[team]['super_bowl'] = float(all_sb[team])/settings.SIMULATIONS
        except:
            final_results_dict[team]['super_bowl'] = 0.0
        
        # WIN SUPER BOWL
        try:
            final_results_dict[team]['champs'] = float(all_champs[team])/settings.SIMULATIONS
        except:
            final_results_dict[team]['champs'] = 0.0
    
    return final_results_dict

def write_forecast():
    
    f = open(os.path.join(settings.PROCESSED_DATA_DIR, week_dir, 'Forecast.csv'), 'wb')
    csv_out = csv.writer(f)
    csv_out.writerow(['team', 'record', 'elo', 'wins', 'losses', 'pt_diff', 'playoffs', 'win_division', 'bye', 'super_bowl', 'champs'])

    for team in final_results_dict:

        # Pull the team's current record
        if current_record[team]['t'] == 0:
            record = '(' + str(current_record[team]['w']) + '-' + str(current_record[team]['l']) + ')'
        else:
            record = '(' + str(current_record[team]['w']) + '-' + str(current_record[team]['l']) + '-' + str(current_record[team]['t']) + ')'

        csv_out.writerow([
                            team,
                            record,
                            final_results_dict[team]['elo'],
                            final_results_dict[team]['wins'],
                            16 - final_results_dict[team]['wins'],
                            final_results_dict[team]['pt_diff'],
                            final_results_dict[team]['playoffs'],
                            final_results_dict[team]['win_division'],
                            final_results_dict[team]['round_one_bye'],
                            final_results_dict[team]['super_bowl'],
                            final_results_dict[team]['champs'],
                         ])

    f.close()



if __name__ == "__main__":
    
    # Week of Forecast
    Week = sys.argv[1]

    # Path and file name for raw schedule and results data
    week_dir = 'Week ' + str(Week)

    # Read the data into Pyhon
    data = pd.read_csv(os.path.join(settings.PROCESSED_DATA_DIR, week_dir, 'processed_schedule_data.csv'))
    results = pd.read_csv(os.path.join(settings.PROCESSED_DATA_DIR, week_dir, 'processed_results_data.csv'))

    ratings = ratings_dict_init()
    ratings_0 = ratings

    # Store all the teams to an array
    teams = [i for i in ratings_0['ratings']]

    season_results = season_results_dict_init()
    pt_diff = pt_diff_dict_init()
    current_record = current_record_init()
    ratings, current_record, season_results, pt_diff = loop_thru_results(pt_diff, season_results, current_record, ratings)
    weekly_predictions()
    playoffs, division_winners, bye_round, super_bowl, champs = run_simulations()
    final_results_dict = final_sim_results(playoffs, division_winners, bye_round, super_bowl, champs)
    write_forecast()
