# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/csv.py
# Compiled at: 2010-05-25 20:46:16
"""
csv.py - read/write/investigate CSV files
"""
import re
from functools import reduce
from _csv import Error, __version__, writer, reader, register_dialect, unregister_dialect, get_dialect, list_dialects, field_size_limit, QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE, __doc__
from _csv import Dialect as _Dialect
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = ['QUOTE_MINIMAL',
 'QUOTE_ALL',
 'QUOTE_NONNUMERIC',
 'QUOTE_NONE',
 'Error',
 'Dialect',
 '__doc__',
 'excel',
 'excel_tab',
 'field_size_limit',
 'reader',
 'writer',
 'register_dialect',
 'get_dialect',
 'list_dialects',
 'Sniffer',
 'unregister_dialect',
 '__version__',
 'DictReader',
 'DictWriter']

class Dialect:
    """Describe an Excel dialect.
    
    This must be subclassed (see csv.excel).  Valid attributes are:
    delimiter, quotechar, escapechar, doublequote, skipinitialspace,
    lineterminator, quoting.
    
    """
    _name = ''
    _valid = False
    delimiter = None
    quotechar = None
    escapechar = None
    doublequote = None
    skipinitialspace = None
    lineterminator = None
    quoting = None

    def __init__(self):
        if self.__class__ != Dialect:
            self._valid = True
        self._validate()

    def _validate(self):
        try:
            _Dialect(self)
        except TypeError as e:
            raise Error(str(e))


