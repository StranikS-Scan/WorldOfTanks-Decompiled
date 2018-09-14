# Embedded file name: scripts/common/Lib/idlelib/PyParse.py
import re
import sys
C_NONE, C_BACKSLASH, C_STRING_FIRST_LINE, C_STRING_NEXT_LINES, C_BRACKET = range(5)
_synchre = re.compile('\n    ^\n    [ \\t]*\n    (?: while\n    |   else\n    |   def\n    |   return\n    |   assert\n    |   break\n    |   class\n    |   continue\n    |   elif\n    |   try\n    |   except\n    |   raise\n    |   import\n    |   yield\n    )\n    \\b\n', re.VERBOSE | re.MULTILINE).search
_junkre = re.compile('\n    [ \\t]*\n    (?: \\# \\S .* )?\n    \\n\n', re.VERBOSE).match
_match_stringre = re.compile('\n    \\""" [^"\\\\]* (?:\n                     (?: \\\\. | "(?!"") )\n                     [^"\\\\]*\n                 )*\n    (?: \\""" )?\n\n|   " [^"\\\\\\n]* (?: \\\\. [^"\\\\\\n]* )* "?\n\n|   \'\'\' [^\'\\\\]* (?:\n                   (?: \\\\. | \'(?!\'\') )\n                   [^\'\\\\]*\n                )*\n    (?: \'\'\' )?\n\n|   \' [^\'\\\\\\n]* (?: \\\\. [^\'\\\\\\n]* )* \'?\n', re.VERBOSE | re.DOTALL).match
_itemre = re.compile('\n    [ \\t]*\n    [^\\s#\\\\]    # if we match, m.end()-1 is the interesting char\n', re.VERBOSE).match
_closere = re.compile('\n    \\s*\n    (?: return\n    |   break\n    |   continue\n    |   raise\n    |   pass\n    )\n    \\b\n', re.VERBOSE).match
_chew_ordinaryre = re.compile('\n    [^[\\](){}#\'"\\\\]+\n', re.VERBOSE).match
_tran = ['x'] * 256
for ch in '({[':
    _tran[ord(ch)] = '('

for ch in ')}]':
    _tran[ord(ch)] = ')'

for ch in '"\'\\\n#':
    _tran[ord(ch)] = ch

_tran = ''.join(_tran)
del ch
try:
    UnicodeType = type(unicode(''))
except NameError:
    UnicodeType = None

class Parser:

    def __init__(self, indentwidth, tabwidth):
        self.indentwidth = indentwidth
        self.tabwidth = tabwidth

    def set_str(self, str):
        if not (len(str) == 0 or str[-1] == '\n'):
            raise AssertionError
            uniphooey = type(str) is UnicodeType and str
            str = []
            push = str.append
            for raw in map(ord, uniphooey):
                push(raw < 127 and chr(raw) or 'x')

            str = ''.join(str)
        self.str = str
        self.study_level = 0

    def find_good_parse_start(self, is_char_in_string = None, _synchre = _synchre):
        str, pos = self.str, None
        if not is_char_in_string:
            return
        else:
            limit = len(str)
            for tries in range(5):
                i = str.rfind(':\n', 0, limit)
                if i < 0:
                    break
                i = str.rfind('\n', 0, i) + 1
                m = _synchre(str, i, limit)
                if m and not is_char_in_string(m.start()):
                    pos = m.start()
                    break
                limit = i

            if pos is None:
                m = _synchre(str)
                if m and not is_char_in_string(m.start()):
                    pos = m.start()
                return pos
            i = pos + 1
            while 1:
                m = _synchre(str, i)
                if m:
                    s, i = m.span()
                    if not is_char_in_string(s):
                        pos = s
                else:
                    break

            return pos

    def set_lo(self, lo):
        if not (lo == 0 or self.str[lo - 1] == '\n'):
            raise AssertionError
            self.str = lo > 0 and self.str[lo:]

    def _study1--- This code section failed: ---

0	LOAD_FAST         'self'
3	LOAD_ATTR         'study_level'
6	LOAD_CONST        1
9	COMPARE_OP        '>='
12	POP_JUMP_IF_FALSE '19'

