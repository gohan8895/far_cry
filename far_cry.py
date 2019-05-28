#!/usr/bin/env python3

import argparse
import os



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



def main():
	argument = parse_arguments()
	if argument.log and not os.path.isfile(argument.log):
		print('No fucking file homie')
		exit(1)
	file_log = argument.log
	print(len(read_log_file(file_log)))


if __name__ == '__main__':
	main()