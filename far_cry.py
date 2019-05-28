#!/usr/bin/env python3

import argparse
import os



def parse_arguments():
	parser = 	argparse.ArgumentParser()
	parser.add_argument('-l', '--log', required=True, help='nothing')
	args = parser.parse_args()
	return args


def main():
	argument = parse_arguments()
	if argument.log and not os.path.isfile(argument.log):
		print('No fucking file homie')
		exit(1)
	file = argument.log




if __name__ == '__main__':
	main()