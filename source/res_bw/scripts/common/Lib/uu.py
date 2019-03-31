# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/uu.py
# Compiled at: 2010-05-25 20:46:16
"""Implementation of the UUencode and UUdecode functions.

encode(in_file, out_file [,name, mode])
decode(in_file [, out_file, mode])
"""
import binascii
import os
import sys
__all__ = ['Error', 'encode', 'decode']

class Error(Exception):
    pass


def encode(in_file, out_file, name=None, mode=None):
    """Uuencode file"""
    if in_file == '-':
        in_file = sys.stdin
    elif isinstance(in_file, basestring):
        if name is None:
            name = os.path.basename(in_file)
        if mode is None:
            try:
                mode = os.stat(in_file).st_mode
            except AttributeError:
                pass

        in_file = open(in_file, 'rb')
    if out_file == '-':
        out_file = sys.stdout
    elif isinstance(out_file, basestring):
        out_file = open(out_file, 'w')
    if name is None:
        name = '-'
    if mode is None:
        mode = 438
    out_file.write('begin %o %s\n' % (mode & 511, name))
    data = in_file.read(45)
    while 1:
        len(data) > 0 and out_file.write(binascii.b2a_uu(data))
        data = in_file.read(45)

    out_file.write(' \nend\n')
    return


def decode--- This code section failed: ---

  88       0	LOAD_FAST         'in_file'
           3	LOAD_CONST        '-'
           6	COMPARE_OP        '=='
           9	JUMP_IF_FALSE     '24'

  89      12	LOAD_GLOBAL       'sys'
          15	LOAD_ATTR         'stdin'
          18	STORE_FAST        'in_file'
          21	JUMP_FORWARD      '54'

  90      24	LOAD_GLOBAL       'isinstance'
          27	LOAD_FAST         'in_file'
          30	LOAD_GLOBAL       'basestring'
          33	CALL_FUNCTION_2   ''
          36	JUMP_IF_FALSE     '54'

  91      39	LOAD_GLOBAL       'open'
          42	LOAD_FAST         'in_file'
          45	CALL_FUNCTION_1   ''
          48	STORE_FAST        'in_file'
          51	JUMP_FORWARD      '54'
        54_0	COME_FROM         '21'
        54_1	COME_FROM         '51'

  95      54	SETUP_LOOP        '218'
          57	LOAD_GLOBAL       'True'
          60	JUMP_IF_FALSE     '217'

  96      63	LOAD_FAST         'in_file'
          66	LOAD_ATTR         'readline'
          69	CALL_FUNCTION_0   ''
          72	STORE_FAST        'hdr'

  97      75	LOAD_FAST         'hdr'
          78	JUMP_IF_TRUE      '96'

  98      81	LOAD_GLOBAL       'Error'
          84	LOAD_CONST        'No valid begin line found in input file'
          87	CALL_FUNCTION_1   ''
          90	RAISE_VARARGS_1   ''
          93	JUMP_FORWARD      '96'
        96_0	COME_FROM         '93'

  99      96	LOAD_FAST         'hdr'
          99	LOAD_ATTR         'startswith'
         102	LOAD_CONST        'begin'
         105	CALL_FUNCTION_1   ''
         108	JUMP_IF_TRUE      '117'

 100     111	CONTINUE          '57'
         114	JUMP_FORWARD      '117'
       117_0	COME_FROM         '114'

 101     117	LOAD_FAST         'hdr'
         120	LOAD_ATTR         'split'
         123	LOAD_CONST        ' '
         126	LOAD_CONST        2
         129	CALL_FUNCTION_2   ''
         132	STORE_FAST        'hdrfields'

 102     135	LOAD_GLOBAL       'len'
         138	LOAD_FAST         'hdrfields'
         141	CALL_FUNCTION_1   ''
         144	LOAD_CONST        3
         147	COMPARE_OP        '=='
         150	JUMP_IF_FALSE     '214'
         153	LOAD_FAST         'hdrfields'
         156	LOAD_CONST        0
         159	BINARY_SUBSCR     ''
         160	LOAD_CONST        'begin'
         163	COMPARE_OP        '=='
       166_0	COME_FROM         '150'
         166	JUMP_IF_FALSE     '214'

 103     169	SETUP_EXCEPT      '194'

 104     172	LOAD_GLOBAL       'int'
         175	LOAD_FAST         'hdrfields'
         178	LOAD_CONST        1
         181	BINARY_SUBSCR     ''
         182	LOAD_CONST        8
         185	CALL_FUNCTION_2   ''
         188	POP_TOP           ''

 105     189	BREAK_LOOP        ''
         190	POP_BLOCK         ''
         191	JUMP_ABSOLUTE     '214'
       194_0	COME_FROM         '169'

 106     194	DUP_TOP           ''
         195	LOAD_GLOBAL       'ValueError'
         198	COMPARE_OP        'exception match'
         201	JUMP_IF_FALSE     '210'
         204	POP_TOP           ''
         205	POP_TOP           ''
         206	POP_TOP           ''

 107     207	JUMP_ABSOLUTE     '214'
         210	END_FINALLY       ''
       211_0	COME_FROM         '210'
         211	JUMP_BACK         '57'
         214	JUMP_BACK         '57'
         217	POP_BLOCK         ''
       218_0	COME_FROM         '54'

 108     218	LOAD_FAST         'out_file'
         221	LOAD_CONST        ''
         224	COMPARE_OP        'is'
         227	JUMP_IF_FALSE     '286'

 109     230	LOAD_FAST         'hdrfields'
         233	LOAD_CONST        2
         236	BINARY_SUBSCR     ''
         237	LOAD_ATTR         'rstrip'
         240	CALL_FUNCTION_0   ''
         243	STORE_FAST        'out_file'

 110     246	LOAD_GLOBAL       'os'
         249	LOAD_ATTR         'path'
         252	LOAD_ATTR         'exists'
         255	LOAD_FAST         'out_file'
         258	CALL_FUNCTION_1   ''
         261	JUMP_IF_FALSE     '283'

 111     264	LOAD_GLOBAL       'Error'
         267	LOAD_CONST        'Cannot overwrite existing file: %s'
         270	LOAD_FAST         'out_file'
         273	BINARY_MODULO     ''
         274	CALL_FUNCTION_1   ''
         277	RAISE_VARARGS_1   ''
         280	JUMP_ABSOLUTE     '286'
         283	JUMP_FORWARD      '286'
       286_0	COME_FROM         '283'

 112     286	LOAD_FAST         'mode'
         289	LOAD_CONST        ''
         292	COMPARE_OP        'is'
         295	JUMP_IF_FALSE     '320'

 113     298	LOAD_GLOBAL       'int'
         301	LOAD_FAST         'hdrfields'
         304	LOAD_CONST        1
         307	BINARY_SUBSCR     ''
         308	LOAD_CONST        8
         311	CALL_FUNCTION_2   ''
         314	STORE_FAST        'mode'
         317	JUMP_FORWARD      '320'
       320_0	COME_FROM         '317'

 117     320	LOAD_GLOBAL       'False'
         323	STORE_FAST        'opened'

 118     326	LOAD_FAST         'out_file'
         329	LOAD_CONST        '-'
         332	COMPARE_OP        '=='
         335	JUMP_IF_FALSE     '350'

 119     338	LOAD_GLOBAL       'sys'
         341	LOAD_ATTR         'stdout'
         344	STORE_FAST        'out_file'
         347	JUMP_FORWARD      '438'

 120     350	LOAD_GLOBAL       'isinstance'
         353	LOAD_FAST         'out_file'
         356	LOAD_GLOBAL       'basestring'
         359	CALL_FUNCTION_2   ''
         362	JUMP_IF_FALSE     '438'

 121     365	LOAD_GLOBAL       'open'
         368	LOAD_FAST         'out_file'
         371	LOAD_CONST        'wb'
         374	CALL_FUNCTION_2   ''
         377	STORE_FAST        'fp'

 122     380	SETUP_EXCEPT      '406'

 123     383	LOAD_GLOBAL       'os'
         386	LOAD_ATTR         'path'
         389	LOAD_ATTR         'chmod'
         392	LOAD_FAST         'out_file'
         395	LOAD_FAST         'mode'
         398	CALL_FUNCTION_2   ''
         401	POP_TOP           ''
         402	POP_BLOCK         ''
         403	JUMP_FORWARD      '423'
       406_0	COME_FROM         '380'

 124     406	DUP_TOP           ''
         407	LOAD_GLOBAL       'AttributeError'
         410	COMPARE_OP        'exception match'
         413	JUMP_IF_FALSE     '422'
         416	POP_TOP           ''
         417	POP_TOP           ''
         418	POP_TOP           ''

 125     419	JUMP_FORWARD      '423'
         422	END_FINALLY       ''
       423_0	COME_FROM         '403'
       423_1	COME_FROM         '422'

 126     423	LOAD_FAST         'fp'
         426	STORE_FAST        'out_file'

 127     429	LOAD_GLOBAL       'True'
         432	STORE_FAST        'opened'
         435	JUMP_FORWARD      '438'
       438_0	COME_FROM         '347'
       438_1	COME_FROM         '435'

 131     438	LOAD_FAST         'in_file'
         441	LOAD_ATTR         'readline'
         444	CALL_FUNCTION_0   ''
         447	STORE_FAST        's'

 132     450	SETUP_LOOP        '634'
         453	LOAD_FAST         's'
         456	JUMP_IF_FALSE     '633'
         459	LOAD_FAST         's'
         462	LOAD_ATTR         'strip'
         465	CALL_FUNCTION_0   ''
         468	LOAD_CONST        'end'
         471	COMPARE_OP        '!='
       474_0	COME_FROM         '456'
         474	JUMP_IF_FALSE     '633'

 133     477	SETUP_EXCEPT      '499'

 134     480	LOAD_GLOBAL       'binascii'
         483	LOAD_ATTR         'a2b_uu'
         486	LOAD_FAST         's'
         489	CALL_FUNCTION_1   ''
         492	STORE_FAST        'data'
         495	POP_BLOCK         ''
         496	JUMP_FORWARD      '605'
       499_0	COME_FROM         '477'

 135     499	DUP_TOP           ''
         500	LOAD_GLOBAL       'binascii'
         503	LOAD_ATTR         'Error'
         506	COMPARE_OP        'exception match'
         509	JUMP_IF_FALSE     '604'
         512	POP_TOP           ''
         513	STORE_FAST        'v'
         516	POP_TOP           ''

 137     517	LOAD_GLOBAL       'ord'
         520	LOAD_FAST         's'
         523	LOAD_CONST        0
         526	BINARY_SUBSCR     ''
         527	CALL_FUNCTION_1   ''
         530	LOAD_CONST        32
         533	BINARY_SUBTRACT   ''
         534	LOAD_CONST        63
         537	BINARY_AND        ''
         538	LOAD_CONST        4
         541	BINARY_MULTIPLY   ''
         542	LOAD_CONST        5
         545	BINARY_ADD        ''
         546	LOAD_CONST        3
         549	BINARY_FLOOR_DIVIDE ''
         550	STORE_FAST        'nbytes'

 138     553	LOAD_GLOBAL       'binascii'
         556	LOAD_ATTR         'a2b_uu'
         559	LOAD_FAST         's'
         562	LOAD_FAST         'nbytes'
         565	SLICE+2           ''
         566	CALL_FUNCTION_1   ''
         569	STORE_FAST        'data'

 139     572	LOAD_FAST         'quiet'
         575	JUMP_IF_TRUE      '601'

 140     578	LOAD_GLOBAL       'sys'
         581	LOAD_ATTR         'stderr'
         584	LOAD_ATTR         'write'
         587	LOAD_CONST        'Warning: %s\n'
         590	LOAD_FAST         'v'
         593	BINARY_MODULO     ''
         594	CALL_FUNCTION_1   ''
         597	POP_TOP           ''
         598	JUMP_ABSOLUTE     '605'
         601	JUMP_FORWARD      '605'
         604	END_FINALLY       ''
       605_0	COME_FROM         '496'
       605_1	COME_FROM         '604'

 141     605	LOAD_FAST         'out_file'
         608	LOAD_ATTR         'write'
         611	LOAD_FAST         'data'
         614	CALL_FUNCTION_1   ''
         617	POP_TOP           ''

 142     618	LOAD_FAST         'in_file'
         621	LOAD_ATTR         'readline'
         624	CALL_FUNCTION_0   ''
         627	STORE_FAST        's'
         630	JUMP_BACK         '453'
         633	POP_BLOCK         ''
       634_0	COME_FROM         '450'

 143     634	LOAD_FAST         's'
         637	JUMP_IF_TRUE      '655'

 144     640	LOAD_GLOBAL       'Error'
         643	LOAD_CONST        'Truncated input file'
         646	CALL_FUNCTION_1   ''
         649	RAISE_VARARGS_1   ''
         652	JUMP_FORWARD      '655'
       655_0	COME_FROM         '652'

 145     655	LOAD_FAST         'opened'
         658	JUMP_IF_FALSE     '674'

 146     661	LOAD_FAST         'out_file'
         664	LOAD_ATTR         'close'
         667	CALL_FUNCTION_0   ''
         670	POP_TOP           ''
         671	JUMP_FORWARD      '674'
       674_0	COME_FROM         '671'
         674	LOAD_CONST        ''
         677	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 633


def test():
    """uuencode/uudecode main program"""
    import optparse
    parser = optparse.OptionParser(usage='usage: %prog [-d] [-t] [input [output]]')
    parser.add_option('-d', '--decode', dest='decode', help='Decode (instead of encode)?', default=False, action='store_true')
    parser.add_option('-t', '--text', dest='text', help='data is text, encoded format unix-compatible text?', default=False, action='store_true')
    options, args = parser.parse_args()
    if len(args) > 2:
        parser.error('incorrect number of arguments')
        sys.exit(1)
    input = sys.stdin
    output = sys.stdout
    if len(args) > 0:
        input = args[0]
    if len(args) > 1:
        output = args[1]
    if options.decode:
        if options.text:
            if isinstance(output, basestring):
                output = open(output, 'w')
            else:
                print sys.argv[0], ': cannot do -t to stdout'
                sys.exit(1)
        decode(input, output)
    else:
        if options.text:
            if isinstance(input, basestring):
                input = open(input, 'r')
            else:
                print sys.argv[0], ': cannot do -t from stdin'
                sys.exit(1)
        encode(input, output)


if __name__ == '__main__':
    test()