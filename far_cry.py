#!/usr/bin/env python3

import argparse
import os
import datetime
from re import search, findall
import csv

def parse_arguments():
    parser =     argparse.ArgumentParser()
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
    list of tuples of strings
    '''
    log_lines = log_data.split('\n')
    list_frags = list()
    start_time = parse_log_start_time(log_data)
    for line in log_lines:
        if 'killed' in line:
            if len(line.split(' ')) == 5:
                delta = datetime.timedelta(hours=int(line.split(' ')[0][1:6].split(':')[0]), minutes=int(line.split(' ')[0][1:6].split(':')[1]))
                frag_time = start_time + delta
                killer_name = line.split(' ')[2]
                list_frags.append((frag_time, killer_name))
            elif len(line.split(' ')) == 7:
                delta = datetime.timedelta(hours=int(line.split(' ')[0][1:6].split(':')[0]), minutes=int(line.split(' ')[0][1:6].split(':')[1]))
                frag_time = start_time + delta
                killer_name = line.split(' ')[2]
                victim_name = line.split(' ')[4]
                weapon_code = line.split(' ')[6]
                list_frags.append((frag_time, killer_name, victim_name, weapon_code))
    return list_frags


def get_weapon_emoji(weapon_code):
    '''
    
    '''
    weapon_emoji_dict = {
                        ('Vehicle'): '🚙',
                        ('Falcon', 'Shotgun', 'P90', 'MP5',
                         'M4', 'AG36', 'OICW', 'SniperRifle',
                         'M249', 'MG', 'VehicleMountedAutoMG',
                         'VehicleMountedMG'): '🔫',
                        ('HandGrenade', 'AG36Grenade',
                         'OICWGrenade', 'StickyExplosive'): '💣',
                        ('Rocket', 'VehicleMountedRocketMG',
                         'VehicleRocket'): '🚀',
                        ('Machete'): '🔪',
                        ('Boat'): '🚤'
    }
    for weapon_group in weapon_emoji_dict:
        if weapon_code in weapon_group:
            return weapon_emoji_dict[weapon_group]


def prettify_frags(frags):
    '''
    copied
    '''
    prettified_frags = []
    for frag in frags:
        if len(frag) == 4:
            frag_time, killer_name, victim_name, weapon_code = frag
            prettified_frags.append('[' + str(frag_time) + ']' + ' 😛 ' +
                                    killer_name + ' ' +
                                    get_weapon_emoji(weapon_code) +
                                    ' 😦 ' +
                                    victim_name)
        if len(frag) == 2:
            frag_time, killer_name = frag
            prettified_frags.append('[' + str(frag_time) + ']' + ' 😦 ' +
                                    killer_name + ' ☠')
    return prettified_frags


def get_frag_time_obj(log_data, frag_time):
    start_time = parse_log_start_time(log_data)
    frag_minute = int(frag_time.split(':')[0])
    frag_second = int(frag_time.split(':')[1])
    frag_time_obj = start_time.replace(minute=frag_minute,
                                       second=frag_second)
    if frag_minute < start_time.minute:
        frag_time_obj += timedelta(hours=1)
    return frag_time_obj


def parse_game_session_start_and_end_times(log_data):
    try:
        end_time_string = search(r'<([0-5]\d:[0-5]\d)> == Statistics ',
                                 log_data).group(1)
    except AttributeError:
        end_time_string = search(
            r'<([0-5]\d:[0-5]\d)> ERROR: .* ERROR File: .* Function: .*',
            log_data).group(1)
    end_time_obj = get_frag_time_obj(log_data, end_time_string)
    start_time_string = search(r'<([0-5]\d:[0-5]\d)>  Level .* seconds',
                               log_data).group(1)
    start_time_obj = get_frag_time_obj(log_data, start_time_string)
    return start_time_obj, end_time_obj



def write_frag_csv_file(log_file_pathname, frags):
    try:
        with open(log_file_pathname, 'w+', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(frags)
    except OSError:
        pass


def insert_match_to_sqlite(file_pathname, start_time, end_time, game_mode,
                           map_name, frags):
    def insert_frags_to_sqlite(connection, match_id, frags):
        # cur = connection.cursor
        for frag in frags:
            if len(frag) == 4:
                new_frag = (match_id, frag[0].isoformat(), frag[1], frag[2], frag[3])
                connection.execute("insert into match_frag\
                             values (?, ?, ?, ?, ?)", new_frag)
            elif len(frag) == 2:
                new_frag = (match_id, frag[0].isoformat(), frag[1])
                connection.execute("insert into match_frag(match_id, frag_time,\
                                    killer_name) values (?, ?, ?)", new_frag)
        connection.commit()

    conn = sqlite3.connect(file_pathname)
    cur = conn.cursor()
    cur.execute("insert into match(start_time, end_time,\
                 game_mode, map_name) values (?, ?, ?, ?)",
                (start_time.isoformat(), end_time.isoformat(), game_mode, map_name))
    conn.commit()
    last_row_id = cur.lastrowid
    insert_frags_to_sqlite(conn, last_row_id, frags)
    conn.close()
    return last_row_id


def main():
    argument = parse_arguments()
    if argument.log and not os.path.isfile(argument.log):
        print('File not found')
        exit(1)
    file_log = argument.log
    basename_file_path = os.path.basename(file_log)
    log_data = read_log_file(file_log)
    # print(log_data)
    # print(len(log_data))
    log_lines = log_data.split('\n')
    # for x in log_lines:
    #     print(x)
    log_start_time = parse_log_start_time(log_data)
    # print(log_start_time)
    # print(log_start_time)
    # print(log_start_time.isoformat())
    console_dict = create_console_variables_dict(log_data)
    # for x, y in console_dict.items():
    #     print(x, y)
    # print(parse_session_mode_and_map(log_data))
    frags = parse_frags(log_data)
    # for x in frags:
    #     print(x)
    prettified_frags = prettify_frags(frags)
    # for x in prettified_frags:
    #     print(x)
    # print('./' + root_file_path[:-4] + '.csv')
    write_frag_csv_file('./' + basename_file_path[:-4] + '.csv', frags)
    end_time, start_time = parse_game_session_start_and_end_times(log_data)
    print(end_time, start_time)



if __name__ == '__main__':
    main()