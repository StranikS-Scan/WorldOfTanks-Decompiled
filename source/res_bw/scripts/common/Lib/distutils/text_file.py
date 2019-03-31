# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/text_file.py
# Compiled at: 2010-05-25 20:46:16
"""text_file

provides the TextFile class, which gives an interface to text files
that (optionally) takes care of stripping comments, ignoring blank
lines, and joining lines with backslashes."""
__revision__ = '$Id: text_file.py 60923 2008-02-21 18:18:37Z guido.van.rossum $'
from types import *
import sys, os, string

class TextFile():
    """Provides a file-like object that takes care of all the things you
    commonly want to do when processing a text file that has some
    line-by-line syntax: strip comments (as long as "#" is your
    comment character), skip blank lines, join adjacent lines by
    escaping the newline (ie. backslash at end of line), strip
    leading and/or trailing whitespace.  All of these are optional
    and independently controllable.
    
    Provides a 'warn()' method so you can generate warning messages that
    report physical line number, even if the logical line in question
    spans multiple physical lines.  Also provides 'unreadline()' for
    implementing line-at-a-time lookahead.
    
    Constructor is called as:
    
        TextFile (filename=None, file=None, **options)
    
    It bombs (RuntimeError) if both 'filename' and 'file' are None;
    'filename' should be a string, and 'file' a file object (or
    something that provides 'readline()' and 'close()' methods).  It is
    recommended that you supply at least 'filename', so that TextFile
    can include it in warning messages.  If 'file' is not supplied,
    TextFile creates its own using the 'open()' builtin.
    
    The options are all boolean, and affect the value returned by
    'readline()':
      strip_comments [default: true]
        strip from "#" to end-of-line, as well as any whitespace
        leading up to the "#" -- unless it is escaped by a backslash
      lstrip_ws [default: false]
        strip leading whitespace from each line before returning it
      rstrip_ws [default: true]
        strip trailing whitespace (including line terminator!) from
        each line before returning it
      skip_blanks [default: true}
        skip lines that are empty *after* stripping comments and
        whitespace.  (If both lstrip_ws and rstrip_ws are false,
        then some lines may consist of solely whitespace: these will
        *not* be skipped, even if 'skip_blanks' is true.)
      join_lines [default: false]
        if a backslash is the last non-newline character on a line
        after stripping comments and whitespace, join the following line
        to it to form one "logical line"; if N consecutive lines end
        with a backslash, then N+1 physical lines will be joined to
        form one logical line.
      collapse_join [default: false]
        strip leading whitespace from lines that are joined to their
        predecessor; only matters if (join_lines and not lstrip_ws)
    
    Note that since 'rstrip_ws' can strip the trailing newline, the
    semantics of 'readline()' must differ from those of the builtin file
    object's 'readline()' method!  In particular, 'readline()' returns
    None for end-of-file: an empty string might just be a blank line (or
    an all-whitespace line), if 'rstrip_ws' is true but 'skip_blanks' is
    not."""
    default_options = {'strip_comments': 1,
     'skip_blanks': 1,
     'lstrip_ws': 0,
     'rstrip_ws': 1,
     'join_lines': 0,
     'collapse_join': 0}

    def __init__(self, filename=None, file=None, **options):
        """Construct a new TextFile object.  At least one of 'filename'
        (a string) and 'file' (a file-like object) must be supplied.
        They keyword argument options are described above and affect
        the values returned by 'readline()'."""
        if filename is None and file is None:
            raise RuntimeError, "you must supply either or both of 'filename' and 'file'"
        for opt in self.default_options.keys():
            if opt in options:
                setattr(self, opt, options[opt])
            else:
                setattr(self, opt, self.default_options[opt])

        for opt in options.keys():
            if opt not in self.default_options:
                raise KeyError, "invalid TextFile option '%s'" % opt

        if file is None:
            self.open(filename)
        else:
            self.filename = filename
            self.file = file
            self.current_line = 0
        self.linebuf = []
        return

    def open(self, filename):
        """Open a new file named 'filename'.  This overrides both the
        'filename' and 'file' arguments to the constructor."""
        self.filename = filename
        self.file = open(self.filename, 'r')
        self.current_line = 0

    def close(self):
        """Close the current file and forget everything we know about it
        (filename, current line number)."""
        self.file.close()
        self.file = None
        self.filename = None
        self.current_line = None
        return

    def gen_error(self, msg, line=None):
        outmsg = []
        if line is None:
            line = self.current_line
        outmsg.append(self.filename + ', ')
        if type(line) in (ListType, TupleType):
            outmsg.append('lines %d-%d: ' % tuple(line))
        else:
            outmsg.append('line %d: ' % line)
        outmsg.append(str(msg))
        return string.join(outmsg, '')

    def error(self, msg, line=None):
        raise ValueError, 'error: ' + self.gen_error(msg, line)

    def warn(self, msg, line=None):
        """Print (to stderr) a warning message tied to the current logical
        line in the current file.  If the current logical line in the
        file spans multiple physical lines, the warning refers to the
        whole range, eg. "lines 3-5".  If 'line' supplied, it overrides
        the current line number; it may be a list or tuple to indicate a
        range of physical lines, or an integer for a single physical
        line."""
        sys.stderr.write('warning: ' + self.gen_error(msg, line) + '\n')

    def readline--- This code section failed: ---

 177       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'linebuf'
           6	JUMP_IF_FALSE     '36'

 178       9	LOAD_FAST         'self'
          12	LOAD_ATTR         'linebuf'
          15	LOAD_CONST        -1
          18	BINARY_SUBSCR     ''
          19	STORE_FAST        'line'

 179      22	LOAD_FAST         'self'
          25	LOAD_ATTR         'linebuf'
          28	LOAD_CONST        -1
          31	DELETE_SUBSCR     ''

 180      32	LOAD_FAST         'line'
          35	RETURN_END_IF     ''

 182      36	LOAD_CONST        ''
          39	STORE_FAST        'buildup_line'

 184      42	SETUP_LOOP        '709'

 186      45	LOAD_FAST         'self'
          48	LOAD_ATTR         'file'
          51	LOAD_ATTR         'readline'
          54	CALL_FUNCTION_0   ''
          57	STORE_FAST        'line'

 187      60	LOAD_FAST         'line'
          63	LOAD_CONST        ''
          66	COMPARE_OP        '=='
          69	JUMP_IF_FALSE     '81'
          72	LOAD_CONST        ''
          75	STORE_FAST        'line'
          78	JUMP_FORWARD      '81'
        81_0	COME_FROM         '78'

 189      81	LOAD_FAST         'self'
          84	LOAD_ATTR         'strip_comments'
          87	JUMP_IF_FALSE     '260'
          90	LOAD_FAST         'line'
        93_0	COME_FROM         '87'
          93	JUMP_IF_FALSE     '260'

 199      96	LOAD_GLOBAL       'string'
          99	LOAD_ATTR         'find'
         102	LOAD_FAST         'line'
         105	LOAD_CONST        '#'
         108	CALL_FUNCTION_2   ''
         111	STORE_FAST        'pos'

 200     114	LOAD_FAST         'pos'
         117	LOAD_CONST        -1
         120	COMPARE_OP        '=='
         123	JUMP_IF_FALSE     '129'

 201     126	JUMP_ABSOLUTE     '260'

 205     129	LOAD_FAST         'pos'
         132	LOAD_CONST        0
         135	COMPARE_OP        '=='
         138	JUMP_IF_TRUE      '161'
         141	LOAD_FAST         'line'
         144	LOAD_FAST         'pos'
         147	LOAD_CONST        1
         150	BINARY_SUBTRACT   ''
         151	BINARY_SUBSCR     ''
         152	LOAD_CONST        '\\'
         155	COMPARE_OP        '!='
       158_0	COME_FROM         '138'
         158	JUMP_IF_FALSE     '236'

 212     161	LOAD_FAST         'line'
         164	LOAD_CONST        -1
         167	BINARY_SUBSCR     ''
         168	LOAD_CONST        '\n'
         171	COMPARE_OP        '=='
         174	JUMP_IF_FALSE     '183'
         177	LOAD_CONST        '\n'
       180_0	COME_FROM         '174'
         180	JUMP_IF_TRUE      '186'
         183	LOAD_CONST        ''
         186	STORE_FAST        'eol'

 213     189	LOAD_FAST         'line'
         192	LOAD_CONST        0
         195	LOAD_FAST         'pos'
         198	SLICE+3           ''
         199	LOAD_FAST         'eol'
         202	BINARY_ADD        ''
         203	STORE_FAST        'line'

 222     206	LOAD_GLOBAL       'string'
         209	LOAD_ATTR         'strip'
         212	LOAD_FAST         'line'
         215	CALL_FUNCTION_1   ''
         218	LOAD_CONST        ''
         221	COMPARE_OP        '=='
         224	JUMP_IF_FALSE     '233'

 223     227	CONTINUE          '45'
         230	JUMP_ABSOLUTE     '257'
         233	JUMP_ABSOLUTE     '260'

 226     236	LOAD_GLOBAL       'string'
         239	LOAD_ATTR         'replace'
         242	LOAD_FAST         'line'
         245	LOAD_CONST        '\\#'
         248	LOAD_CONST        '#'
         251	CALL_FUNCTION_3   ''
         254	STORE_FAST        'line'
         257	JUMP_FORWARD      '260'
       260_0	COME_FROM         '257'

 230     260	LOAD_FAST         'self'
         263	LOAD_ATTR         'join_lines'
         266	JUMP_IF_FALSE     '417'
         269	LOAD_FAST         'buildup_line'
       272_0	COME_FROM         '266'
         272	JUMP_IF_FALSE     '417'

 232     275	LOAD_FAST         'line'
         278	LOAD_CONST        ''
         281	COMPARE_OP        'is'
         284	JUMP_IF_FALSE     '304'

 233     287	LOAD_FAST         'self'
         290	LOAD_ATTR         'warn'
         293	LOAD_CONST        'continuation line immediately precedes end-of-file'
         296	CALL_FUNCTION_1   ''
         299	POP_TOP           ''

 235     300	LOAD_FAST         'buildup_line'
         303	RETURN_END_IF     ''

 237     304	LOAD_FAST         'self'
         307	LOAD_ATTR         'collapse_join'
         310	JUMP_IF_FALSE     '331'

 238     313	LOAD_GLOBAL       'string'
         316	LOAD_ATTR         'lstrip'
         319	LOAD_FAST         'line'
         322	CALL_FUNCTION_1   ''
         325	STORE_FAST        'line'
         328	JUMP_FORWARD      '331'
       331_0	COME_FROM         '328'

 239     331	LOAD_FAST         'buildup_line'
         334	LOAD_FAST         'line'
         337	BINARY_ADD        ''
         338	STORE_FAST        'line'

 242     341	LOAD_GLOBAL       'type'
         344	LOAD_FAST         'self'
         347	LOAD_ATTR         'current_line'
         350	CALL_FUNCTION_1   ''
         353	LOAD_GLOBAL       'ListType'
         356	COMPARE_OP        'is'
         359	JUMP_IF_FALSE     '389'

 243     362	LOAD_FAST         'self'
         365	LOAD_ATTR         'current_line'
         368	LOAD_CONST        1
         371	BINARY_SUBSCR     ''
         372	LOAD_CONST        1
         375	BINARY_ADD        ''
         376	LOAD_FAST         'self'
         379	LOAD_ATTR         'current_line'
         382	LOAD_CONST        1
         385	STORE_SUBSCR      ''
         386	JUMP_ABSOLUTE     '493'

 245     389	LOAD_FAST         'self'
         392	LOAD_ATTR         'current_line'

 246     395	LOAD_FAST         'self'
         398	LOAD_ATTR         'current_line'
         401	LOAD_CONST        1
         404	BINARY_ADD        ''
         405	BUILD_LIST_2      ''
         408	LOAD_FAST         'self'
         411	STORE_ATTR        'current_line'
         414	JUMP_FORWARD      '493'

 249     417	LOAD_FAST         'line'
         420	LOAD_CONST        ''
         423	COMPARE_OP        'is'
         426	JUMP_IF_FALSE     '433'

 250     429	LOAD_CONST        ''
         432	RETURN_END_IF     ''

 253     433	LOAD_GLOBAL       'type'
         436	LOAD_FAST         'self'
         439	LOAD_ATTR         'current_line'
         442	CALL_FUNCTION_1   ''
         445	LOAD_GLOBAL       'ListType'
         448	COMPARE_OP        'is'
         451	JUMP_IF_FALSE     '477'

 254     454	LOAD_FAST         'self'
         457	LOAD_ATTR         'current_line'
         460	LOAD_CONST        1
         463	BINARY_SUBSCR     ''
         464	LOAD_CONST        1
         467	BINARY_ADD        ''
         468	LOAD_FAST         'self'
         471	STORE_ATTR        'current_line'
         474	JUMP_FORWARD      '493'

 256     477	LOAD_FAST         'self'
         480	LOAD_ATTR         'current_line'
         483	LOAD_CONST        1
         486	BINARY_ADD        ''
         487	LOAD_FAST         'self'
         490	STORE_ATTR        'current_line'
       493_0	COME_FROM         '414'
       493_1	COME_FROM         '474'

 261     493	LOAD_FAST         'self'
         496	LOAD_ATTR         'lstrip_ws'
         499	JUMP_IF_FALSE     '529'
         502	LOAD_FAST         'self'
         505	LOAD_ATTR         'rstrip_ws'
       508_0	COME_FROM         '499'
         508	JUMP_IF_FALSE     '529'

 262     511	LOAD_GLOBAL       'string'
         514	LOAD_ATTR         'strip'
         517	LOAD_FAST         'line'
         520	CALL_FUNCTION_1   ''
         523	STORE_FAST        'line'
         526	JUMP_FORWARD      '583'

 263     529	LOAD_FAST         'self'
         532	LOAD_ATTR         'lstrip_ws'
         535	JUMP_IF_FALSE     '556'

 264     538	LOAD_GLOBAL       'string'
         541	LOAD_ATTR         'lstrip'
         544	LOAD_FAST         'line'
         547	CALL_FUNCTION_1   ''
         550	STORE_FAST        'line'
         553	JUMP_FORWARD      '583'

 265     556	LOAD_FAST         'self'
         559	LOAD_ATTR         'rstrip_ws'
         562	JUMP_IF_FALSE     '583'

 266     565	LOAD_GLOBAL       'string'
         568	LOAD_ATTR         'rstrip'
         571	LOAD_FAST         'line'
         574	CALL_FUNCTION_1   ''
         577	STORE_FAST        'line'
         580	JUMP_FORWARD      '583'
       583_0	COME_FROM         '526'
       583_1	COME_FROM         '553'
       583_2	COME_FROM         '580'

 270     583	LOAD_FAST         'line'
         586	LOAD_CONST        ''
         589	COMPARE_OP        '=='
         592	JUMP_IF_TRUE      '607'
         595	LOAD_FAST         'line'
         598	LOAD_CONST        '\n'
         601	COMPARE_OP        '=='
       604_0	COME_FROM         '592'
         604	JUMP_IF_FALSE     '622'
         607	LOAD_FAST         'self'
         610	LOAD_ATTR         'skip_blanks'
       613_0	COME_FROM         '604'
         613	JUMP_IF_FALSE     '622'

 271     616	CONTINUE          '45'
         619	JUMP_FORWARD      '622'
       622_0	COME_FROM         '619'

 273     622	LOAD_FAST         'self'
         625	LOAD_ATTR         'join_lines'
         628	JUMP_IF_FALSE     '705'

 274     631	LOAD_FAST         'line'
         634	LOAD_CONST        -1
         637	BINARY_SUBSCR     ''
         638	LOAD_CONST        '\\'
         641	COMPARE_OP        '=='
         644	JUMP_IF_FALSE     '663'

 275     647	LOAD_FAST         'line'
         650	LOAD_CONST        -1
         653	SLICE+2           ''
         654	STORE_FAST        'buildup_line'

 276     657	CONTINUE          '45'
         660	JUMP_FORWARD      '663'
       663_0	COME_FROM         '660'

 278     663	LOAD_FAST         'line'
         666	LOAD_CONST        -2
         669	SLICE+1           ''
         670	LOAD_CONST        '\\\n'
         673	COMPARE_OP        '=='
         676	JUMP_IF_FALSE     '702'

 279     679	LOAD_FAST         'line'
         682	LOAD_CONST        0
         685	LOAD_CONST        -2
         688	SLICE+3           ''
         689	LOAD_CONST        '\n'
         692	BINARY_ADD        ''
         693	STORE_FAST        'buildup_line'

 280     696	CONTINUE          '45'
         699	JUMP_ABSOLUTE     '705'
         702	JUMP_FORWARD      '705'
       705_0	COME_FROM         '702'

 283     705	LOAD_FAST         'line'
         708	RETURN_VALUE      ''
       709_0	COME_FROM         '42'
         709	LOAD_CONST        ''
         712	RETURN_VALUE      ''

