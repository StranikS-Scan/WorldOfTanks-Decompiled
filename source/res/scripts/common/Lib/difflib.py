# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/difflib.py
__all__ = ['get_close_matches',
 'ndiff',
 'restore',
 'SequenceMatcher',
 'Differ',
 'IS_CHARACTER_JUNK',
 'IS_LINE_JUNK',
 'context_diff',
 'unified_diff',
 'HtmlDiff',
 'Match']
import heapq
from collections import namedtuple as _namedtuple
from functools import reduce
Match = _namedtuple('Match', 'a b size')

def _calculate_ratio(matches, length):
    return 2.0 * matches / length if length else 1.0


class SequenceMatcher():

    def __init__(self, isjunk=None, a='', b='', autojunk=True):
        self.isjunk = isjunk
        self.a = self.b = None
        self.autojunk = autojunk
        self.set_seqs(a, b)
        return

    def set_seqs(self, a, b):
        self.set_seq1(a)
        self.set_seq2(b)

    def set_seq1(self, a):
        if a is self.a:
            return
        else:
            self.a = a
            self.matching_blocks = self.opcodes = None
            return

    def set_seq2(self, b):
        if b is self.b:
            return
        else:
            self.b = b
            self.matching_blocks = self.opcodes = None
            self.fullbcount = None
            self.__chain_b()
            return

    def __chain_b(self):
        b = self.b
        self.b2j = b2j = {}
        for i, elt in enumerate(b):
            indices = b2j.setdefault(elt, [])
            indices.append(i)

        junk = set()
        isjunk = self.isjunk
        if isjunk:
            for elt in list(b2j.keys()):
                if isjunk(elt):
                    junk.add(elt)
                    del b2j[elt]

        popular = set()
        n = len(b)
        if self.autojunk and n >= 200:
            ntest = n // 100 + 1
            for elt, idxs in list(b2j.items()):
                if len(idxs) > ntest:
                    popular.add(elt)
                    del b2j[elt]

        self.isbjunk = junk.__contains__
        self.isbpopular = popular.__contains__

    def find_longest_match(self, alo, ahi, blo, bhi):
        a, b, b2j, isbjunk = (self.a,
         self.b,
         self.b2j,
         self.isbjunk)
        besti, bestj, bestsize = alo, blo, 0
        j2len = {}
        nothing = []
        for i in xrange(alo, ahi):
            j2lenget = j2len.get
            newj2len = {}
            for j in b2j.get(a[i], nothing):
                if j < blo:
                    continue
                if j >= bhi:
                    break
                k = newj2len[j] = j2lenget(j - 1, 0) + 1
                if k > bestsize:
                    besti, bestj, bestsize = i - k + 1, j - k + 1, k

            j2len = newj2len

        while 1:
            besti, bestj, bestsize = besti > alo and bestj > blo and not isbjunk(b[bestj - 1]) and a[besti - 1] == b[bestj - 1] and besti - 1, bestj - 1, bestsize + 1

        while 1:
            besti + bestsize < ahi and bestj + bestsize < bhi and not isbjunk(b[bestj + bestsize]) and a[besti + bestsize] == b[bestj + bestsize] and bestsize += 1

        while 1:
            besti, bestj, bestsize = besti > alo and bestj > blo and isbjunk(b[bestj - 1]) and a[besti - 1] == b[bestj - 1] and besti - 1, bestj - 1, bestsize + 1

        while 1:
            bestsize = besti + bestsize < ahi and bestj + bestsize < bhi and isbjunk(b[bestj + bestsize]) and a[besti + bestsize] == b[bestj + bestsize] and bestsize + 1

        return Match(besti, bestj, bestsize)

    def get_matching_blocks(self):
        if self.matching_blocks is not None:
            return self.matching_blocks
        else:
            la, lb = len(self.a), len(self.b)
            queue = [(0,
              la,
              0,
              lb)]
            matching_blocks = []
            while queue:
                alo, ahi, blo, bhi = queue.pop()
                i, j, k = x = self.find_longest_match(alo, ahi, blo, bhi)
                if k:
                    matching_blocks.append(x)
                    if alo < i and blo < j:
                        queue.append((alo,
                         i,
                         blo,
                         j))
                    if i + k < ahi and j + k < bhi:
                        queue.append((i + k,
                         ahi,
                         j + k,
                         bhi))

            matching_blocks.sort()
            i1 = j1 = k1 = 0
            non_adjacent = []
            for i2, j2, k2 in matching_blocks:
                if i1 + k1 == i2 and j1 + k1 == j2:
                    k1 += k2
                if k1:
                    non_adjacent.append((i1, j1, k1))
                i1, j1, k1 = i2, j2, k2

            if k1:
                non_adjacent.append((i1, j1, k1))
            non_adjacent.append((la, lb, 0))
            self.matching_blocks = map(Match._make, non_adjacent)
            return self.matching_blocks

    def get_opcodes(self):
        if self.opcodes is not None:
            return self.opcodes
        else:
            i = j = 0
            self.opcodes = answer = []
            for ai, bj, size in self.get_matching_blocks():
                tag = ''
                if i < ai and j < bj:
                    tag = 'replace'
                elif i < ai:
                    tag = 'delete'
                elif j < bj:
                    tag = 'insert'
                if tag:
                    answer.append((tag,
                     i,
                     ai,
                     j,
                     bj))
                i, j = ai + size, bj + size
                if size:
                    answer.append(('equal',
                     ai,
                     i,
                     bj,
                     j))

            return answer

    def get_grouped_opcodes(self, n=3):
        codes = self.get_opcodes()
        if not codes:
            codes = [('equal', 0, 1, 0, 1)]
        if codes[0][0] == 'equal':
            tag, i1, i2, j1, j2 = codes[0]
            codes[0] = (tag,
             max(i1, i2 - n),
             i2,
             max(j1, j2 - n),
             j2)
        if codes[-1][0] == 'equal':
            tag, i1, i2, j1, j2 = codes[-1]
            codes[-1] = (tag,
             i1,
             min(i2, i1 + n),
             j1,
             min(j2, j1 + n))
        nn = n + n
        group = []
        for tag, i1, i2, j1, j2 in codes:
            if tag == 'equal' and i2 - i1 > nn:
                group.append((tag,
                 i1,
                 min(i2, i1 + n),
                 j1,
                 min(j2, j1 + n)))
                yield group
                group = []
                i1, j1 = max(i1, i2 - n), max(j1, j2 - n)
            group.append((tag,
             i1,
             i2,
             j1,
             j2))

        if group and not (len(group) == 1 and group[0][0] == 'equal'):
            yield group

    def ratio(self):
        matches = reduce(lambda sum, triple: sum + triple[-1], self.get_matching_blocks(), 0)
        return _calculate_ratio(matches, len(self.a) + len(self.b))

    def quick_ratio(self):
        if self.fullbcount is None:
            self.fullbcount = fullbcount = {}
            for elt in self.b:
                fullbcount[elt] = fullbcount.get(elt, 0) + 1

        fullbcount = self.fullbcount
        avail = {}
        availhas, matches = avail.__contains__, 0
        for elt in self.a:
            if availhas(elt):
                numb = avail[elt]
            else:
                numb = fullbcount.get(elt, 0)
            avail[elt] = numb - 1
            if numb > 0:
                matches = matches + 1

        return _calculate_ratio(matches, len(self.a) + len(self.b))

    def real_quick_ratio(self):
        la, lb = len(self.a), len(self.b)
        return _calculate_ratio(min(la, lb), la + lb)


