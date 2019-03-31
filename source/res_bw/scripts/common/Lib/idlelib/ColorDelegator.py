# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/ColorDelegator.py
# Compiled at: 2010-05-25 20:46:16
import time
import re
import keyword
import __builtin__
from Tkinter import *
from Delegator import Delegator
from configHandler import idleConf
DEBUG = False

def any(name, alternates):
    """Return a named group pattern matching list of alternates."""
    return '(?P<%s>' % name + '|'.join(alternates) + ')'


def make_pat():
    kw = '\\b' + any('KEYWORD', keyword.kwlist) + '\\b'
    builtinlist = [ str(name) for name in dir(__builtin__) if not name.startswith('_') ]
    builtin = '([^.\'\\"\\\\#]\\b|^)' + any('BUILTIN', builtinlist) + '\\b'
    comment = any('COMMENT', ['#[^\\n]*'])
    sqstring = "(\\b[rRuU])?'[^'\\\\\\n]*(\\\\.[^'\\\\\\n]*)*'?"
    dqstring = '(\\b[rRuU])?"[^"\\\\\\n]*(\\\\.[^"\\\\\\n]*)*"?'
    sq3string = "(\\b[rRuU])?'''[^'\\\\]*((\\\\.|'(?!''))[^'\\\\]*)*(''')?"
    dq3string = '(\\b[rRuU])?"""[^"\\\\]*((\\\\.|"(?!""))[^"\\\\]*)*(""")?'
    string = any('STRING', [sq3string,
     dq3string,
     sqstring,
     dqstring])
    return kw + '|' + builtin + '|' + comment + '|' + string + '|' + any('SYNC', ['\\n'])


prog = re.compile(make_pat(), re.S)
idprog = re.compile('\\s+(\\w+)', re.S)
asprog = re.compile('.*?\\b(as)\\b')