15	LOAD_CONST        None
18	RETURN_END_IF     None

19	LOAD_CONST        1
22	LOAD_FAST         'self'
25	STORE_ATTR        'study_level'

28	LOAD_FAST         'self'
31	LOAD_ATTR         'str'
34	STORE_FAST        'str'

37	LOAD_FAST         'str'
40	LOAD_ATTR         'translate'
43	LOAD_GLOBAL       '_tran'
46	CALL_FUNCTION_1   None
49	STORE_FAST        'str'

52	LOAD_FAST         'str'
55	LOAD_ATTR         'replace'
58	LOAD_CONST        'xxxxxxxx'
61	LOAD_CONST        'x'
64	CALL_FUNCTION_2   None
67	STORE_FAST        'str'

70	LOAD_FAST         'str'
73	LOAD_ATTR         'replace'
76	LOAD_CONST        'xxxx'
79	LOAD_CONST        'x'
82	CALL_FUNCTION_2   None
85	STORE_FAST        'str'

88	LOAD_FAST         'str'
91	LOAD_ATTR         'replace'
94	LOAD_CONST        'xx'
97	LOAD_CONST        'x'
100	CALL_FUNCTION_2   None
103	STORE_FAST        'str'

106	LOAD_FAST         'str'
109	LOAD_ATTR         'replace'
112	LOAD_CONST        'xx'
115	LOAD_CONST        'x'
118	CALL_FUNCTION_2   None
121	STORE_FAST        'str'

124	LOAD_FAST         'str'
127	LOAD_ATTR         'replace'
130	LOAD_CONST        '\nx'
133	LOAD_CONST        '\n'
136	CALL_FUNCTION_2   None
139	STORE_FAST        'str'

142	LOAD_GLOBAL       'C_NONE'
145	STORE_FAST        'continuation'

148	LOAD_CONST        0
151	DUP_TOP           None
152	STORE_FAST        'level'
155	STORE_FAST        'lno'

158	LOAD_CONST        0
161	BUILD_LIST_1      None
164	DUP_TOP           None
165	LOAD_FAST         'self'
168	STORE_ATTR        'goodlines'
171	STORE_FAST        'goodlines'

174	LOAD_FAST         'goodlines'
177	LOAD_ATTR         'append'
180	STORE_FAST        'push_good'

183	LOAD_CONST        0
186	LOAD_GLOBAL       'len'
189	LOAD_FAST         'str'
192	CALL_FUNCTION_1   None
195	ROT_TWO           None
196	STORE_FAST        'i'
199	STORE_FAST        'n'

202	SETUP_LOOP        '916'
205	LOAD_FAST         'i'
208	LOAD_FAST         'n'
211	COMPARE_OP        '<'
214	POP_JUMP_IF_FALSE '915'

217	LOAD_FAST         'str'
220	LOAD_FAST         'i'
223	BINARY_SUBSCR     None
224	STORE_FAST        'ch'

227	LOAD_FAST         'i'
230	LOAD_CONST        1
233	BINARY_ADD        None
234	STORE_FAST        'i'

237	LOAD_FAST         'ch'
240	LOAD_CONST        'x'
243	COMPARE_OP        '=='
246	POP_JUMP_IF_FALSE '255'

249	CONTINUE          '205'
252	JUMP_FORWARD      '255'
255_0	COME_FROM         '252'

255	LOAD_FAST         'ch'
258	LOAD_CONST        '\n'
261	COMPARE_OP        '=='
264	POP_JUMP_IF_FALSE '308'

267	LOAD_FAST         'lno'
270	LOAD_CONST        1
273	BINARY_ADD        None
274	STORE_FAST        'lno'

277	LOAD_FAST         'level'
280	LOAD_CONST        0
283	COMPARE_OP        '=='
286	POP_JUMP_IF_FALSE '205'

289	LOAD_FAST         'push_good'
292	LOAD_FAST         'lno'
295	CALL_FUNCTION_1   None
298	POP_TOP           None
299	JUMP_BACK         '205'

