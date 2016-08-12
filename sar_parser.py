#!/usr/bin/env python
# -*- coding: utf8 -*-
'''
Analysis sar log file, auto generate all information with sar.json.
The sar.json is a json file format {'field key word': 'table name'}.

The idea: every item in sar log can regard a table and every table has a unique
field, so a unique field is a mark of table.
You maybe need edit the sar.json makesure the table you need can be get.
'''
import sys
import json


def parser(logfile, tablemap):
    '''
    analysis sar logfile and return info
    Para:
        logfile: file, opened by sar log file
        tablemap: dict, format {'field key word': 'table name'}
    Return:
        sar: a dict of {str:item}
    '''
    sar = {}  # all info store in dict sar
    #  store lines
    loglines = [line for line in logfile]
    #  get log file basic info from first line
    #      first line format: 'linux [2.6*] (name)\t[time]\t[arch]\t32 cpu'
    values = [x for x in loglines[0].split('\t') if x != '']
    sar['sys'] = values[0].split(' ')[0]
    sar['kernel'] = values[0].split(' ')[1]
    sar['hostname'] = values[0].split(' ')[2][1:-1]  # del '()'
    sar['date'] = values[1]
    sar['arch'] = values[2][1:-1]  # del '__'
    sar['cpuinfo'] = values[3][1:-2]  # del '()\n'
    # get table info, format {'table':{name:{field:[values]}}}
    sar['table'] = {}
    #  get line blocks split by '\n\n', most blocks is a table
    logblocks = ''.join(loglines[2:]).split('\n\n')
    #  get table info from a block
    for block in logblocks:
        tablename = None
        #  get table name by key field word from table head
        tablehead = block.split('\n')[0]
        #  get table field from tablehead
        fields = [f for f in tablehead.split(' ') if f != ''][2:]
        fields.insert(0, 'time')  # add field 'time'
        for keyfield in tablemap.keys():
            if keyfield in fields:
                tablename = tablemap[keyfield]
                break
        if tablename is None:  # Not a table block
            continue
        if tablename not in sar['table']:
            sar['table'][tablename] = {}
            #  insert fields to sar
            for field in fields:
                sar['table'][tablename][field] = []
        #  get field value from remain lines
        for line in block.split('\n')[1:]:
            if 'Average' in line:  # no average info
                break
            # get values, format eg: '[12-time, [PM/AM], ...]'
            values = [f for f in line.split(' ') if f != '']
            # 12 hours to 24 hours
            temp = values[0].split(':')  # [h,m,s]
            if values[1] == 'AM':
                if '12' in values[0]:  # eg: '12:01:01 AM'
                    temp[0] = '00'
                    values[0] = ':'.join(temp)
            else:
                if '12' not in values[0]:  # eg: '12:01:01 PM'
                    temp[0] = str(int(temp[0]) + 12)
                    values[0] = ':'.join(temp)
            values[0] = sar['date'] + values[0]  # add date to time field
            values.pop(1)  # delect 'AM' or 'PM'
            # add to sar
            for index, value in enumerate(values):
                sar['table'][tablename][fields[index]].append(value)
    return sar


def test():
    if len(sys.argv) < 3:
        print('use: {:s} [sar log file] [sar json file]')
    else:
        with open(sys.argv[1], 'r') as l, open(sys.argv[2], 'r') as m:
                print(parser(l, json.load(m)))


if __name__ == '__main__':
    test()