class excel(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL


register_dialect('excel', excel)

class excel_tab(excel):
    """Describe the usual properties of Excel-generated TAB-delimited files."""
    delimiter = '\t'


register_dialect('excel-tab', excel_tab)

class DictReader:

    def __init__(self, f, fieldnames=None, restkey=None, restval=None, dialect='excel', *args, **kwds):
        self._fieldnames = fieldnames
        self.restkey = restkey
        self.restval = restval
        self.reader = reader(f, dialect, *args, **kwds)
        self.dialect = dialect
        self.line_num = 0

    def __iter__(self):
        return self

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = self.reader.next()
            except StopIteration:
                pass

        self.line_num = self.reader.line_num
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    def next(self):
        if self.line_num == 0:
            self.fieldnames
        row = self.reader.next()
        self.line_num = self.reader.line_num
        while 1:
            row = row == [] and self.reader.next()

        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval

        return d


class DictWriter:

    def __init__(self, f, fieldnames, restval='', extrasaction='raise', dialect='excel', *args, **kwds):
        self.fieldnames = fieldnames
        self.restval = restval
        if extrasaction.lower() not in ('raise', 'ignore'):
            raise ValueError, "extrasaction (%s) must be 'raise' or 'ignore'" % extrasaction
        self.extrasaction = extrasaction
        self.writer = writer(f, dialect, *args, **kwds)

    def _dict_to_list(self, rowdict):
        if self.extrasaction == 'raise':
            wrong_fields = [ k for k in rowdict if k not in self.fieldnames ]
            if wrong_fields:
                raise ValueError('dict contains fields not in fieldnames: ' + ', '.join(wrong_fields))
        return [ rowdict.get(key, self.restval) for key in self.fieldnames ]

    def writerow(self, rowdict):
        return self.writer.writerow(self._dict_to_list(rowdict))

    def writerows(self, rowdicts):
        rows = []
        for rowdict in rowdicts:
            rows.append(self._dict_to_list(rowdict))

        return self.writer.writerows(rows)


try:
    complex
except NameError:
    complex = float

class Sniffer:
    """
    "Sniffs" the format of a CSV file (i.e. delimiter, quotechar)
    Returns a Dialect object.
    """

    def __init__(self):
        self.preferred = [',',
         '\t',
         ';',
         ' ',
         ':']

    def sniff(self, sample, delimiters=None):
        """
        Returns a dialect (or None) corresponding to the sample
        """
        quotechar, delimiter, skipinitialspace = self._guess_quote_and_delimiter(sample, delimiters)
        if not delimiter:
            delimiter, skipinitialspace = self._guess_delimiter(sample, delimiters)
        if not delimiter:
            raise Error, 'Could not determine delimiter'

        class dialect(Dialect):
            _name = 'sniffed'
            lineterminator = '\r\n'
            quoting = QUOTE_MINIMAL
            doublequote = False

        dialect.delimiter = delimiter
        dialect.quotechar = quotechar or '"'
        dialect.skipinitialspace = skipinitialspace
        return dialect

    def _guess_quote_and_delimiter(self, data, delimiters):
        """
        Looks for text enclosed between two identical quotes
        (the probable quotechar) which are preceded and followed
        by the same character (the probable delimiter).
        For example:
                         ,'some text',
        The quote with the most wins, same with the delimiter.
        If there is no quotechar the delimiter can't be determined
        this way.
        """
        matches = []
        for restr in ('(?P<delim>[^\\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?P=delim)', '(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?P<delim>[^\\w\n"\'])(?P<space> ?)', '(?P<delim>>[^\\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?:$|\n)', '(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?:$|\n)'):
            regexp = re.compile(restr, re.DOTALL | re.MULTILINE)
            matches = regexp.findall(data)
            if matches:
                break

        if not matches:
            return ('', None, 0)
        else:
            quotes = {}
            delims = {}
            spaces = 0
            for m in matches:
                n = regexp.groupindex['quote'] - 1
                key = m[n]
                if key:
                    quotes[key] = quotes.get(key, 0) + 1
                try:
                    n = regexp.groupindex['delim'] - 1
                    key = m[n]
                except KeyError:
                    continue

                if key and (delimiters is None or key in delimiters):
                    delims[key] = delims.get(key, 0) + 1
                try:
                    n = regexp.groupindex['space'] - 1
                except KeyError:
                    continue

                if m[n]:
                    spaces += 1

            quotechar = reduce(lambda a, b, quotes=quotes: quotes[a] > quotes[b] and a or b, quotes.keys())
            if delims:
                delim = reduce(lambda a, b, delims=delims: delims[a] > delims[b] and a or b, delims.keys())
                skipinitialspace = delims[delim] == spaces
                if delim == '\n':
                    delim = ''
            else:
                delim = ''
                skipinitialspace = 0
            return (quotechar, delim, skipinitialspace)

    def _guess_delimiter--- This code section failed: ---

 279       0	LOAD_GLOBAL       'filter'
           3	LOAD_CONST        ''
           6	LOAD_FAST         'data'
           9	LOAD_ATTR         'split'
          12	LOAD_CONST        '\n'
          15	CALL_FUNCTION_1   ''
          18	CALL_FUNCTION_2   ''
          21	STORE_FAST        'data'

 281      24	BUILD_LIST_0      ''
          27	LOAD_GLOBAL       'range'
          30	LOAD_CONST        127
          33	CALL_FUNCTION_1   ''
          36	GET_ITER          ''
          37	FOR_ITER          '58'
          40	STORE_FAST        'c'
          43	LOAD_GLOBAL       'chr'
          46	LOAD_FAST         'c'
          49	CALL_FUNCTION_1   ''
          52	LIST_APPEND       ''
          55	JUMP_BACK         '37'
          58	STORE_FAST        'ascii'

 284      61	LOAD_GLOBAL       'min'
          64	LOAD_CONST        10
          67	LOAD_GLOBAL       'len'
          70	LOAD_FAST         'data'
          73	CALL_FUNCTION_1   ''
          76	CALL_FUNCTION_2   ''
          79	STORE_FAST        'chunkLength'

 285      82	LOAD_CONST        0
          85	STORE_FAST        'iteration'

 286      88	BUILD_MAP         ''
          91	STORE_FAST        'charFrequency'

 287      94	BUILD_MAP         ''
          97	STORE_FAST        'modes'

 288     100	BUILD_MAP         ''
         103	STORE_FAST        'delims'

 289     106	LOAD_CONST        0
         109	LOAD_GLOBAL       'min'
         112	LOAD_FAST         'chunkLength'
         115	LOAD_GLOBAL       'len'
         118	LOAD_FAST         'data'
         121	CALL_FUNCTION_1   ''
         124	CALL_FUNCTION_2   ''
         127	ROT_TWO           ''
         128	STORE_FAST        'start'
         131	STORE_FAST        'end'

 290     134	SETUP_LOOP        '792'
         137	LOAD_FAST         'start'
         140	LOAD_GLOBAL       'len'
         143	LOAD_FAST         'data'
         146	CALL_FUNCTION_1   ''
         149	COMPARE_OP        '<'
         152	JUMP_IF_FALSE     '791'

 291     155	LOAD_FAST         'iteration'
         158	LOAD_CONST        1
         161	INPLACE_ADD       ''
         162	STORE_FAST        'iteration'

 292     165	SETUP_LOOP        '275'
         168	LOAD_FAST         'data'
         171	LOAD_FAST         'start'
         174	LOAD_FAST         'end'
         177	SLICE+3           ''
         178	GET_ITER          ''
         179	FOR_ITER          '274'
         182	STORE_FAST        'line'

 293     185	SETUP_LOOP        '271'
         188	LOAD_FAST         'ascii'
         191	GET_ITER          ''
         192	FOR_ITER          '270'
         195	STORE_FAST        'char'

 294     198	LOAD_FAST         'charFrequency'
         201	LOAD_ATTR         'get'
         204	LOAD_FAST         'char'
         207	BUILD_MAP         ''
         210	CALL_FUNCTION_2   ''
         213	STORE_FAST        'metaFrequency'

 296     216	LOAD_FAST         'line'
         219	LOAD_ATTR         'count'
         222	LOAD_FAST         'char'
         225	CALL_FUNCTION_1   ''
         228	STORE_FAST        'freq'

 298     231	LOAD_FAST         'metaFrequency'
         234	LOAD_ATTR         'get'
         237	LOAD_FAST         'freq'
         240	LOAD_CONST        0
         243	CALL_FUNCTION_2   ''
         246	LOAD_CONST        1
         249	BINARY_ADD        ''
         250	LOAD_FAST         'metaFrequency'
         253	LOAD_FAST         'freq'
         256	STORE_SUBSCR      ''

 299     257	LOAD_FAST         'metaFrequency'
         260	LOAD_FAST         'charFrequency'
         263	LOAD_FAST         'char'
         266	STORE_SUBSCR      ''
         267	JUMP_BACK         '192'
         270	POP_BLOCK         ''
       271_0	COME_FROM         '185'
         271	JUMP_BACK         '179'
         274	POP_BLOCK         ''
       275_0	COME_FROM         '165'

 301     275	SETUP_LOOP        '484'
         278	LOAD_FAST         'charFrequency'
         281	LOAD_ATTR         'keys'
         284	CALL_FUNCTION_0   ''
         287	GET_ITER          ''
         288	FOR_ITER          '483'
         291	STORE_FAST        'char'

 302     294	LOAD_FAST         'charFrequency'
         297	LOAD_FAST         'char'
         300	BINARY_SUBSCR     ''
         301	LOAD_ATTR         'items'
         304	CALL_FUNCTION_0   ''
         307	STORE_FAST        'items'

 303     310	LOAD_GLOBAL       'len'
         313	LOAD_FAST         'items'
         316	CALL_FUNCTION_1   ''
         319	LOAD_CONST        1
         322	COMPARE_OP        '=='
         325	JUMP_IF_FALSE     '354'
         328	LOAD_FAST         'items'
         331	LOAD_CONST        0
         334	BINARY_SUBSCR     ''
         335	LOAD_CONST        0
         338	BINARY_SUBSCR     ''
         339	LOAD_CONST        0
         342	COMPARE_OP        '=='
       345_0	COME_FROM         '325'
         345	JUMP_IF_FALSE     '354'

 304     348	CONTINUE          '288'
         351	JUMP_FORWARD      '354'
       354_0	COME_FROM         '351'

 306     354	LOAD_GLOBAL       'len'
         357	LOAD_FAST         'items'
         360	CALL_FUNCTION_1   ''
         363	LOAD_CONST        1
         366	COMPARE_OP        '>'
         369	JUMP_IF_FALSE     '466'

 307     372	LOAD_GLOBAL       'reduce'
         375	LOAD_LAMBDA       '<code_object <lambda>>'
         378	MAKE_FUNCTION_0   ''

 308     381	LOAD_FAST         'items'
         384	CALL_FUNCTION_2   ''
         387	LOAD_FAST         'modes'
         390	LOAD_FAST         'char'
         393	STORE_SUBSCR      ''

 311     394	LOAD_FAST         'items'
         397	LOAD_ATTR         'remove'
         400	LOAD_FAST         'modes'
         403	LOAD_FAST         'char'
         406	BINARY_SUBSCR     ''
         407	CALL_FUNCTION_1   ''
         410	POP_TOP           ''

 312     411	LOAD_FAST         'modes'
         414	LOAD_FAST         'char'
         417	BINARY_SUBSCR     ''
         418	LOAD_CONST        0
         421	BINARY_SUBSCR     ''
         422	LOAD_FAST         'modes'
         425	LOAD_FAST         'char'
         428	BINARY_SUBSCR     ''
         429	LOAD_CONST        1
         432	BINARY_SUBSCR     ''

 313     433	LOAD_GLOBAL       'reduce'
         436	LOAD_LAMBDA       '<code_object <lambda>>'
         439	MAKE_FUNCTION_0   ''

 314     442	LOAD_FAST         'items'
         445	CALL_FUNCTION_2   ''
         448	LOAD_CONST        1
         451	BINARY_SUBSCR     ''
         452	BINARY_SUBTRACT   ''
         453	BUILD_TUPLE_2     ''
         456	LOAD_FAST         'modes'
         459	LOAD_FAST         'char'
         462	STORE_SUBSCR      ''
         463	JUMP_BACK         '288'

 316     466	LOAD_FAST         'items'
         469	LOAD_CONST        0
         472	BINARY_SUBSCR     ''
         473	LOAD_FAST         'modes'
         476	LOAD_FAST         'char'
         479	STORE_SUBSCR      ''
         480	JUMP_BACK         '288'
         483	POP_BLOCK         ''
       484_0	COME_FROM         '275'

 319     484	LOAD_FAST         'modes'
         487	LOAD_ATTR         'items'
         490	CALL_FUNCTION_0   ''
         493	STORE_FAST        'modeList'

 320     496	LOAD_GLOBAL       'float'
         499	LOAD_FAST         'chunkLength'
         502	LOAD_FAST         'iteration'
         505	BINARY_MULTIPLY   ''
         506	CALL_FUNCTION_1   ''
         509	STORE_FAST        'total'

 322     512	LOAD_CONST        1.0
         515	STORE_FAST        'consistency'

 324     518	LOAD_CONST        0.9
         521	STORE_FAST        'threshold'

 325     524	SETUP_LOOP        '686'
         527	LOAD_GLOBAL       'len'
         530	LOAD_FAST         'delims'
         533	CALL_FUNCTION_1   ''
         536	LOAD_CONST        0
         539	COMPARE_OP        '=='
         542	JUMP_IF_FALSE     '685'
         545	LOAD_FAST         'consistency'
         548	LOAD_FAST         'threshold'
         551	COMPARE_OP        '>='
       554_0	COME_FROM         '542'
         554	JUMP_IF_FALSE     '685'

 326     557	SETUP_LOOP        '672'
         560	LOAD_FAST         'modeList'
         563	GET_ITER          ''
         564	FOR_ITER          '671'
         567	UNPACK_SEQUENCE_2 ''
         570	STORE_FAST        'k'
         573	STORE_FAST        'v'

 327     576	LOAD_FAST         'v'
         579	LOAD_CONST        0
         582	BINARY_SUBSCR     ''
         583	LOAD_CONST        0
         586	COMPARE_OP        '>'
         589	JUMP_IF_FALSE     '668'
         592	LOAD_FAST         'v'
         595	LOAD_CONST        1
         598	BINARY_SUBSCR     ''
         599	LOAD_CONST        0
         602	COMPARE_OP        '>'
       605_0	COME_FROM         '589'
         605	JUMP_IF_FALSE     '668'

 328     608	LOAD_FAST         'v'
         611	LOAD_CONST        1
         614	BINARY_SUBSCR     ''
         615	LOAD_FAST         'total'
         618	BINARY_DIVIDE     ''
         619	LOAD_FAST         'consistency'
         622	COMPARE_OP        '>='
         625	JUMP_IF_FALSE     '665'

 329     628	LOAD_FAST         'delimiters'
         631	LOAD_CONST        ''
         634	COMPARE_OP        'is'
         637	JUMP_IF_TRUE      '652'
         640	LOAD_FAST         'k'
         643	LOAD_FAST         'delimiters'
         646	COMPARE_OP        'in'
       649_0	COME_FROM         '625'
       649_1	COME_FROM         '637'
         649	JUMP_IF_FALSE     '665'

 330     652	LOAD_FAST         'v'
         655	LOAD_FAST         'delims'
         658	LOAD_FAST         'k'
         661	STORE_SUBSCR      ''
         662	JUMP_ABSOLUTE     '668'
         665	JUMP_BACK         '564'
         668	JUMP_BACK         '564'
         671	POP_BLOCK         ''
       672_0	COME_FROM         '557'

 331     672	LOAD_FAST         'consistency'
         675	LOAD_CONST        0.01
         678	INPLACE_SUBTRACT  ''
         679	STORE_FAST        'consistency'
         682	JUMP_BACK         '527'
         685	POP_BLOCK         ''
       686_0	COME_FROM         '524'

 333     686	LOAD_GLOBAL       'len'
         689	LOAD_FAST         'delims'
         692	CALL_FUNCTION_1   ''
         695	LOAD_CONST        1
         698	COMPARE_OP        '=='
         701	JUMP_IF_FALSE     '772'

 334     704	LOAD_FAST         'delims'
         707	LOAD_ATTR         'keys'
         710	CALL_FUNCTION_0   ''
         713	LOAD_CONST        0
         716	BINARY_SUBSCR     ''
         717	STORE_FAST        'delim'

 335     720	LOAD_FAST         'data'
         723	LOAD_CONST        0
         726	BINARY_SUBSCR     ''
         727	LOAD_ATTR         'count'
         730	LOAD_FAST         'delim'
         733	CALL_FUNCTION_1   ''

 336     736	LOAD_FAST         'data'
         739	LOAD_CONST        0
         742	BINARY_SUBSCR     ''
         743	LOAD_ATTR         'count'
         746	LOAD_CONST        '%c '
         749	LOAD_FAST         'delim'
         752	BINARY_MODULO     ''
         753	CALL_FUNCTION_1   ''
         756	COMPARE_OP        '=='
         759	STORE_FAST        'skipinitialspace'

 337     762	LOAD_FAST         'delim'
         765	LOAD_FAST         'skipinitialspace'
         768	BUILD_TUPLE_2     ''
         771	RETURN_END_IF     ''

 340     772	LOAD_FAST         'end'
         775	STORE_FAST        'start'

 341     778	LOAD_FAST         'end'
         781	LOAD_FAST         'chunkLength'
         784	INPLACE_ADD       ''
         785	STORE_FAST        'end'
         788	JUMP_BACK         '137'
         791	POP_BLOCK         ''
       792_0	COME_FROM         '134'

 343     792	LOAD_FAST         'delims'
         795	JUMP_IF_TRUE      '802'

 344     798	LOAD_CONST        ('', 0)
         801	RETURN_END_IF     ''

 347     802	LOAD_GLOBAL       'len'
         805	LOAD_FAST         'delims'
         808	CALL_FUNCTION_1   ''
         811	LOAD_CONST        1
         814	COMPARE_OP        '>'
         817	JUMP_IF_FALSE     '913'

 348     820	SETUP_LOOP        '913'
         823	LOAD_FAST         'self'
         826	LOAD_ATTR         'preferred'
         829	GET_ITER          ''
         830	FOR_ITER          '909'
         833	STORE_FAST        'd'

 349     836	LOAD_FAST         'd'
         839	LOAD_FAST         'delims'
         842	LOAD_ATTR         'keys'
         845	CALL_FUNCTION_0   ''
         848	COMPARE_OP        'in'
         851	JUMP_IF_FALSE     '906'

 350     854	LOAD_FAST         'data'
         857	LOAD_CONST        0
         860	BINARY_SUBSCR     ''
         861	LOAD_ATTR         'count'
         864	LOAD_FAST         'd'
         867	CALL_FUNCTION_1   ''

 351     870	LOAD_FAST         'data'
         873	LOAD_CONST        0
         876	BINARY_SUBSCR     ''
         877	LOAD_ATTR         'count'
         880	LOAD_CONST        '%c '
         883	LOAD_FAST         'd'
         886	BINARY_MODULO     ''
         887	CALL_FUNCTION_1   ''
         890	COMPARE_OP        '=='
         893	STORE_FAST        'skipinitialspace'

 352     896	LOAD_FAST         'd'
         899	LOAD_FAST         'skipinitialspace'
         902	BUILD_TUPLE_2     ''
         905	RETURN_END_IF     ''
         906	JUMP_BACK         '830'
         909	POP_BLOCK         ''
       910_0	COME_FROM         '820'
         910	JUMP_FORWARD      '913'
       913_0	COME_FROM         '910'

 356     913	BUILD_LIST_0      ''
         916	LOAD_FAST         'delims'
         919	LOAD_ATTR         'items'
         922	CALL_FUNCTION_0   ''
         925	GET_ITER          ''
         926	FOR_ITER          '953'
         929	UNPACK_SEQUENCE_2 ''
         932	STORE_FAST        'k'
         935	STORE_FAST        'v'
         938	LOAD_FAST         'v'
         941	LOAD_FAST         'k'
         944	BUILD_TUPLE_2     ''
         947	LIST_APPEND       ''
         950	JUMP_BACK         '926'
         953	STORE_FAST        'items'

 357     956	LOAD_FAST         'items'
         959	LOAD_ATTR         'sort'
         962	CALL_FUNCTION_0   ''
         965	POP_TOP           ''

 358     966	LOAD_FAST         'items'
         969	LOAD_CONST        -1
         972	BINARY_SUBSCR     ''
         973	LOAD_CONST        1
         976	BINARY_SUBSCR     ''
         977	STORE_FAST        'delim'

 360     980	LOAD_FAST         'data'
         983	LOAD_CONST        0
         986	BINARY_SUBSCR     ''
         987	LOAD_ATTR         'count'
         990	LOAD_FAST         'delim'
         993	CALL_FUNCTION_1   ''

 361     996	LOAD_FAST         'data'
         999	LOAD_CONST        0
        1002	BINARY_SUBSCR     ''
        1003	LOAD_ATTR         'count'
        1006	LOAD_CONST        '%c '
        1009	LOAD_FAST         'delim'
        1012	BINARY_MODULO     ''
        1013	CALL_FUNCTION_1   ''
        1016	COMPARE_OP        '=='
        1019	STORE_FAST        'skipinitialspace'

 362    1022	LOAD_FAST         'delim'
        1025	LOAD_FAST         'skipinitialspace'
        1028	BUILD_TUPLE_2     ''
        1031	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 685

    def has_header(self, sample):
        rdr = reader(StringIO(sample), self.sniff(sample))
        header = rdr.next()
        columns = len(header)
        columnTypes = {}
        for i in range(columns):
            columnTypes[i] = None

        checked = 0
        for row in rdr:
            if checked > 20:
                break
            checked += 1
            if len(row) != columns:
                continue
            for col in columnTypes.keys():
                for thisType in [int,
                 long,
                 float,
                 complex]:
                    try:
                        thisType(row[col])
                        break
                    except (ValueError, OverflowError):
                        pass

                else:
                    thisType = len(row[col])

                if thisType == long:
                    thisType = int
                if thisType != columnTypes[col]:
                    if columnTypes[col] is None:
                        columnTypes[col] = thisType
                    else:
                        del columnTypes[col]

        hasHeader = 0
        for col, colType in columnTypes.items():
            if type(colType) == type(0):
                if len(header[col]) != colType:
                    hasHeader += 1
                else:
                    hasHeader -= 1
            else:
                try:
                    colType(header[col])
                except (ValueError, TypeError):
                    hasHeader += 1
                else:
                    hasHeader -= 1

        return hasHeader > 0