302	CONTINUE          '205'
305	JUMP_FORWARD      '308'
308_0	COME_FROM         '305'

308	LOAD_FAST         'ch'
311	LOAD_CONST        '('
314	COMPARE_OP        '=='
317	POP_JUMP_IF_FALSE '336'

320	LOAD_FAST         'level'
323	LOAD_CONST        1
326	BINARY_ADD        None
327	STORE_FAST        'level'

330	CONTINUE          '205'
333	JUMP_FORWARD      '336'
336_0	COME_FROM         '333'

336	LOAD_FAST         'ch'
339	LOAD_CONST        ')'
342	COMPARE_OP        '=='
345	POP_JUMP_IF_FALSE '373'

348	LOAD_FAST         'level'
351	POP_JUMP_IF_FALSE '205'

354	LOAD_FAST         'level'
357	LOAD_CONST        1
360	BINARY_SUBTRACT   None
361	STORE_FAST        'level'
364	JUMP_BACK         '205'

367	CONTINUE          '205'
370	JUMP_FORWARD      '373'
373_0	COME_FROM         '370'

373	LOAD_FAST         'ch'
376	LOAD_CONST        '"'
379	COMPARE_OP        '=='
382	POP_JUMP_IF_TRUE  '397'
385	LOAD_FAST         'ch'
388	LOAD_CONST        "'"
391	COMPARE_OP        '=='
394_0	COME_FROM         '382'
394	POP_JUMP_IF_FALSE '758'

397	LOAD_FAST         'ch'
400	STORE_FAST        'quote'

403	LOAD_FAST         'str'
406	LOAD_FAST         'i'
409	LOAD_CONST        1
412	BINARY_SUBTRACT   None
413	LOAD_FAST         'i'
416	LOAD_CONST        2
419	BINARY_ADD        None
420	SLICE+3           None
421	LOAD_FAST         'quote'
424	LOAD_CONST        3
427	BINARY_MULTIPLY   None
428	COMPARE_OP        '=='
431	POP_JUMP_IF_FALSE '447'

434	LOAD_FAST         'quote'
437	LOAD_CONST        3
440	BINARY_MULTIPLY   None
441	STORE_FAST        'quote'
444	JUMP_FORWARD      '447'
447_0	COME_FROM         '444'

447	LOAD_FAST         'lno'
450	STORE_FAST        'firstlno'

453	LOAD_GLOBAL       'len'
456	LOAD_FAST         'quote'
459	CALL_FUNCTION_1   None
462	LOAD_CONST        1
465	BINARY_SUBTRACT   None
466	STORE_FAST        'w'

469	LOAD_FAST         'i'
472	LOAD_FAST         'w'
475	BINARY_ADD        None
476	STORE_FAST        'i'

479	SETUP_LOOP        '752'
482	LOAD_FAST         'i'
485	LOAD_FAST         'n'
488	COMPARE_OP        '<'
491	POP_JUMP_IF_FALSE '720'

494	LOAD_FAST         'str'
497	LOAD_FAST         'i'
500	BINARY_SUBSCR     None
501	STORE_FAST        'ch'

504	LOAD_FAST         'i'
507	LOAD_CONST        1
510	BINARY_ADD        None
511	STORE_FAST        'i'

514	LOAD_FAST         'ch'
517	LOAD_CONST        'x'
520	COMPARE_OP        '=='
523	POP_JUMP_IF_FALSE '532'

526	CONTINUE          '482'
529	JUMP_FORWARD      '532'
532_0	COME_FROM         '529'

532	LOAD_FAST         'str'
535	LOAD_FAST         'i'
538	LOAD_CONST        1
541	BINARY_SUBTRACT   None
542	LOAD_FAST         'i'
545	LOAD_FAST         'w'
548	BINARY_ADD        None
549	SLICE+3           None
550	LOAD_FAST         'quote'
553	COMPARE_OP        '=='
556	POP_JUMP_IF_FALSE '573'

559	LOAD_FAST         'i'
562	LOAD_FAST         'w'
565	BINARY_ADD        None
566	STORE_FAST        'i'

