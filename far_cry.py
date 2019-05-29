#!/usr/bin/env python3

import argparse
import os
import datetime


def parse_arguments():
	parser = 	argparse.ArgumentParser()
	parser.add_argument('-l', '--log', required=True, help='nothing')
	args = parser.parse_args()
	return args


def read_log_file(log_file_pathname):
	try:
		with open(log_file_pathname, 'r') as file_log:
			return file_log.read()
	except OSError:
		print('Invalid input')


def parse_log_start_time(log_data):
	log_lines = log_data.split('\n')
	time_format = '%A, %B %d, %Y %X'
	for line in log_lines:
		if 'Log Started at' in line:
			time = line.split(' ',3)[3]			
			time_object = datetime.datetime.strptime(time, time_format)
		elif 'g_timezone' in line:
			time_zone = line.split(',')[1][:-1]
	return time_object.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=int(time_zone))))


def main():
	argument = parse_arguments()
	if argument.log and not os.path.isfile(argument.log):
		print('No fucking file homie')
		exit(1)
	file_log = argument.log
	log_data = read_log_file(file_log)
	# print(len(log_data))
	log_lines = log_data.split('\n')
	# for x in log_lines:
	# 	print(x)
	log_start_time = parse_log_start_time(log_data)
	print(log_start_time.isoformat())


if __name__ == '__main__':
	main()