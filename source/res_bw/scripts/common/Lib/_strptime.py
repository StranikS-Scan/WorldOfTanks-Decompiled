# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/_strptime.py
# Compiled at: 2010-05-25 20:46:16
"""Strptime-related classes and functions.

CLASSES:
    LocaleTime -- Discovers and stores locale-specific time information
    TimeRE -- Creates regexes for pattern matching a string of text containing
                time information

FUNCTIONS:
    _getlang -- Figure out what language is being used for the locale
    strptime -- Calculates the time struct represented by the passed-in string

"""
--- This code section failed: ---

 212       0	LOAD_FAST         '.0'
           3	FOR_ITER          '33'
           6	STORE_FAST        'tz_names'
           9	SETUP_LOOP        '30'

 213      12	LOAD_FAST         'tz_names'
          15	GET_ITER          ''
          16	FOR_ITER          '30'
          19	STORE_FAST        'tz'
          22	LOAD_FAST         'tz'
          25	YIELD_VALUE       ''
          26	POP_TOP           ''
          27	JUMP_BACK         '16'
        30_0	COME_FROM         '9'
          30	JUMP_BACK         '3'
          33	POP_BLOCK         ''

Syntax error at or near 'SETUP_LOOP' token at offset 9
