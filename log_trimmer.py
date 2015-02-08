#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Trims log files by datetime intervals

import argparse
import datetime
import sys
import re
import os


def match(line):
    global timeformat
    global timeformat_regex_c
    global target_file
    matched = timeformat_regex_c.search(line)
    if not matched:
        while not matched:
            line = target_file.readline()
            matched = timeformat_regex_c.search(line)
    return datetime.datetime.strptime(matched.group(), timeformat)


def retrieve_test_line(position):
    target_file.seek(position, 0)
    target_file.readline()  # avoids reading partial line, which will mess up match attempt
    new_position = target_file.tell()  # gets start of line position
    return target_file.readline(), new_position


def check_lower_bound(position):
    target_file.seek(position, 0)
    return target_file.readline()


def find_line(target, lower_bound, upper_bound):
    target_file.seek(lower_bound, 0)
    target_file.seek(upper_bound, 0)

    trial = int((lower_bound + upper_bound) / 2)
    inspection_text, position = retrieve_test_line(trial)
    if position == upper_bound:
        text = check_lower_bound(lower_bound)
        if match(text) == target:
            return position
        return position
    matched_timestamp = match(inspection_text)
    if matched_timestamp == target:
        return position
    elif matched_timestamp < target:
        return find_line(target, position, upper_bound)
    elif matched_timestamp > target:
        return find_line(target, lower_bound, position)
    else:
        return  # no match for target within range


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Cut log files by timestamp',
                                     epilog='Example:\n'
                                     '{script_name} -r "2012-10-09 15:45:38" "2012-10-12 14:34:43" -f bigbig.log\n'
                                     '{script_name} -r "30-01-1999 15:55:09" "02-02-1999 22:01:01"'
                                     ' -f file.log -t "%d-%m-%Y %H:%M:%S"\n'.format(script_name=sys.argv[0]))

    parser.add_argument('-r', '--range',
                        action='store',
                        dest='ranges',
                        nargs=2,
                        metavar='RANGE',
                        required=True,
                        help='start and end range for cutting')
    parser.add_argument('-f', '--file',
                        action='store',
                        dest='log_filename',
                        metavar='FILENAME',
                        required=True,
                        help='Log file name')
    parser.add_argument('-t', '--timeformat',
                        action='store',
                        dest='timeformat',
                        default='%Y-%m-%d %H:%M:%S',
                        help='timeformat in log file')
    parser.add_argument('-o', '--outfile',
                        action='store',
                        dest='out_filename',
                        default='',
                        metavar='FILENAME',
                        help='out filename')

    args = parser.parse_args()

    timeformat_dictionary = {'%Y': '\d\d\d\d',
                             '%y': '\d\d',
                             '%m': '\d\d',
                             '%d': '\d\d',
                             '%H': '\d\d',
                             '%M': '\d\d',
                             '%S': '\d\d',
                             '%f': '\d+',
                             '%j': '\d\d\d',
                             '%I': '\d\d',
                             '%U': '\d\d',
                             '%w': '\d',
                             '%W': '\d\d',
                             '%a': '\w+',
                             '%A': '\w+',
                             '%b': '\w+',
                             '%B': '\w+',
                             '%c': '\w+',
                             '%p': '\w+',
                             '%Z': '\w+'}
    global timeformat_regex_c
    global timeformat
    global target_file

    timeformat_regex = args.timeformat.replace(' ', '\ ')
    timeformat_regex = timeformat_regex.replace('.', '\.')
    for key, value in timeformat_dictionary.items():
        timeformat_regex = timeformat_regex.replace(key, value)

    timeformat_regex_c = re.compile(timeformat_regex)
    timeformat = args.timeformat

    # start_target =  # first line you are trying to find:
    start_target = datetime.datetime.strptime(args.ranges[0], timeformat)
    # end_target =  # last line you are trying to find:
    end_target = datetime.datetime.strptime(args.ranges[1], timeformat)

    target_file = open(args.log_filename, "r")
    lower_bound = 0
    target_file.seek(0, 2)  # find upper bound
    upper_bound = target_file.tell()
    sys.stdout.write('Start searching in {file_name}\n'.format(file_name=args.log_filename))
    sequence_start = find_line(start_target, lower_bound, upper_bound)

    if sequence_start or sequence_start == 0:   # allow for starting at zero - corner case
        sequence_end = find_line(end_target, sequence_start, upper_bound)
        if not sequence_end:
            sys.stderr.write("start_target match: " + str(sequence_start) + '\n')
    else:
        sys.stderr.write("start match is not present in the current file")

    if (sequence_start or sequence_start == 0) and sequence_end:
        if args.out_filename:
            out_filename = args.out_filename
        else:
            out_filename = os.path.basename(args.log_filename)
            out_filename = 'cutted_' + out_filename
            out_filename = os.path.join(os.path.dirname(args.log_filename), out_filename)
        target_file.seek(sequence_start, 0)
        out_file = open(out_filename, 'w')
        sys.stdout.write('writing {file_name}...\n'.format(file_name=out_filename))
        while target_file.tell() <= sequence_end:
            out_file.write(target_file.readline())

if __name__ == '__main__':
    main()
