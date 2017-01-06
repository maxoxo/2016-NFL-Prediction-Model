import csv
import os
import sys
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
	return DataFrame(csv_data[0], csv_data[1:])



if __name__ == '__main__':

	# Week of Forecast
	Week = sys.argv[1]

	# Path and file name for raw schedule and results data
	#f = 'Week ' + str(Week)+ '/years_2016_games_games.csv'
	week_dir = 'Week ' + str(Week)

	# Open raw schedule and results data
	data = ReadCsv(os.path.join(settings.DATA_DIR, week_dir, 'years_2016_games_games.csv'))

	### Open two files: one to print result; and one to print the upcoming schedule
	f1 = open(os.path.join(settings.PROCESSED_DATA_DIR, week_dir, 'processed_results_data.csv'), 'wb')
	f2 = open(os.path.join(settings.PROCESSED_DATA_DIR, week_dir, 'processed_schedule_data.csv'), 'wb')


	csv_out1 = csv.writer(f1)
	csv_out2 = csv.writer(f2)

	csv_out1.writerow(['week', 'home', 'home_pts', 'away', 'away_pts'])
	csv_out2.writerow(['week', 'home', 'away'])

	for row in data.Data():

		location = row[5]
		week = row[data.FieldIndex('Week')]
		winner = row[data.FieldIndex('Winner/tie')]
		pts_w = row[data.FieldIndex('PtsW')]
		loser = row[data.FieldIndex('Loser/tie')]
		pts_l = row[data.FieldIndex('PtsL')]



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

		if pts_w != "":
			csv_out1.writerow([week, home, home_pts, away, away_pts])
		else:
			csv_out2.writerow([week, home, away])



	f1.close()
	f2.close()


