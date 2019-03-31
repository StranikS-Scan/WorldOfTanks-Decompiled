# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/_abcoll.py
# Compiled at: 2010-10-21 18:49:01
"""Abstract Base Classes (ABCs) for collections, according to PEP 3119.

DON'T USE THIS MODULE DIRECTLY!  The classes here should be imported
via collections; they are defined here only to alleviate certain
bootstrapping issues.  Unit tests are in test_collections.
"""
--- This code section failed: ---

 192       0	LOAD_FAST         '.0'
           3	FOR_ITER          '33'
           6	STORE_FAST        's'
           9	SETUP_LOOP        '30'
          12	LOAD_FAST         's'
          15	GET_ITER          ''
          16	FOR_ITER          '30'
          19	STORE_FAST        'e'
          22	LOAD_FAST         'e'
          25	YIELD_VALUE       ''
          26	POP_TOP           ''
          27	JUMP_BACK         '16'
        30_0	COME_FROM         '9'
          30	JUMP_BACK         '3'
          33	POP_BLOCK         ''

Syntax error at or near 'SETUP_LOOP' token at offset 9