def get_close_matches(word, possibilities, n=3, cutoff=0.6):
    if not n > 0:
        raise ValueError('n must be > 0: %r' % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError('cutoff must be in [0.0, 1.0]: %r' % (cutoff,))
    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    for x in possibilities:
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and s.quick_ratio() >= cutoff and s.ratio() >= cutoff:
            result.append((s.ratio(), x))

    result = heapq.nlargest(n, result)
    return [ x for score, x in result ]


def _count_leading(line, ch):
    i, n = 0, len(line)
    while i < n and line[i] == ch:
        i += 1

    return i


class Differ():

    def __init__(self, linejunk=None, charjunk=None):
        self.linejunk = linejunk
        self.charjunk = charjunk

    def compare(self, a, b):
        cruncher = SequenceMatcher(self.linejunk, a, b)
        for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
            if tag == 'replace':
                g = self._fancy_replace(a, alo, ahi, b, blo, bhi)
            elif tag == 'delete':
                g = self._dump('-', a, alo, ahi)
            elif tag == 'insert':
                g = self._dump('+', b, blo, bhi)
            elif tag == 'equal':
                g = self._dump(' ', a, alo, ahi)
            else:
                raise ValueError, 'unknown tag %r' % (tag,)
            for line in g:
                yield line

    def _dump(self, tag, x, lo, hi):
        for i in xrange(lo, hi):
            yield '%s %s' % (tag, x[i])

    def _plain_replace(self, a, alo, ahi, b, blo, bhi):
        if bhi - blo < ahi - alo:
            first = self._dump('+', b, blo, bhi)
            second = self._dump('-', a, alo, ahi)
        else:
            first = self._dump('-', a, alo, ahi)
            second = self._dump('+', b, blo, bhi)
        for g in (first, second):
            for line in g:
                yield line

    def _fancy_replace(self, a, alo, ahi, b, blo, bhi):
        best_ratio, cutoff = (0.74, 0.75)
        cruncher = SequenceMatcher(self.charjunk)
        eqi, eqj = (None, None)
        for j in xrange(blo, bhi):
            bj = b[j]
            cruncher.set_seq2(bj)
            for i in xrange(alo, ahi):
                ai = a[i]
                if ai == bj:
                    if eqi is None:
                        eqi, eqj = i, j
                    continue
                cruncher.set_seq1(ai)
                if cruncher.real_quick_ratio() > best_ratio and cruncher.quick_ratio() > best_ratio and cruncher.ratio() > best_ratio:
                    best_ratio, best_i, best_j = cruncher.ratio(), i, j

        if best_ratio < cutoff:
            if eqi is None:
                for line in self._plain_replace(a, alo, ahi, b, blo, bhi):
                    yield line

                return
            best_i, best_j, best_ratio = eqi, eqj, 1.0
        else:
            eqi = None
        for line in self._fancy_helper(a, alo, best_i, b, blo, best_j):
            yield line

        aelt, belt = a[best_i], b[best_j]
        if eqi is None:
            atags = btags = ''
            cruncher.set_seqs(aelt, belt)
            for tag, ai1, ai2, bj1, bj2 in cruncher.get_opcodes():
                la, lb = ai2 - ai1, bj2 - bj1
                if tag == 'replace':
                    atags += '^' * la
                    btags += '^' * lb
                if tag == 'delete':
                    atags += '-' * la
                if tag == 'insert':
                    btags += '+' * lb
                if tag == 'equal':
                    atags += ' ' * la
                    btags += ' ' * lb
                raise ValueError, 'unknown tag %r' % (tag,)

            for line in self._qformat(aelt, belt, atags, btags):
                yield line

        else:
            yield '  ' + aelt
        for line in self._fancy_helper(a, best_i + 1, ahi, b, best_j + 1, bhi):
            yield line

        return

    def _fancy_helper(self, a, alo, ahi, b, blo, bhi):
        g = []
        if alo < ahi:
            if blo < bhi:
                g = self._fancy_replace(a, alo, ahi, b, blo, bhi)
            else:
                g = self._dump('-', a, alo, ahi)
        elif blo < bhi:
            g = self._dump('+', b, blo, bhi)
        for line in g:
            yield line

    def _qformat(self, aline, bline, atags, btags):
        common = min(_count_leading(aline, '\t'), _count_leading(bline, '\t'))
        common = min(common, _count_leading(atags[:common], ' '))
        common = min(common, _count_leading(btags[:common], ' '))
        atags = atags[common:].rstrip()
        btags = btags[common:].rstrip()
        yield '- ' + aline
        if atags:
            yield '? %s%s\n' % ('\t' * common, atags)
        yield '+ ' + bline
        if btags:
            yield '? %s%s\n' % ('\t' * common, btags)


import re

def IS_LINE_JUNK(line, pat=re.compile('\\s*(?:#\\s*)?$').match):
    return pat(line) is not None


def IS_CHARACTER_JUNK(ch, ws=' \t'):
    return ch in ws


def _format_range_unified(start, stop):
    beginning = start + 1
    length = stop - start
    if length == 1:
        return '{}'.format(beginning)
    if not length:
        beginning -= 1
    return '{},{}'.format(beginning, length)


def unified_diff(a, b, fromfile='', tofile='', fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    started = False
    for group in SequenceMatcher(None, a, b).get_grouped_opcodes(n):
        if not started:
            started = True
            fromdate = '\t{}'.format(fromfiledate) if fromfiledate else ''
            todate = '\t{}'.format(tofiledate) if tofiledate else ''
            yield '--- {}{}{}'.format(fromfile, fromdate, lineterm)
            yield '+++ {}{}{}'.format(tofile, todate, lineterm)
        first, last = group[0], group[-1]
        file1_range = _format_range_unified(first[1], last[2])
        file2_range = _format_range_unified(first[3], last[4])
        yield '@@ -{} +{} @@{}'.format(file1_range, file2_range, lineterm)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in a[i1:i2]:
                    yield ' ' + line

                continue
            if tag in ('replace', 'delete'):
                for line in a[i1:i2]:
                    yield '-' + line

            if tag in ('replace', 'insert'):
                for line in b[j1:j2]:
                    yield '+' + line

    return


def _format_range_context(start, stop):
    beginning = start + 1
    length = stop - start
    if not length:
        beginning -= 1
    return '{}'.format(beginning) if length <= 1 else '{},{}'.format(beginning, beginning + length - 1)


def context_diff(a, b, fromfile='', tofile='', fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    prefix = dict(insert='+ ', delete='- ', replace='! ', equal='  ')
    started = False
    for group in SequenceMatcher(None, a, b).get_grouped_opcodes(n):
        if not started:
            started = True
            fromdate = '\t{}'.format(fromfiledate) if fromfiledate else ''
            todate = '\t{}'.format(tofiledate) if tofiledate else ''
            yield '*** {}{}{}'.format(fromfile, fromdate, lineterm)
            yield '--- {}{}{}'.format(tofile, todate, lineterm)
        first, last = group[0], group[-1]
        yield '***************' + lineterm
        file1_range = _format_range_context(first[1], last[2])
        yield '*** {} ****{}'.format(file1_range, lineterm)
        if any((tag in ('replace', 'delete') for tag, _, _, _, _ in group)):
            for tag, i1, i2, _, _ in group:
                if tag != 'insert':
                    for line in a[i1:i2]:
                        yield prefix[tag] + line

        file2_range = _format_range_context(first[3], last[4])
        yield '--- {} ----{}'.format(file2_range, lineterm)
        if any((tag in ('replace', 'insert') for tag, _, _, _, _ in group)):
            for tag, _, _, j1, j2 in group:
                if tag != 'delete':
                    for line in b[j1:j2]:
                        yield prefix[tag] + line

    return


def ndiff(a, b, linejunk=None, charjunk=IS_CHARACTER_JUNK):
    return Differ(linejunk, charjunk).compare(a, b)


def _mdiff(fromlines, tolines, context=None, linejunk=None, charjunk=IS_CHARACTER_JUNK):
    import re
    change_re = re.compile('(\\++|\\-+|\\^+)')
    diff_lines_iterator = ndiff(fromlines, tolines, linejunk, charjunk)

    def _make_line(lines, format_key, side, num_lines=[0, 0]):
        num_lines[side] += 1
        if format_key is None:
            return (num_lines[side], lines.pop(0)[2:])
        else:
            if format_key == '?':
                text, markers = lines.pop(0), lines.pop(0)
                sub_info = []

                def record_sub_info(match_object, sub_info=sub_info):
                    sub_info.append([match_object.group(1)[0], match_object.span()])
                    return match_object.group(1)

                change_re.sub(record_sub_info, markers)
                for key, (begin, end) in sub_info[::-1]:
                    text = text[0:begin] + '\x00' + key + text[begin:end] + '\x01' + text[end:]

                text = text[2:]
            else:
                text = lines.pop(0)[2:]
                if not text:
                    text = ' '
                text = '\x00' + format_key + text + '\x01'
            return (num_lines[side], text)

    def _line_iterator():
        lines = []
        num_blanks_pending, num_blanks_to_yield = (0, 0)
        while True:
            while len(lines) < 4:
                try:
                    lines.append(diff_lines_iterator.next())
                except StopIteration:
                    lines.append('X')

            s = ''.join([ line[0] for line in lines ])
            if s.startswith('X'):
                num_blanks_to_yield = num_blanks_pending
            elif s.startswith('-?+?'):
                yield (_make_line(lines, '?', 0), _make_line(lines, '?', 1), True)
                continue
            elif s.startswith('--++'):
                num_blanks_pending -= 1
                yield (_make_line(lines, '-', 0), None, True)
                continue
            elif s.startswith(('--?+', '--+', '- ')):
                from_line, to_line = _make_line(lines, '-', 0), None
                num_blanks_to_yield, num_blanks_pending = num_blanks_pending - 1, 0
            elif s.startswith('-+?'):
                yield (_make_line(lines, None, 0), _make_line(lines, '?', 1), True)
                continue
            elif s.startswith('-?+'):
                yield (_make_line(lines, '?', 0), _make_line(lines, None, 1), True)
                continue
            elif s.startswith('-'):
                num_blanks_pending -= 1
                yield (_make_line(lines, '-', 0), None, True)
                continue
            elif s.startswith('+--'):
                num_blanks_pending += 1
                yield (None, _make_line(lines, '+', 1), True)
                continue
            elif s.startswith(('+ ', '+-')):
                from_line, to_line = None, _make_line(lines, '+', 1)
                num_blanks_to_yield, num_blanks_pending = num_blanks_pending + 1, 0
            elif s.startswith('+'):
                num_blanks_pending += 1
                yield (None, _make_line(lines, '+', 1), True)
                continue
            elif s.startswith(' '):
                yield (_make_line(lines[:], None, 0), _make_line(lines, None, 1), False)
                continue
            while num_blanks_to_yield < 0:
                num_blanks_to_yield += 1
                yield (None, ('', '\n'), True)

            while num_blanks_to_yield > 0:
                num_blanks_to_yield -= 1
                yield (('', '\n'), None, True)

            if s.startswith('X'):
                raise StopIteration
            yield (from_line, to_line, True)

        return

    def _line_pair_iterator():
        line_iterator = _line_iterator()
        fromlines, tolines = [], []
        while True:
            while len(fromlines) == 0 or len(tolines) == 0:
                from_line, to_line, found_diff = line_iterator.next()
                if from_line is not None:
                    fromlines.append((from_line, found_diff))
                if to_line is not None:
                    tolines.append((to_line, found_diff))

            from_line, fromDiff = fromlines.pop(0)
            to_line, to_diff = tolines.pop(0)
            yield (from_line, to_line, fromDiff or to_diff)

        return

    line_pair_iterator = _line_pair_iterator()
    if context is None:
        while True:
            yield line_pair_iterator.next()

    else:
        context += 1
        lines_to_write = 0
        while True:
            index, contextLines = 0, [None] * context
            found_diff = False
            while found_diff is False:
                from_line, to_line, found_diff = line_pair_iterator.next()
                i = index % context
                contextLines[i] = (from_line, to_line, found_diff)
                index += 1

            if index > context:
                yield (None, None, None)
                lines_to_write = context
            else:
                lines_to_write = index
                index = 0
            while lines_to_write:
                i = index % context
                index += 1
                yield contextLines[i]
                lines_to_write -= 1

            lines_to_write = context - 1
            while lines_to_write:
                from_line, to_line, found_diff = line_pair_iterator.next()
                if found_diff:
                    lines_to_write = context - 1
                else:
                    lines_to_write -= 1
                yield (from_line, to_line, found_diff)

    return


_file_template = '\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n\n<html>\n\n<head>\n    <meta http-equiv="Content-Type"\n          content="text/html; charset=ISO-8859-1" />\n    <title></title>\n    <style type="text/css">%(styles)s\n    </style>\n</head>\n\n<body>\n    %(table)s%(legend)s\n</body>\n\n</html>'
_styles = '\n        table.diff {font-family:Courier; border:medium;}\n        .diff_header {background-color:#e0e0e0}\n        td.diff_header {text-align:right}\n        .diff_next {background-color:#c0c0c0}\n        .diff_add {background-color:#aaffaa}\n        .diff_chg {background-color:#ffff77}\n        .diff_sub {background-color:#ffaaaa}'
_table_template = '\n    <table class="diff" id="difflib_chg_%(prefix)s_top"\n           cellspacing="0" cellpadding="0" rules="groups" >\n        <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>\n        <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>\n        %(header_row)s\n        <tbody>\n%(data_rows)s        </tbody>\n    </table>'
_legend = '\n    <table class="diff" summary="Legends">\n        <tr> <th colspan="2"> Legends </th> </tr>\n        <tr> <td> <table border="" summary="Colors">\n                      <tr><th> Colors </th> </tr>\n                      <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr>\n                      <tr><td class="diff_chg">Changed</td> </tr>\n                      <tr><td class="diff_sub">Deleted</td> </tr>\n                  </table></td>\n             <td> <table border="" summary="Links">\n                      <tr><th colspan="2"> Links </th> </tr>\n                      <tr><td>(f)irst change</td> </tr>\n                      <tr><td>(n)ext change</td> </tr>\n                      <tr><td>(t)op</td> </tr>\n                  </table></td> </tr>\n    </table>'

class HtmlDiff(object):
    _file_template = _file_template
    _styles = _styles
    _table_template = _table_template
    _legend = _legend
    _default_prefix = 0

    def __init__(self, tabsize=8, wrapcolumn=None, linejunk=None, charjunk=IS_CHARACTER_JUNK):
        self._tabsize = tabsize
        self._wrapcolumn = wrapcolumn
        self._linejunk = linejunk
        self._charjunk = charjunk

    def make_file(self, fromlines, tolines, fromdesc='', todesc='', context=False, numlines=5):
        return self._file_template % dict(styles=self._styles, legend=self._legend, table=self.make_table(fromlines, tolines, fromdesc, todesc, context=context, numlines=numlines))

    def _tab_newline_replace(self, fromlines, tolines):

        def expand_tabs(line):
            line = line.replace(' ', '\x00')
            line = line.expandtabs(self._tabsize)
            line = line.replace(' ', '\t')
            return line.replace('\x00', ' ').rstrip('\n')

        fromlines = [ expand_tabs(line) for line in fromlines ]
        tolines = [ expand_tabs(line) for line in tolines ]
        return (fromlines, tolines)

    def _split_line(self, data_list, line_num, text):
        if not line_num:
            data_list.append((line_num, text))
            return
        size = len(text)
        max = self._wrapcolumn
        if size <= max or size - text.count('\x00') * 3 <= max:
            data_list.append((line_num, text))
            return
        i = 0
        n = 0
        mark = ''
        while n < max and i < size:
            if text[i] == '\x00':
                i += 1
                mark = text[i]
                i += 1
            if text[i] == '\x01':
                i += 1
                mark = ''
            i += 1
            n += 1

        line1 = text[:i]
        line2 = text[i:]
        if mark:
            line1 = line1 + '\x01'
            line2 = '\x00' + mark + line2
        data_list.append((line_num, line1))
        self._split_line(data_list, '>', line2)

    def _line_wrapper(self, diffs):
        for fromdata, todata, flag in diffs:
            if flag is None:
                yield (fromdata, todata, flag)
                continue
            (fromline, fromtext), (toline, totext) = fromdata, todata
            fromlist, tolist = [], []
            self._split_line(fromlist, fromline, fromtext)
            self._split_line(tolist, toline, totext)
            while fromlist or tolist:
                if fromlist:
                    fromdata = fromlist.pop(0)
                else:
                    fromdata = ('', ' ')
                if tolist:
                    todata = tolist.pop(0)
                else:
                    todata = ('', ' ')
                yield (fromdata, todata, flag)

        return

    def _collect_lines(self, diffs):
        fromlist, tolist, flaglist = [], [], []
        for fromdata, todata, flag in diffs:
            try:
                fromlist.append(self._format_line(0, flag, *fromdata))
                tolist.append(self._format_line(1, flag, *todata))
            except TypeError:
                fromlist.append(None)
                tolist.append(None)

            flaglist.append(flag)

        return (fromlist, tolist, flaglist)

    def _format_line(self, side, flag, linenum, text):
        try:
            linenum = '%d' % linenum
            id = ' id="%s%s"' % (self._prefix[side], linenum)
        except TypeError:
            id = ''

        text = text.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;')
        text = text.replace(' ', '&nbsp;').rstrip()
        return '<td class="diff_header"%s>%s</td><td nowrap="nowrap">%s</td>' % (id, linenum, text)

    def _make_prefix(self):
        fromprefix = 'from%d_' % HtmlDiff._default_prefix
        toprefix = 'to%d_' % HtmlDiff._default_prefix
        HtmlDiff._default_prefix += 1
        self._prefix = [fromprefix, toprefix]

    def _convert_flags(self, fromlist, tolist, flaglist, context, numlines):
        toprefix = self._prefix[1]
        next_id = [''] * len(flaglist)
        next_href = [''] * len(flaglist)
        num_chg, in_change = 0, False
        last = 0
        for i, flag in enumerate(flaglist):
            if flag:
                if not in_change:
                    in_change = True
                    last = i
                    i = max([0, i - numlines])
                    next_id[i] = ' id="difflib_chg_%s_%d"' % (toprefix, num_chg)
                    num_chg += 1
                    next_href[last] = '<a href="#difflib_chg_%s_%d">n</a>' % (toprefix, num_chg)
            in_change = False

        if not flaglist:
            flaglist = [False]
            next_id = ['']
            next_href = ['']
            last = 0
            if context:
                fromlist = ['<td></td><td>&nbsp;No Differences Found&nbsp;</td>']
                tolist = fromlist
            else:
                fromlist = tolist = ['<td></td><td>&nbsp;Empty File&nbsp;</td>']
        if not flaglist[0]:
            next_href[0] = '<a href="#difflib_chg_%s_0">f</a>' % toprefix
        next_href[last] = '<a href="#difflib_chg_%s_top">t</a>' % toprefix
        return (fromlist,
         tolist,
         flaglist,
         next_href,
         next_id)

    def make_table(self, fromlines, tolines, fromdesc='', todesc='', context=False, numlines=5):
        self._make_prefix()
        fromlines, tolines = self._tab_newline_replace(fromlines, tolines)
        if context:
            context_lines = numlines
        else:
            context_lines = None
        diffs = _mdiff(fromlines, tolines, context_lines, linejunk=self._linejunk, charjunk=self._charjunk)
        if self._wrapcolumn:
            diffs = self._line_wrapper(diffs)
        fromlist, tolist, flaglist = self._collect_lines(diffs)
        fromlist, tolist, flaglist, next_href, next_id = self._convert_flags(fromlist, tolist, flaglist, context, numlines)
        s = []
        fmt = '            <tr><td class="diff_next"%s>%s</td>%s' + '<td class="diff_next">%s</td>%s</tr>\n'
        for i in range(len(flaglist)):
            if flaglist[i] is None:
                if i > 0:
                    s.append('        </tbody>        \n        <tbody>\n')
            s.append(fmt % (next_id[i],
             next_href[i],
             fromlist[i],
             next_href[i],
             tolist[i]))

        if fromdesc or todesc:
            header_row = '<thead><tr>%s%s%s%s</tr></thead>' % ('<th class="diff_next"><br /></th>',
             '<th colspan="2" class="diff_header">%s</th>' % fromdesc,
             '<th class="diff_next"><br /></th>',
             '<th colspan="2" class="diff_header">%s</th>' % todesc)
        else:
            header_row = ''
        table = self._table_template % dict(data_rows=''.join(s), header_row=header_row, prefix=self._prefix[1])
        return table.replace('\x00+', '<span class="diff_add">').replace('\x00-', '<span class="diff_sub">').replace('\x00^', '<span class="diff_chg">').replace('\x01', '</span>').replace('\t', '&nbsp;')


del re

def restore(delta, which):
    try:
        tag = {1: '- ',
         2: '+ '}[int(which)]
    except KeyError:
        raise ValueError, 'unknown delta choice (must be 1 or 2): %r' % which

    prefixes = ('  ', tag)
    for line in delta:
        if line[:2] in prefixes:
            yield line[2:]


def _test():
    import doctest, difflib
    return doctest.testmod(difflib)


if __name__ == '__main__':
    _test()
