#!/usr/bin/env python3

import argparse
import os



def parse_arguments():
	parser = 	argparse.ArgumentParser()
	parser.add_argument('-l', '--log', required=True, help='nothing')
	args = parser.parse_args()
	return args


def read_log_file(log_file_pathname):
	return os.path.getsize(log_file_pathname)



def main():
	argument = parse_arguments()
	if argument.log and not os.path.isfile(argument.log):
		print('No fucking file homie')
		exit(1)
	file = argument.log
	print(type(file), file)
	# with open(file, 'r') as file_log:
	# 	lines = file_log.readlines()
	# for x in lines:
	# 	print(x[:-1])
	print(read_log_file(file))

if __name__ == '__main__':
	main()