Syntax error at or near 'COME_FROM' token at offset 709_0

    def readlines(self):
        """Read and return the list of all logical lines remaining in the
        current file."""
        lines = []
        while 1:
            line = self.readline()
            if line is None:
                return lines
            lines.append(line)

        return

    def unreadline(self, line):
        """Push 'line' (a string) onto an internal buffer that will be
        checked by future 'readline()' calls.  Handy for implementing
        a parser with line-at-a-time lookahead."""
        self.linebuf.append(line)


if __name__ == '__main__':
    test_data = '# test file\n\nline 3 \\\n# intervening comment\n  continues on next line\n'
    result1 = map(lambda x: x + '\n', string.split(test_data, '\n')[0:-1])
    result2 = ['\n', 'line 3 \\\n', '  continues on next line\n']
    result3 = ['# test file\n',
     'line 3 \\\n',
     '# intervening comment\n',
     '  continues on next line\n']
    result4 = ['line 3 \\', '  continues on next line']
    result5 = ['line 3   continues on next line']
    result6 = ['line 3 continues on next line']

    def test_input(count, description, file, expected_result):
        result = file.readlines()
        if result == expected_result:
            print 'ok %d (%s)' % (count, description)
        else:
            print 'not ok %d (%s):' % (count, description)
            print '** expected:'
            print expected_result
            print '** received:'
            print result


    filename = 'test.txt'
    out_file = open(filename, 'w')
    out_file.write(test_data)
    out_file.close()
    in_file = TextFile(filename, strip_comments=0, skip_blanks=0, lstrip_ws=0, rstrip_ws=0)
    test_input(1, 'no processing', in_file, result1)
    in_file = TextFile(filename, strip_comments=1, skip_blanks=0, lstrip_ws=0, rstrip_ws=0)
    test_input(2, 'strip comments', in_file, result2)
    in_file = TextFile(filename, strip_comments=0, skip_blanks=1, lstrip_ws=0, rstrip_ws=0)
    test_input(3, 'strip blanks', in_file, result3)
    in_file = TextFile(filename)
    test_input(4, 'default processing', in_file, result4)
    in_file = TextFile(filename, strip_comments=1, skip_blanks=1, join_lines=1, rstrip_ws=1)
    test_input(5, 'join lines without collapsing', in_file, result5)
    in_file = TextFile(filename, strip_comments=1, skip_blanks=1, join_lines=1, rstrip_ws=1, collapse_join=1)
    test_input(6, 'join lines with collapsing', in_file, result6)
    os.remove(filename)