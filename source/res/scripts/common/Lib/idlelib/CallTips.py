# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/CallTips.py
import __main__
import re
import sys
import textwrap
import types
from idlelib import CallTipWindow
from idlelib.HyperParser import HyperParser

class CallTips:
    menudefs = [('edit', [('Show call tip', '<<force-open-calltip>>')])]

    def __init__(self, editwin=None):
        if editwin is None:
            self.editwin = None
            return
        else:
            self.editwin = editwin
            self.text = editwin.text
            self.calltip = None
            self._make_calltip_window = self._make_tk_calltip_window
            return

    def close(self):
        self._make_calltip_window = None
        return

    def _make_tk_calltip_window(self):
        return CallTipWindow.CallTip(self.text)

    def _remove_calltip_window(self, event=None):
        if self.calltip:
            self.calltip.hidetip()
            self.calltip = None
        return

    def force_open_calltip_event(self, event):
        self.open_calltip(True)

    def try_open_calltip_event(self, event):
        self.open_calltip(False)

    def refresh_calltip_event(self, event):
        if self.calltip and self.calltip.is_active():
            self.open_calltip(False)

    def open_calltip(self, evalfuncs):
        self._remove_calltip_window()
        hp = HyperParser(self.editwin, 'insert')
        sur_paren = hp.get_surrounding_brackets('(')
        if not sur_paren:
            return
        hp.set_index(sur_paren[0])
        expression = hp.get_expression()
        if not expression or not evalfuncs and expression.find('(') != -1:
            return
        arg_text = self.fetch_tip(expression)
        if not arg_text:
            return
        self.calltip = self._make_calltip_window()
        self.calltip.showtip(arg_text, sur_paren[0], sur_paren[1])

    def fetch_tip(self, expression):
        try:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        except AttributeError:
            rpcclt = None

        if rpcclt:
            return rpcclt.remotecall('exec', 'get_the_calltip', (expression,), {})
        else:
            entity = self.get_entity(expression)
            return get_arg_text(entity)
            return

    def get_entity(self, expression):
        if expression:
            namespace = sys.modules.copy()
            namespace.update(__main__.__dict__)
            try:
                return eval(expression, namespace)
            except BaseException:
                return None

        return None


def _find_constructor(class_ob):
    try:
        return class_ob.__init__.im_func
    except AttributeError:
        for base in class_ob.__bases__:
            rc = _find_constructor(base)
            if rc is not None:
                return rc

    return


_MAX_COLS = 85
_MAX_LINES = 5
_INDENT = '    '

def get_arg_text(ob):
    argspec = ''
    try:
        ob_call = ob.__call__
    except BaseException:
        if type(ob) is types.ClassType:
            ob_call = ob
        else:
            return argspec

    arg_offset = 0
    if type(ob) in (types.ClassType, types.TypeType):
        fob = _find_constructor(ob)
        if fob is None:
            fob = lambda : None
        else:
            arg_offset = 1
    elif type(ob) == types.MethodType:
        fob = ob.im_func
        if ob.im_self:
            arg_offset = 1
    elif type(ob_call) == types.MethodType:
        fob = ob_call.im_func
        arg_offset = 1
    else:
        fob = ob
    if type(fob) in [types.FunctionType, types.LambdaType]:
        argcount = fob.func_code.co_argcount
        real_args = fob.func_code.co_varnames[arg_offset:argcount]
        defaults = fob.func_defaults or []
        defaults = list(map(lambda name: '=%s' % repr(name), defaults))
        defaults = [''] * (len(real_args) - len(defaults)) + defaults
        items = map(lambda arg, dflt: arg + dflt, real_args, defaults)
        if fob.func_code.co_flags & 4:
            items.append('*args')
        if fob.func_code.co_flags & 8:
            items.append('**kwds')
        argspec = ', '.join(items)
        argspec = '(%s)' % re.sub('(?<!\\d)\\.\\d+', '<tuple>', argspec)
    lines = textwrap.wrap(argspec, _MAX_COLS, subsequent_indent=_INDENT) if len(argspec) > _MAX_COLS else ([argspec] if argspec else [])
    if isinstance(ob_call, types.MethodType):
        doc = ob_call.__doc__
    else:
        doc = getattr(ob, '__doc__', '')
    if doc:
        for line in doc.split('\n', _MAX_LINES)[:_MAX_LINES]:
            line = line.strip()
            if not line:
                break
            if len(line) > _MAX_COLS:
                line = line[:_MAX_COLS - 3] + '...'
            lines.append(line)

        argspec = '\n'.join(lines)
    return argspec


if __name__ == '__main__':
    from unittest import main
    main('idlelib.idle_test.test_calltips', verbosity=2)
