import csv
import os
import settings

class DataFrame:
	def __init__(self, header, data):
		self.header = header
		self.data = data
	def FieldIndex(self, field):
		return self.header.index(field)
	def Data(self):
		return self.data


def ReadCsv(filename):
	csv_data = []
	with open(filename, 'rb') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter = ',')
		for row in csv_reader:
			csv_data.append(row)
	return DataFrame(csv_data[1], csv_data[2:])

# Seasons to loop through
seasons = range(2000, 2016)

if __name__ == '__main__':

	f = open(os.path.join(settings.PROCESSED_DATA_DIR, 'all_game_results.csv'), 'wb')
	csv_out = csv.writer(f)
	csv_out.writerow(['season', 'week', 'week_id', 'home', 'home_pts', 'away', 'away_pts' ])

	for i in seasons:
		
		file_name = 'historical data/years_' + str(i) + '_games_games.csv'
		data = ReadCsv(os.path.join(settings.DATA_DIR, file_name))

		for row in data.Data():

			# Pull necessary data
			season = i
			week = row[data.FieldIndex('Week')]
			winner = row[data.FieldIndex('Winner/tie')]
			pts_w = row[data.FieldIndex('PtsW')]
			loser = row[data.FieldIndex('Loser/tie')]
			pts_l = row[data.FieldIndex('PtsL')]
			location = row[4]

			# Update playoff weeks so that they are a number
			if week == 'WildCard':
				week = 18
			if week == 'Division':
				week = 19
			if week == 'ConfChamp':
				week = 20
			if week == 'SuperBowl':
				week = 21
			
			# Skip rows with no data
			if week in ('Week', ''):
				continue

			week_id = (season - seasons[0])  * 21 + int(week)

			# Which team was home and which team was away
			if location == '@':
				home = loser
				home_pts = pts_l
				away = winner
				away_pts = pts_w
			else:
				home = winner
				home_pts = pts_w
				away = loser
				away_pts = pts_l


			csv_out.writerow([i, week, week_id, home, home_pts, away, away_pts])

	f.close()






