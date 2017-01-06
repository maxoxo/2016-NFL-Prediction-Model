# functions.py
import math

################
### k factor ### ----------------------------------------------------------------------
################
'''
	For the purposes of this model, I have chosen to set k equal to 20
'''
k = 20

#############################
### Expectation Functions ### ---------------------------------------------------------
#############################

'''
	The expectation will be used in the function to update Elo ratings
'''

def E(R1, R2):
    return float(R1) / (R1 + R2)

####################################
### Margin of Victory Multiplier ### ------------------------------------------------
####################################

'''
	This function will determine the number of Elo points gained after a win or lost
	after a loss depending on the margin of victory for the winning team. 
'''

def mov_mult(mov, elo_w, elo_l):
    return math.log(abs(mov) + 1) * (2.2 / ((elo_w - elo_l) * 0.001 + 2.2))

###############################
### Mean Reversion Function ### -----------------------------------------------------
###############################

'''
	At the end of each season, each team's rating will revert towards the mean by
	updating their final rating as follows: allow them to retain 75 percent of
	ther rating and have the rest be set at 1505, about five points above the expected
	average.
'''

def revert2mean(x):
    return round((0.75*x) + (0.25*1505),0)



######################
### update_ratings ### ---------------------------------------------------------------
######################

'''
	Function will be used to update Elo ratings of individal teams accoring to
	the results of games contained in the all_game_results.csv file.
'''

def update_ratings(week, elo_home, pts_home, elo_away, pts_away):
    
    R_home = 10**(elo_home/400)
    R_away = 10**(elo_away/400)
    
    
    
    if pts_home > pts_away:
        
        S_home = 1
        S_away = 0
        
        E_home = E(R_home, R_away)
        mov = pts_home - pts_away
        if week != 21:
            elo_w = elo_home + 65
        else:
            elo_w = elo_home
        elo_l = elo_away
        mult = mov_mult(mov, elo_w, elo_l)
        change = k * mult * (S_home - E_home)
        
        elo_home_new = elo_home + change
        elo_away_new = elo_away - change
        
    else:
        
        S_home = 0
        S_away = 1
        
        E_away = E(R_away, R_home)
        mov = pts_away - pts_home
        elo_w = elo_away
        if week != 21:
            elo_l = elo_home + 65
        else:
            elo_l = elo_home
        mult = mov_mult(mov, elo_w, elo_l)
        change = k * mult * (S_away - E_away)
    
        elo_home_new = elo_home - change
        elo_away_new = elo_away + change
        
        
        
    return round(elo_home_new, 0), round(elo_away_new, 0)