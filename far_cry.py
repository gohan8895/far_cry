#!/usr/bin/env python3

import argparse
import os
import datetime
import re

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
			time_string = line.split(' ',3)[3]			
			time_object = datetime.datetime.strptime(time_string, time_format)
		elif 'g_timezone' in line:
			time_zone = int(line.split(',')[1][:-1])
	return time_object.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=time_zone)))


def create_console_variables_dict(log_data):
	console_variables_dict = dict()
	log_lines = log_data.split('\n')
	for line in log_lines:
		if 'cvar' in line:
			key, value = line.split('(')[1].split(',')[0], line.split('(')[1].split(',')[1][:-1]
			console_variables_dict[key] = [value]
	return console_variables_dict


def parse_session_mode_and_map(log_data):
	log_lines = log_data.split('\n')
	for line in log_lines:
		if 'Loading level Levels' in line:
			mode, map = line.split('/')[1].split(',')[1].split(' ')[2], line.split('/')[1].split(',')[0]
			return (mode, map)

def parse_frags(log_data):
	'''
	(frag_time, killer_name, victim_name, weapon_code)
	(frag_time, killer_name)
	list of tuples of strings
	'''
	log_lines = log_data.split('\n')
	list_frags = list()
	for line in log_lines:
		if 'killed' in line:
			if len(line.split(' ')) == 5:
				frag_time = line.split(' ')[0][1:6]
				killer_name = line.split(' ')[2]
				list_frags.append((frag_time, killer_name))
			elif len(line.split(' ')) == 7:
				frag_time = line.split(' ')[0][1:6]
				killer_name = line.split(' ')[2]
				victim_name = line.split(' ')[4]
				weapon_code = line.split(' ')[6]
				list_frags.append((frag_time, killer_name, victim_name, weapon_code))
	return list_frags



def main():
	argument = parse_arguments()
	if argument.log and not os.path.isfile(argument.log):
		print('File not found')
		exit(1)
	file_log = argument.log
	log_data = read_log_file(file_log)
	# print(log_data)
	print(len(log_data))
	log_lines = log_data.split('\n')
	# for x in log_lines:
	# 	print(x)
	log_start_time = parse_log_start_time(log_data)
	# print(log_start_time)
	print(log_start_time)
	print(log_start_time.isoformat())
	console_dict = create_console_variables_dict(log_data)
	# for x, y in console_dict.items():
	# 	print(x, y)
	print(parse_session_mode_and_map(log_data))
	list_frags = parse_frags(log_data)
	


if __name__ == '__main__':
	main()