569	BREAK_LOOP        None
570	JUMP_FORWARD      '573'
573_0	COME_FROM         '570'

573	LOAD_FAST         'ch'
576	LOAD_CONST        '\n'
579	COMPARE_OP        '=='
582	POP_JUMP_IF_FALSE '642'

585	LOAD_FAST         'lno'
588	LOAD_CONST        1
591	BINARY_ADD        None
592	STORE_FAST        'lno'

595	LOAD_FAST         'w'
598	LOAD_CONST        0
601	COMPARE_OP        '=='
604	POP_JUMP_IF_FALSE '482'

607	LOAD_FAST         'level'
610	LOAD_CONST        0
613	COMPARE_OP        '=='
616	POP_JUMP_IF_FALSE '632'

619	LOAD_FAST         'push_good'
622	LOAD_FAST         'lno'
625	CALL_FUNCTION_1   None
628	POP_TOP           None
629	JUMP_FORWARD      '632'
632_0	COME_FROM         '629'

632	BREAK_LOOP        None
633	JUMP_BACK         '482'

636	CONTINUE          '482'
639	JUMP_FORWARD      '642'
642_0	COME_FROM         '639'

642	LOAD_FAST         'ch'
645	LOAD_CONST        '\\'
648	COMPARE_OP        '=='
651	POP_JUMP_IF_FALSE '482'

654	LOAD_FAST         'i'
657	LOAD_FAST         'n'
660	COMPARE_OP        '<'
663	POP_JUMP_IF_TRUE  '672'
666	LOAD_ASSERT       'AssertionError'
669	RAISE_VARARGS_1   None

672	LOAD_FAST         'str'
675	LOAD_FAST         'i'
678	BINARY_SUBSCR     None
679	LOAD_CONST        '\n'
682	COMPARE_OP        '=='
685	POP_JUMP_IF_FALSE '701'

688	LOAD_FAST         'lno'
691	LOAD_CONST        1
694	BINARY_ADD        None
695	STORE_FAST        'lno'
698	JUMP_FORWARD      '701'
701_0	COME_FROM         '698'

701	LOAD_FAST         'i'
704	LOAD_CONST        1
707	BINARY_ADD        None
708	STORE_FAST        'i'

711	CONTINUE          '482'
714	JUMP_BACK         '482'
717	JUMP_BACK         '482'
720	POP_BLOCK         None

721	LOAD_FAST         'lno'
724	LOAD_CONST        1
727	BINARY_SUBTRACT   None
728	LOAD_FAST         'firstlno'
731	COMPARE_OP        '=='
734	POP_JUMP_IF_FALSE '746'

737	LOAD_GLOBAL       'C_STRING_FIRST_LINE'
740	STORE_FAST        'continuation'
743	JUMP_BACK         '205'

746	LOAD_GLOBAL       'C_STRING_NEXT_LINES'
749	STORE_FAST        'continuation'
752_0	COME_FROM         '479'

752	CONTINUE          '205'
755	JUMP_FORWARD      '758'
758_0	COME_FROM         '755'

758	LOAD_FAST         'ch'
761	LOAD_CONST        '#'
764	COMPARE_OP        '=='
767	POP_JUMP_IF_FALSE '812'

770	LOAD_FAST         'str'
773	LOAD_ATTR         'find'
776	LOAD_CONST        '\n'
779	LOAD_FAST         'i'
782	CALL_FUNCTION_2   None
785	STORE_FAST        'i'

788	LOAD_FAST         'i'
791	LOAD_CONST        0
794	COMPARE_OP        '>='
797	POP_JUMP_IF_TRUE  '205'
800	LOAD_GLOBAL       'AssertionError'
803	RAISE_VARARGS_1   None

806	CONTINUE          '205'
809	JUMP_FORWARD      '812'
812_0	COME_FROM         '809'

812	LOAD_FAST         'ch'
815	LOAD_CONST        '\\'
818	COMPARE_OP        '=='
821	POP_JUMP_IF_TRUE  '830'
824	LOAD_ASSERT       'AssertionError'
827	RAISE_VARARGS_1   None

