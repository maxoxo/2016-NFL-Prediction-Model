# 2016 NFL Prediction Model

### Overview
This repository contains the code and data for a predictive model for the upcoming NFL season. In short, the model does the following: One, generate probabilistic predictions and estimated point spreads for each game throughout the season; and two, estimate each team’s chances of making the playoffs, winning their division, receiving a first-round bye, playing in the Super Bowl, and winning the Super Bowl.

### Download the data
All the data used for this project were obtained from Pro-Football-Reference.com.

### Install the requirements
Install the required packages by running `pip install -r requirements.txt` from the command line once you have navigated to the project's directory.

* This project uses Python 2.7 and the following libraries: `pandas` and `numpy`.

### Usage
1. Run `python process_historical_results_data.py` to create a single processed data file containing results from all NFL games--regular season and playoffs--since the 2000 season. This script will output a csv file called `all_game_results.csv` in the `processed data` directory. Note that this script only needs to be run once; there is no need to re-run it when updating the forecast at the beginning of each week.

2. Run `python initial_ratings.py` to generate initial Elo ratings for 2016 NFL season for all 32 teams. This script will output two csv files in the `processed data` directory: `initial_ratings_2016.csv` and `historical_ratings.csv`. Like the script form step 1, this script only needs to be run once and there is no need to re-run it when updating the forecast at the beginning of each week. 

3. Process the raw schedule and results data for the desired week. Do this by running the following command: `python process_schedule_data.py [Week]`. So, for example, to process the raw schedule and results data for Week 3, you would enter the following command: `python process_schedule_data.py 3`. Once this script has finished running you will see the following files in the `Week 3` folder in the `processed data` directory: `processed_results_data.csv` and `processed_schedule_data.csv`. The former will contain the data on the outcomes of all NFL games played up until that point in the season. The latter will contain data on all remaining games in the 2016 NFL schedule.

4. Generate predictions for the upcoming week and an updated full season forecast by running the following command: `python forecast [Week]`. This will generate two csv files into the `processed data` folder for the specified week: one containing predictions for the upcoming week and one containing the full season forecast.
