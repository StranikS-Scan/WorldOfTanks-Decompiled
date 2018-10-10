# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/HyperParser.py
import string
import keyword
from idlelib import PyParse

class HyperParser:

    def __init__(self, editwin, index):
        self.editwin = editwin
        self.text = text = editwin.text
        parser = PyParse.Parser(editwin.indentwidth, editwin.tabwidth)

        def index2line(index):
            return int(float(index))

        lno = index2line(text.index(index))
        if not editwin.context_use_ps1:
            for context in editwin.num_context_lines:
                startat = max(lno - context, 1)
                startatindex = repr(startat) + '.0'
                stopatindex = '%d.end' % lno
                parser.set_str(text.get(startatindex, stopatindex) + ' \n')
                bod = parser.find_good_parse_start(editwin._build_char_in_string_func(startatindex))
                if bod is not None or startat == 1:
                    break

            parser.set_lo(bod or 0)
        else:
            r = text.tag_prevrange('console', index)
            if r:
                startatindex = r[1]
            else:
                startatindex = '1.0'
            stopatindex = '%d.end' % lno
            parser.set_str(text.get(startatindex, stopatindex) + ' \n')
            parser.set_lo(0)
        self.rawtext = parser.str[:-2]
        self.stopatindex = stopatindex
        self.bracketing = parser.get_last_stmt_bracketing()
        self.isopener = [ i > 0 and self.bracketing[i][1] > self.bracketing[i - 1][1] for i in range(len(self.bracketing)) ]
        self.set_index(index)
        return

    def set_index(self, index):
        indexinrawtext = len(self.rawtext) - len(self.text.get(index, self.stopatindex))
        if indexinrawtext < 0:
            raise ValueError('The index given is before the analyzed statement')
        self.indexinrawtext = indexinrawtext
        self.indexbracket = 0
        while 1:
            self.indexbracket < len(self.bracketing) - 1 and self.bracketing[self.indexbracket + 1][0] < self.indexinrawtext and self.indexbracket += 1

        if self.indexbracket < len(self.bracketing) - 1 and self.bracketing[self.indexbracket + 1][0] == self.indexinrawtext and not self.isopener[self.indexbracket + 1]:
            self.indexbracket += 1

    def is_in_string(self):
        return self.isopener[self.indexbracket] and self.rawtext[self.bracketing[self.indexbracket][0]] in ('"', "'")

    def is_in_code(self):
        return not self.isopener[self.indexbracket] or self.rawtext[self.bracketing[self.indexbracket][0]] not in ('#', '"', "'")

    def get_surrounding_brackets(self, openers='([{', mustclose=False):
        bracketinglevel = self.bracketing[self.indexbracket][1]
        before = self.indexbracket
        while 1:
            if not self.isopener[before] or self.rawtext[self.bracketing[before][0]] not in openers or self.bracketing[before][1] > bracketinglevel:
                before -= 1
                return before < 0 and None
            bracketinglevel = min(bracketinglevel, self.bracketing[before][1])

        after = self.indexbracket + 1
        while 1:
            after < len(self.bracketing) and self.bracketing[after][1] >= bracketinglevel and after += 1

        beforeindex = self.text.index('%s-%dc' % (self.stopatindex, len(self.rawtext) - self.bracketing[before][0]))
        if after >= len(self.bracketing) or self.bracketing[after][0] > len(self.rawtext):
            if mustclose:
                return None
            afterindex = self.stopatindex
        else:
            afterindex = self.text.index('%s-%dc' % (self.stopatindex, len(self.rawtext) - (self.bracketing[after][0] - 1)))
        return (beforeindex, afterindex)

    _whitespace_chars = ' \t\n\\'
    _id_chars = string.ascii_letters + string.digits + '_'
    _id_first_chars = string.ascii_letters + '_'

    def _eat_identifier(self, str, limit, pos):
        i = pos
        while i > limit and str[i - 1] in self._id_chars:
            i -= 1

        if i < pos and (str[i] not in self._id_first_chars or keyword.iskeyword(str[i:pos])):
            i = pos
        return pos - i

    def get_expression(self):
        if not self.is_in_code():
            raise ValueError('get_expression should only be called if index is inside a code.')
        rawtext = self.rawtext
        bracketing = self.bracketing
        brck_index = self.indexbracket
        brck_limit = bracketing[brck_index][0]
        pos = self.indexinrawtext
        last_identifier_pos = pos
        postdot_phase = True
        while 1:
            while 1:
                if pos > brck_limit and rawtext[pos - 1] in self._whitespace_chars:
                    pos -= 1
                if not postdot_phase and pos > brck_limit and rawtext[pos - 1] == '.':
                    pos -= 1
                    postdot_phase = True
                if pos == brck_limit and brck_index > 0 and rawtext[bracketing[brck_index - 1][0]] == '#':
                    brck_index -= 2
                    brck_limit = bracketing[brck_index][0]
                    pos = bracketing[brck_index + 1][0]
                break

            if not postdot_phase:
                break
            ret = self._eat_identifier(rawtext, brck_limit, pos)
            if ret:
                pos = pos - ret
                last_identifier_pos = pos
                postdot_phase = False
            if pos == brck_limit:
                level = bracketing[brck_index][1]
                while brck_index > 0 and bracketing[brck_index - 1][1] > level:
                    brck_index -= 1

                if bracketing[brck_index][0] == brck_limit:
                    break
                pos = bracketing[brck_index][0]
                brck_index -= 1
                brck_limit = bracketing[brck_index][0]
                last_identifier_pos = pos
                if rawtext[pos] in '([':
                    pass
                else:
                    if rawtext[pos] in '\'"':
                        while pos > 0 and rawtext[pos - 1] in 'rRbBuU':
                            pos -= 1

                        last_identifier_pos = pos
                    break
            break

        return rawtext[last_identifier_pos:self.indexinrawtext]
