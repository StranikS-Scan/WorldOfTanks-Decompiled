# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/AutoComplete.py
import os
import sys
import string
from idlelib.configHandler import idleConf
FILENAME_CHARS = string.ascii_letters + string.digits + os.curdir + '._~#$:-'
ID_CHARS = string.ascii_letters + string.digits + '_'
COMPLETE_ATTRIBUTES, COMPLETE_FILES = range(1, 3)
from idlelib import AutoCompleteWindow
from idlelib.HyperParser import HyperParser
import __main__
SEPS = os.sep
if os.altsep:
    SEPS += os.altsep

class AutoComplete:
    menudefs = [('edit', [('Show Completions', '<<force-open-completions>>')])]
    popupwait = idleConf.GetOption('extensions', 'AutoComplete', 'popupwait', type='int', default=0)

    def __init__(self, editwin=None):
        self.editwin = editwin
        if editwin is None:
            return
        else:
            self.text = editwin.text
            self.autocompletewindow = None
            self._delayed_completion_id = None
            self._delayed_completion_index = None
            return

    def _make_autocomplete_window(self):
        return AutoCompleteWindow.AutoCompleteWindow(self.text)

    def _remove_autocomplete_window(self, event=None):
        if self.autocompletewindow:
            self.autocompletewindow.hide_window()
            self.autocompletewindow = None
        return

    def force_open_completions_event(self, event):
        self.open_completions(True, False, True)

    def try_open_completions_event(self, event):
        lastchar = self.text.get('insert-1c')
        if lastchar == '.':
            self._open_completions_later(False, False, False, COMPLETE_ATTRIBUTES)
        elif lastchar in SEPS:
            self._open_completions_later(False, False, False, COMPLETE_FILES)

    def autocomplete_event(self, event):
        if hasattr(event, 'mc_state') and event.mc_state:
            return
        if self.autocompletewindow and self.autocompletewindow.is_active():
            self.autocompletewindow.complete()
            return 'break'
        opened = self.open_completions(False, True, True)
        return 'break' if opened else None

    def _open_completions_later(self, *args):
        self._delayed_completion_index = self.text.index('insert')
        if self._delayed_completion_id is not None:
            self.text.after_cancel(self._delayed_completion_id)
        self._delayed_completion_id = self.text.after(self.popupwait, self._delayed_open_completions, *args)
        return

    def _delayed_open_completions(self, *args):
        self._delayed_completion_id = None
        if self.text.index('insert') != self._delayed_completion_index:
            return
        else:
            self.open_completions(*args)
            return

    def open_completions(self, evalfuncs, complete, userWantsWin, mode=None):
        if self._delayed_completion_id is not None:
            self.text.after_cancel(self._delayed_completion_id)
            self._delayed_completion_id = None
        hp = HyperParser(self.editwin, 'insert')
        curline = self.text.get('insert linestart', 'insert')
        i = j = len(curline)
        if hp.is_in_string() and (not mode or mode == COMPLETE_FILES):
            self._remove_autocomplete_window()
            mode = COMPLETE_FILES
            while i and curline[i - 1] in FILENAME_CHARS:
                i -= 1

            comp_start = curline[i:j]
            j = i
            while i and curline[i - 1] in FILENAME_CHARS + SEPS:
                i -= 1

            comp_what = curline[i:j]
        elif hp.is_in_code() and (not mode or mode == COMPLETE_ATTRIBUTES):
            self._remove_autocomplete_window()
            mode = COMPLETE_ATTRIBUTES
            while i and curline[i - 1] in ID_CHARS:
                i -= 1

            comp_start = curline[i:j]
            if i and curline[i - 1] == '.':
                hp.set_index('insert-%dc' % (len(curline) - (i - 1)))
                comp_what = hp.get_expression()
                if not comp_what or not evalfuncs and comp_what.find('(') != -1:
                    return
            else:
                comp_what = ''
        else:
            return
        if complete and not comp_what and not comp_start:
            return
        else:
            comp_lists = self.fetch_completions(comp_what, mode)
            if not comp_lists[0]:
                return
            self.autocompletewindow = self._make_autocomplete_window()
            return not self.autocompletewindow.show_window(comp_lists, 'insert-%dc' % len(comp_start), complete, mode, userWantsWin)

    def fetch_completions(self, what, mode):
        try:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        except:
            rpcclt = None

        if rpcclt:
            return rpcclt.remotecall('exec', 'get_the_completion_list', (what, mode), {})
        else:
            if mode == COMPLETE_ATTRIBUTES:
                if what == '':
                    namespace = __main__.__dict__.copy()
                    namespace.update(__main__.__builtins__.__dict__)
                    bigl = eval('dir()', namespace)
                    bigl.sort()
                    if '__all__' in bigl:
                        smalll = sorted(eval('__all__', namespace))
                    else:
                        smalll = [ s for s in bigl if s[:1] != '_' ]
                else:
                    try:
                        entity = self.get_entity(what)
                        bigl = dir(entity)
                        bigl.sort()
                        if '__all__' in bigl:
                            smalll = sorted(entity.__all__)
                        else:
                            smalll = [ s for s in bigl if s[:1] != '_' ]
                    except:
                        return ([], [])

            elif mode == COMPLETE_FILES:
                if what == '':
                    what = '.'
                try:
                    expandedpath = os.path.expanduser(what)
                    bigl = os.listdir(expandedpath)
                    bigl.sort()
                    smalll = [ s for s in bigl if s[:1] != '.' ]
                except OSError:
                    return ([], [])

            if not smalll:
                smalll = bigl
            return (smalll, bigl)
            return

    def get_entity(self, name):
        namespace = sys.modules.copy()
        namespace.update(__main__.__dict__)
        return eval(name, namespace)