830	LOAD_FAST         'i'
833	LOAD_FAST         'n'
836	COMPARE_OP        '<'
839	POP_JUMP_IF_TRUE  '848'
842	LOAD_ASSERT       'AssertionError'
845	RAISE_VARARGS_1   None

848	LOAD_FAST         'str'
851	LOAD_FAST         'i'
854	BINARY_SUBSCR     None
855	LOAD_CONST        '\n'
858	COMPARE_OP        '=='
861	POP_JUMP_IF_FALSE '902'

864	LOAD_FAST         'lno'
867	LOAD_CONST        1
870	BINARY_ADD        None
871	STORE_FAST        'lno'

874	LOAD_FAST         'i'
877	LOAD_CONST        1
880	BINARY_ADD        None
881	LOAD_FAST         'n'
884	COMPARE_OP        '=='
887	POP_JUMP_IF_FALSE '902'

890	LOAD_GLOBAL       'C_BACKSLASH'
893	STORE_FAST        'continuation'
896	JUMP_ABSOLUTE     '902'
899	JUMP_FORWARD      '902'
902_0	COME_FROM         '899'

902	LOAD_FAST         'i'
905	LOAD_CONST        1
908	BINARY_ADD        None
909	STORE_FAST        'i'
912	JUMP_BACK         '205'
915	POP_BLOCK         None
916_0	COME_FROM         '202'

916	LOAD_FAST         'continuation'
919	LOAD_GLOBAL       'C_STRING_FIRST_LINE'
922	COMPARE_OP        '!='
925	POP_JUMP_IF_FALSE '961'

928	LOAD_FAST         'continuation'
931	LOAD_GLOBAL       'C_STRING_NEXT_LINES'
934	COMPARE_OP        '!='
937	POP_JUMP_IF_FALSE '961'
940	LOAD_FAST         'level'
943	LOAD_CONST        0
946	COMPARE_OP        '>'
949_0	COME_FROM         '925'
949_1	COME_FROM         '937'
949	POP_JUMP_IF_FALSE '961'

952	LOAD_GLOBAL       'C_BRACKET'
955	STORE_FAST        'continuation'
958	JUMP_FORWARD      '961'
961_0	COME_FROM         '958'

961	LOAD_FAST         'continuation'
964	LOAD_FAST         'self'
967	STORE_ATTR        'continuation'

970	LOAD_FAST         'continuation'
973	LOAD_GLOBAL       'C_NONE'
976	COMPARE_OP        '=='
979	LOAD_FAST         'goodlines'
982	LOAD_CONST        -1
985	BINARY_SUBSCR     None
986	LOAD_FAST         'lno'
989	COMPARE_OP        '=='
992	COMPARE_OP        '=='
995	POP_JUMP_IF_TRUE  '1004'
998	LOAD_ASSERT       'AssertionError'
1001	RAISE_VARARGS_1   None

1004	LOAD_FAST         'goodlines'
1007	LOAD_CONST        -1
1010	BINARY_SUBSCR     None
1011	LOAD_FAST         'lno'
1014	COMPARE_OP        '!='
1017	POP_JUMP_IF_FALSE '1033'

1020	LOAD_FAST         'push_good'
1023	LOAD_FAST         'lno'
1026	CALL_FUNCTION_1   None
1029	POP_TOP           None
1030	JUMP_FORWARD      '1033'
1033_0	COME_FROM         '1030'