class ColorDelegator(Delegator):

    def __init__(self):
        Delegator.__init__(self)
        self.prog = prog
        self.idprog = idprog
        self.asprog = asprog
        self.LoadTagDefs()

    def setdelegate(self, delegate):
        if self.delegate is not None:
            self.unbind('<<toggle-auto-coloring>>')
        Delegator.setdelegate(self, delegate)
        if delegate is not None:
            self.config_colors()
            self.bind('<<toggle-auto-coloring>>', self.toggle_colorize_event)
            self.notify_range('1.0', 'end')
        return

    def config_colors(self):
        for tag, cnf in self.tagdefs.items():
            if cnf:
                self.tag_configure(tag, **cnf)

        self.tag_raise('sel')

    def LoadTagDefs(self):
        theme = idleConf.GetOption('main', 'Theme', 'name')
        self.tagdefs = {'COMMENT': idleConf.GetHighlight(theme, 'comment'),
         'KEYWORD': idleConf.GetHighlight(theme, 'keyword'),
         'BUILTIN': idleConf.GetHighlight(theme, 'builtin'),
         'STRING': idleConf.GetHighlight(theme, 'string'),
         'DEFINITION': idleConf.GetHighlight(theme, 'definition'),
         'SYNC': {'background': None,
                  'foreground': None},
         'TODO': {'background': None,
                  'foreground': None},
         'BREAK': idleConf.GetHighlight(theme, 'break'),
         'ERROR': idleConf.GetHighlight(theme, 'error'),
         'hit': idleConf.GetHighlight(theme, 'hit')}
        if DEBUG:
            print 'tagdefs', self.tagdefs
        return

    def insert(self, index, chars, tags=None):
        index = self.index(index)
        self.delegate.insert(index, chars, tags)
        self.notify_range(index, index + '+%dc' % len(chars))

    def delete(self, index1, index2=None):
        index1 = self.index(index1)
        self.delegate.delete(index1, index2)
        self.notify_range(index1)

    after_id = None
    allow_colorizing = True
    colorizing = False

    def notify_range(self, index1, index2=None):
        self.tag_add('TODO', index1, index2)
        if self.after_id:
            if DEBUG:
                print 'colorizing already scheduled'
            return
        if self.colorizing:
            self.stop_colorizing = True
            if DEBUG:
                print 'stop colorizing'
        if self.allow_colorizing:
            if DEBUG:
                print 'schedule colorizing'
            self.after_id = self.after(1, self.recolorize)

    close_when_done = None

    def close(self, close_when_done=None):
        if self.after_id:
            after_id = self.after_id
            self.after_id = None
            if DEBUG:
                print 'cancel scheduled recolorizer'
            self.after_cancel(after_id)
        self.allow_colorizing = False
        self.stop_colorizing = True
        if close_when_done:
            if not self.colorizing:
                close_when_done.destroy()
            else:
                self.close_when_done = close_when_done
        return

    def toggle_colorize_event(self, event):
        if self.after_id:
            after_id = self.after_id
            self.after_id = None
            if DEBUG:
                print 'cancel scheduled recolorizer'
            self.after_cancel(after_id)
        if self.allow_colorizing and self.colorizing:
            if DEBUG:
                print 'stop colorizing'
            self.stop_colorizing = True
        self.allow_colorizing = not self.allow_colorizing
        if self.allow_colorizing and not self.colorizing:
            self.after_id = self.after(1, self.recolorize)
        if DEBUG:
            print 'auto colorizing turned',
            print self.allow_colorizing and 'on' or 'off'
        return 'break'

    def recolorize(self):
        self.after_id = None
        if not self.delegate:
            if DEBUG:
                print 'no delegate'
            return
        elif not self.allow_colorizing:
            if DEBUG:
                print 'auto colorizing is off'
            return
        elif self.colorizing:
            if DEBUG:
                print 'already colorizing'
            return
        else:
            try:
                self.stop_colorizing = False
                self.colorizing = True
                if DEBUG:
                    print 'colorizing...'
                t0 = time.clock()
                self.recolorize_main()
                t1 = time.clock()
                if DEBUG:
                    print '%.3f seconds' % (t1 - t0)
            finally:
                self.colorizing = False

            if self.allow_colorizing and self.tag_nextrange('TODO', '1.0'):
                if DEBUG:
                    print 'reschedule colorizing'
                self.after_id = self.after(1, self.recolorize)
            if self.close_when_done:
                top = self.close_when_done
                self.close_when_done = None
                top.destroy()
            return

    def recolorize_main--- This code section failed: ---

 166       0	LOAD_CONST        '1.0'
           3	STORE_FAST        'next'

 167       6	SETUP_LOOP        '841'
           9	LOAD_GLOBAL       'True'
          12	JUMP_IF_FALSE     '840'

 168      15	LOAD_FAST         'self'
          18	LOAD_ATTR         'tag_nextrange'
          21	LOAD_CONST        'TODO'
          24	LOAD_FAST         'next'
          27	CALL_FUNCTION_2   ''
          30	STORE_FAST        'item'

 169      33	LOAD_FAST         'item'
          36	JUMP_IF_TRUE      '43'

 170      39	BREAK_LOOP        ''
          40	JUMP_FORWARD      '43'
        43_0	COME_FROM         '40'

 171      43	LOAD_FAST         'item'
          46	UNPACK_SEQUENCE_2 ''
          49	STORE_FAST        'head'
          52	STORE_FAST        'tail'

 172      55	LOAD_FAST         'self'
          58	LOAD_ATTR         'tag_remove'
          61	LOAD_CONST        'SYNC'
          64	LOAD_FAST         'head'
          67	LOAD_FAST         'tail'
          70	CALL_FUNCTION_3   ''
          73	POP_TOP           ''

 173      74	LOAD_FAST         'self'
          77	LOAD_ATTR         'tag_prevrange'
          80	LOAD_CONST        'SYNC'
          83	LOAD_FAST         'head'
          86	CALL_FUNCTION_2   ''
          89	STORE_FAST        'item'

 174      92	LOAD_FAST         'item'
          95	JUMP_IF_FALSE     '111'

 175      98	LOAD_FAST         'item'
         101	LOAD_CONST        1
         104	BINARY_SUBSCR     ''
         105	STORE_FAST        'head'
         108	JUMP_FORWARD      '117'

 177     111	LOAD_CONST        '1.0'
         114	STORE_FAST        'head'
       117_0	COME_FROM         '108'

 179     117	LOAD_CONST        ''
         120	STORE_FAST        'chars'

 180     123	LOAD_FAST         'head'
         126	STORE_FAST        'next'

 181     129	LOAD_CONST        1
         132	STORE_FAST        'lines_to_get'

 182     135	LOAD_GLOBAL       'False'
         138	STORE_FAST        'ok'

 183     141	SETUP_LOOP        '837'
         144	LOAD_FAST         'ok'
         147	JUMP_IF_TRUE      '836'

 184     150	LOAD_FAST         'next'
         153	STORE_FAST        'mark'

 185     156	LOAD_FAST         'self'
         159	LOAD_ATTR         'index'
         162	LOAD_FAST         'mark'
         165	LOAD_CONST        '+%d lines linestart'

 186     168	LOAD_FAST         'lines_to_get'
         171	BINARY_MODULO     ''
         172	BINARY_ADD        ''
         173	CALL_FUNCTION_1   ''
         176	STORE_FAST        'next'

 187     179	LOAD_GLOBAL       'min'
         182	LOAD_FAST         'lines_to_get'
         185	LOAD_CONST        2
         188	BINARY_MULTIPLY   ''
         189	LOAD_CONST        100
         192	CALL_FUNCTION_2   ''
         195	STORE_FAST        'lines_to_get'

 188     198	LOAD_CONST        'SYNC'
         201	LOAD_FAST         'self'
         204	LOAD_ATTR         'tag_names'
         207	LOAD_FAST         'next'
         210	LOAD_CONST        '-1c'
         213	BINARY_ADD        ''
         214	CALL_FUNCTION_1   ''
         217	COMPARE_OP        'in'
         220	STORE_FAST        'ok'

 189     223	LOAD_FAST         'self'
         226	LOAD_ATTR         'get'
         229	LOAD_FAST         'mark'
         232	LOAD_FAST         'next'
         235	CALL_FUNCTION_2   ''
         238	STORE_FAST        'line'

 191     241	LOAD_FAST         'line'
         244	JUMP_IF_TRUE      '251'

 192     247	LOAD_CONST        ''
         250	RETURN_END_IF     ''

 193     251	SETUP_LOOP        '296'
         254	LOAD_FAST         'self'
         257	LOAD_ATTR         'tagdefs'
         260	LOAD_ATTR         'keys'
         263	CALL_FUNCTION_0   ''
         266	GET_ITER          ''
         267	FOR_ITER          '295'
         270	STORE_FAST        'tag'

 194     273	LOAD_FAST         'self'
         276	LOAD_ATTR         'tag_remove'
         279	LOAD_FAST         'tag'
         282	LOAD_FAST         'mark'
         285	LOAD_FAST         'next'
         288	CALL_FUNCTION_3   ''
         291	POP_TOP           ''
         292	JUMP_BACK         '267'
         295	POP_BLOCK         ''
       296_0	COME_FROM         '251'

 195     296	LOAD_FAST         'chars'
         299	LOAD_FAST         'line'
         302	BINARY_ADD        ''
         303	STORE_FAST        'chars'

 196     306	LOAD_FAST         'self'
         309	LOAD_ATTR         'prog'
         312	LOAD_ATTR         'search'
         315	LOAD_FAST         'chars'
         318	CALL_FUNCTION_1   ''
         321	STORE_FAST        'm'

 197     324	SETUP_LOOP        '725'
         327	LOAD_FAST         'm'
         330	JUMP_IF_FALSE     '724'

 198     333	SETUP_LOOP        '694'
         336	LOAD_FAST         'm'
         339	LOAD_ATTR         'groupdict'
         342	CALL_FUNCTION_0   ''
         345	LOAD_ATTR         'items'
         348	CALL_FUNCTION_0   ''
         351	GET_ITER          ''
         352	FOR_ITER          '693'
         355	UNPACK_SEQUENCE_2 ''
         358	STORE_FAST        'key'
         361	STORE_FAST        'value'

 199     364	LOAD_FAST         'value'
         367	JUMP_IF_FALSE     '690'

 200     370	LOAD_FAST         'm'
         373	LOAD_ATTR         'span'
         376	LOAD_FAST         'key'
         379	CALL_FUNCTION_1   ''
         382	UNPACK_SEQUENCE_2 ''
         385	STORE_FAST        'a'
         388	STORE_FAST        'b'

 201     391	LOAD_FAST         'self'
         394	LOAD_ATTR         'tag_add'
         397	LOAD_FAST         'key'

 202     400	LOAD_FAST         'head'
         403	LOAD_CONST        '+%dc'
         406	LOAD_FAST         'a'
         409	BINARY_MODULO     ''
         410	BINARY_ADD        ''

 203     411	LOAD_FAST         'head'
         414	LOAD_CONST        '+%dc'
         417	LOAD_FAST         'b'
         420	BINARY_MODULO     ''
         421	BINARY_ADD        ''
         422	CALL_FUNCTION_3   ''
         425	POP_TOP           ''

 204     426	LOAD_FAST         'value'
         429	LOAD_CONST        ('def', 'class')
         432	COMPARE_OP        'in'
         435	JUMP_IF_FALSE     '527'

 205     438	LOAD_FAST         'self'
         441	LOAD_ATTR         'idprog'
         444	LOAD_ATTR         'match'
         447	LOAD_FAST         'chars'
         450	LOAD_FAST         'b'
         453	CALL_FUNCTION_2   ''
         456	STORE_FAST        'm1'

 206     459	LOAD_FAST         'm1'
         462	JUMP_IF_FALSE     '524'

 207     465	LOAD_FAST         'm1'
         468	LOAD_ATTR         'span'
         471	LOAD_CONST        1
         474	CALL_FUNCTION_1   ''
         477	UNPACK_SEQUENCE_2 ''
         480	STORE_FAST        'a'
         483	STORE_FAST        'b'

 208     486	LOAD_FAST         'self'
         489	LOAD_ATTR         'tag_add'
         492	LOAD_CONST        'DEFINITION'

 209     495	LOAD_FAST         'head'
         498	LOAD_CONST        '+%dc'
         501	LOAD_FAST         'a'
         504	BINARY_MODULO     ''
         505	BINARY_ADD        ''

 210     506	LOAD_FAST         'head'
         509	LOAD_CONST        '+%dc'
         512	LOAD_FAST         'b'
         515	BINARY_MODULO     ''
         516	BINARY_ADD        ''
         517	CALL_FUNCTION_3   ''
         520	POP_TOP           ''
         521	JUMP_ABSOLUTE     '687'
         524	JUMP_ABSOLUTE     '690'

 211     527	LOAD_FAST         'value'
         530	LOAD_CONST        'import'
         533	COMPARE_OP        '=='
         536	JUMP_IF_FALSE     '687'

 215     539	LOAD_CONST        '#'
         542	LOAD_FAST         'chars'
         545	COMPARE_OP        'in'
         548	JUMP_IF_FALSE     '569'

 216     551	LOAD_FAST         'chars'
         554	LOAD_ATTR         'index'
         557	LOAD_CONST        '#'
         560	CALL_FUNCTION_1   ''
         563	STORE_FAST        'endpos'
         566	JUMP_FORWARD      '581'

 218     569	LOAD_GLOBAL       'len'
         572	LOAD_FAST         'chars'
         575	CALL_FUNCTION_1   ''
         578	STORE_FAST        'endpos'
       581_0	COME_FROM         '566'

 219     581	SETUP_LOOP        '687'
         584	LOAD_GLOBAL       'True'
         587	JUMP_IF_FALSE     '683'

 220     590	LOAD_FAST         'self'
         593	LOAD_ATTR         'asprog'
         596	LOAD_ATTR         'match'
         599	LOAD_FAST         'chars'
         602	LOAD_FAST         'b'
         605	LOAD_FAST         'endpos'
         608	CALL_FUNCTION_3   ''
         611	STORE_FAST        'm1'

 221     614	LOAD_FAST         'm1'
         617	JUMP_IF_TRUE      '624'

 222     620	BREAK_LOOP        ''
         621	JUMP_FORWARD      '624'
       624_0	COME_FROM         '621'

 223     624	LOAD_FAST         'm1'
         627	LOAD_ATTR         'span'
         630	LOAD_CONST        1
         633	CALL_FUNCTION_1   ''
         636	UNPACK_SEQUENCE_2 ''
         639	STORE_FAST        'a'
         642	STORE_FAST        'b'

 224     645	LOAD_FAST         'self'
         648	LOAD_ATTR         'tag_add'
         651	LOAD_CONST        'KEYWORD'

 225     654	LOAD_FAST         'head'
         657	LOAD_CONST        '+%dc'
         660	LOAD_FAST         'a'
         663	BINARY_MODULO     ''
         664	BINARY_ADD        ''

 226     665	LOAD_FAST         'head'
         668	LOAD_CONST        '+%dc'
         671	LOAD_FAST         'b'
         674	BINARY_MODULO     ''
         675	BINARY_ADD        ''
         676	CALL_FUNCTION_3   ''
         679	POP_TOP           ''
         680	JUMP_BACK         '584'
         683	POP_BLOCK         ''
       684_0	COME_FROM         '581'
         684	JUMP_ABSOLUTE     '690'
         687	JUMP_BACK         '352'
         690	JUMP_BACK         '352'
         693	POP_BLOCK         ''
       694_0	COME_FROM         '333'

 227     694	LOAD_FAST         'self'
         697	LOAD_ATTR         'prog'
         700	LOAD_ATTR         'search'
         703	LOAD_FAST         'chars'
         706	LOAD_FAST         'm'
         709	LOAD_ATTR         'end'
         712	CALL_FUNCTION_0   ''
         715	CALL_FUNCTION_2   ''
         718	STORE_FAST        'm'
         721	JUMP_BACK         '327'
         724	POP_BLOCK         ''
       725_0	COME_FROM         '324'

 228     725	LOAD_CONST        'SYNC'
         728	LOAD_FAST         'self'
         731	LOAD_ATTR         'tag_names'
         734	LOAD_FAST         'next'
         737	LOAD_CONST        '-1c'
         740	BINARY_ADD        ''
         741	CALL_FUNCTION_1   ''
         744	COMPARE_OP        'in'
         747	JUMP_IF_FALSE     '765'

 229     750	LOAD_FAST         'next'
         753	STORE_FAST        'head'

 230     756	LOAD_CONST        ''
         759	STORE_FAST        'chars'
         762	JUMP_FORWARD      '771'

 232     765	LOAD_GLOBAL       'False'
         768	STORE_FAST        'ok'
       771_0	COME_FROM         '762'

 233     771	LOAD_FAST         'ok'
         774	JUMP_IF_TRUE      '796'

 240     777	LOAD_FAST         'self'
         780	LOAD_ATTR         'tag_add'
         783	LOAD_CONST        'TODO'
         786	LOAD_FAST         'next'
         789	CALL_FUNCTION_2   ''
         792	POP_TOP           ''
         793	JUMP_FORWARD      '796'
       796_0	COME_FROM         '793'

 241     796	LOAD_FAST         'self'
         799	LOAD_ATTR         'update'
         802	CALL_FUNCTION_0   ''
         805	POP_TOP           ''

 242     806	LOAD_FAST         'self'
         809	LOAD_ATTR         'stop_colorizing'
         812	JUMP_IF_FALSE     '833'

 243     815	LOAD_GLOBAL       'DEBUG'
         818	JUMP_IF_FALSE     '829'
         821	LOAD_CONST        'colorizing stopped'
         824	PRINT_ITEM        ''
         825	PRINT_NEWLINE_CONT ''
         826	JUMP_FORWARD      '829'
       829_0	COME_FROM         '826'

 244     829	LOAD_CONST        ''
         832	RETURN_END_IF     ''
         833	JUMP_BACK         '144'
         836	POP_BLOCK         ''
       837_0	COME_FROM         '141'
         837	JUMP_BACK         '9'
         840	POP_BLOCK         ''
       841_0	COME_FROM         '6'

Syntax error at or near 'POP_BLOCK' token at offset 724

    def removecolors(self):
        for tag in self.tagdefs.keys():
            self.tag_remove(tag, '1.0', 'end')


def main():
    from Percolator import Percolator
    root = Tk()
    root.wm_protocol('WM_DELETE_WINDOW', root.quit)
    text = Text(background='white')
    text.pack(expand=1, fill='both')
    text.focus_set()
    p = Percolator(text)
    d = ColorDelegator()
    p.insertfilter(d)
    root.mainloop()


if __name__ == '__main__':
    main()