Syntax error at or near `COME_FROM' token at offset 752_0

    def get_continuation_type(self):
        self._study1()
        return self.continuation

    def _study2(self):
        if self.study_level >= 2:
            return
        self._study1()
        self.study_level = 2
        str, goodlines = self.str, self.goodlines
        i = len(goodlines) - 1
        p = len(str)
        while not (i and p):
            raise AssertionError
            q = p
            for nothing in range(goodlines[i - 1], goodlines[i]):
                p = str.rfind('\n', 0, p - 1) + 1

            if _junkre(str, p):
                i = i - 1
            else:
                break

        if i == 0:
            if not p == 0:
                raise AssertionError
                q = p
            self.stmt_start, self.stmt_end = p, q
            lastch = ''
            stack = []
            push_stack = stack.append
            bracketing = [(p, 0)]
            while p < q:
                m = _chew_ordinaryre(str, p, q)
                if m:
                    newp = m.end()
                    i = newp - 1
                    while i >= p and str[i] in ' \t\n':
                        i = i - 1

                    if i >= p:
                        lastch = str[i]
                    p = newp
                    if p >= q:
                        break
                ch = str[p]
                if ch in '([{':
                    push_stack(p)
                    bracketing.append((p, len(stack)))
                    lastch = ch
                    p = p + 1
                    continue
                if ch in ')]}':
                    if stack:
                        del stack[-1]
                    lastch = ch
                    p = p + 1
                    bracketing.append((p, len(stack)))
                    continue
                if ch == '"' or ch == "'":
                    bracketing.append((p, len(stack) + 1))
                    lastch = ch
                    p = _match_stringre(str, p, q).end()
                    bracketing.append((p, len(stack)))
                    continue
                ch == '#' and bracketing.append((p, len(stack) + 1))
                p = str.find('\n', p, q) + 1
                if not p > 0:
                    raise AssertionError
                    bracketing.append((p, len(stack)))
                    continue
                raise ch == '\\' or AssertionError
                p = p + 1
                if not p < q:
                    raise AssertionError
                    lastch = str[p] != '\n' and ch + str[p]
                p = p + 1

            self.lastch = lastch
            self.lastopenbracketpos = stack and stack[-1]
        self.stmt_bracketing = tuple(bracketing)

    def compute_bracket_indent(self):
        self._study2()
        raise self.continuation == C_BRACKET or AssertionError
        j = self.lastopenbracketpos
        str = self.str
        n = len(str)
        origi = i = str.rfind('\n', 0, j) + 1
        j = j + 1
        while j < n:
            m = _itemre(str, j)
            if m:
                j = m.end() - 1
                extra = 0
                break
            else:
                i = j = str.find('\n', j) + 1
        else:
            j = i = origi
            while str[j] in ' \t':
                j = j + 1

            extra = self.indentwidth

        return len(str[i:j].expandtabs(self.tabwidth)) + extra

    def get_num_lines_in_stmt(self):
        self._study1()
        goodlines = self.goodlines
        return goodlines[-1] - goodlines[-2]

    def compute_backslash_indent(self):
        self._study2()
        if not self.continuation == C_BACKSLASH:
            raise AssertionError
            str = self.str
            i = self.stmt_start
            while str[i] in ' \t':
                i = i + 1

            startpos = i
            endpos = str.find('\n', startpos) + 1
            found = level = 0
            while i < endpos:
                ch = str[i]
                if ch in '([{':
                    level = level + 1
                    i = i + 1
                elif ch in ')]}':
                    if level:
                        level = level - 1
                    i = i + 1
                elif ch == '"' or ch == "'":
                    i = _match_stringre(str, i, endpos).end()
                elif ch == '#':
                    break
                elif level == 0 and ch == '=' and (i == 0 or str[i - 1] not in '=<>!') and str[i + 1] != '=':
                    found = 1
                    break
                else:
                    i = i + 1

            if found:
                i = i + 1
                found = re.match('\\s*\\\\', str[i:endpos]) is None
            i = found or startpos
            while str[i] not in ' \t\n':
                i = i + 1

        return len(str[self.stmt_start:i].expandtabs(self.tabwidth)) + 1

    def get_base_indent_string(self):
        self._study2()
        i, n = self.stmt_start, self.stmt_end
        j = i
        str = self.str
        while j < n and str[j] in ' \t':
            j = j + 1

        return str[i:j]

    def is_block_opener(self):
        self._study2()
        return self.lastch == ':'

    def is_block_closer(self):
        self._study2()
        return _closere(self.str, self.stmt_start) is not None

    lastopenbracketpos = None

    def get_last_open_bracket_pos(self):
        self._study2()
        return self.lastopenbracketpos

    stmt_bracketing = None

    def get_last_stmt_bracketing(self):
        self._study2()
        return self.stmt_bracketing