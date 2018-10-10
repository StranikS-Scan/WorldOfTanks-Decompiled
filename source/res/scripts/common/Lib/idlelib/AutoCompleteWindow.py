# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/AutoCompleteWindow.py
from Tkinter import *
from idlelib.MultiCall import MC_SHIFT
from idlelib.AutoComplete import COMPLETE_FILES, COMPLETE_ATTRIBUTES
HIDE_VIRTUAL_EVENT_NAME = '<<autocompletewindow-hide>>'
HIDE_SEQUENCES = ('<FocusOut>', '<ButtonPress>')
KEYPRESS_VIRTUAL_EVENT_NAME = '<<autocompletewindow-keypress>>'
KEYPRESS_SEQUENCES = ('<Key>', '<Key-BackSpace>', '<Key-Return>', '<Key-Tab>', '<Key-Up>', '<Key-Down>', '<Key-Home>', '<Key-End>', '<Key-Prior>', '<Key-Next>')
KEYRELEASE_VIRTUAL_EVENT_NAME = '<<autocompletewindow-keyrelease>>'
KEYRELEASE_SEQUENCE = '<KeyRelease>'
LISTUPDATE_SEQUENCE = '<B1-ButtonRelease>'
WINCONFIG_SEQUENCE = '<Configure>'
DOUBLECLICK_SEQUENCE = '<B1-Double-ButtonRelease>'

class AutoCompleteWindow:

    def __init__(self, widget):
        self.widget = widget
        self.autocompletewindow = self.listbox = self.scrollbar = None
        self.origselforeground = self.origselbackground = None
        self.completions = None
        self.morecompletions = None
        self.mode = None
        self.start = None
        self.startindex = None
        self.lasttypedstart = None
        self.userwantswindow = None
        self.hideid = self.keypressid = self.listupdateid = self.winconfigid = self.keyreleaseid = self.doubleclickid = None
        self.lastkey_was_tab = False
        return

    def _change_start(self, newstart):
        min_len = min(len(self.start), len(newstart))
        i = 0
        while i < min_len and self.start[i] == newstart[i]:
            i += 1

        if i < len(self.start):
            self.widget.delete('%s+%dc' % (self.startindex, i), '%s+%dc' % (self.startindex, len(self.start)))
        if i < len(newstart):
            self.widget.insert('%s+%dc' % (self.startindex, i), newstart[i:])
        self.start = newstart

    def _binary_search(self, s):
        i = 0
        j = len(self.completions)
        while j > i:
            m = (i + j) // 2
            if self.completions[m] >= s:
                j = m
            i = m + 1

        return min(i, len(self.completions) - 1)

    def _complete_string(self, s):
        first = self._binary_search(s)
        if self.completions[first][:len(s)] != s:
            return s
        i = first + 1
        j = len(self.completions)
        while j > i:
            m = (i + j) // 2
            if self.completions[m][:len(s)] != s:
                j = m
            i = m + 1

        last = i - 1
        if first == last:
            return self.completions[first]
        first_comp = self.completions[first]
        last_comp = self.completions[last]
        min_len = min(len(first_comp), len(last_comp))
        i = len(s)
        while i < min_len and first_comp[i] == last_comp[i]:
            i += 1

        return first_comp[:i]

    def _selection_changed(self):
        cursel = int(self.listbox.curselection()[0])
        self.listbox.see(cursel)
        lts = self.lasttypedstart
        selstart = self.completions[cursel]
        if self._binary_search(lts) == cursel:
            newstart = lts
        else:
            min_len = min(len(lts), len(selstart))
            i = 0
            while i < min_len and lts[i] == selstart[i]:
                i += 1

            newstart = selstart[:i]
        self._change_start(newstart)
        if self.completions[cursel][:len(self.start)] == self.start:
            self.listbox.configure(selectbackground=self.origselbackground, selectforeground=self.origselforeground)
        else:
            self.listbox.configure(selectbackground=self.listbox.cget('bg'), selectforeground=self.listbox.cget('fg'))
            if self.morecompletions:
                self.completions = self.morecompletions
                self.morecompletions = None
                self.listbox.delete(0, END)
                for item in self.completions:
                    self.listbox.insert(END, item)

                self.listbox.select_set(self._binary_search(self.start))
                self._selection_changed()
        return

    def show_window(self, comp_lists, index, complete, mode, userWantsWin):
        self.completions, self.morecompletions = comp_lists
        self.mode = mode
        self.startindex = self.widget.index(index)
        self.start = self.widget.get(self.startindex, 'insert')
        if complete:
            completed = self._complete_string(self.start)
            start = self.start
            self._change_start(completed)
            i = self._binary_search(completed)
            if self.completions[i] == completed and (i == len(self.completions) - 1 or self.completions[i + 1][:len(completed)] != completed):
                return completed == start
        self.userwantswindow = userWantsWin
        self.lasttypedstart = self.start
        self.autocompletewindow = acw = Toplevel(self.widget)
        acw.wm_geometry('+10000+10000')
        acw.wm_overrideredirect(1)
        try:
            acw.tk.call('::tk::unsupported::MacWindowStyle', 'style', acw._w, 'help', 'noActivates')
        except TclError:
            pass

        self.scrollbar = scrollbar = Scrollbar(acw, orient=VERTICAL)
        self.listbox = listbox = Listbox(acw, yscrollcommand=scrollbar.set, exportselection=False, bg='white')
        for item in self.completions:
            listbox.insert(END, item)

        self.origselforeground = listbox.cget('selectforeground')
        self.origselbackground = listbox.cget('selectbackground')
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.listbox.select_set(self._binary_search(self.start))
        self._selection_changed()
        self.hideid = self.widget.bind(HIDE_VIRTUAL_EVENT_NAME, self.hide_event)
        for seq in HIDE_SEQUENCES:
            self.widget.event_add(HIDE_VIRTUAL_EVENT_NAME, seq)

        self.keypressid = self.widget.bind(KEYPRESS_VIRTUAL_EVENT_NAME, self.keypress_event)
        for seq in KEYPRESS_SEQUENCES:
            self.widget.event_add(KEYPRESS_VIRTUAL_EVENT_NAME, seq)

        self.keyreleaseid = self.widget.bind(KEYRELEASE_VIRTUAL_EVENT_NAME, self.keyrelease_event)
        self.widget.event_add(KEYRELEASE_VIRTUAL_EVENT_NAME, KEYRELEASE_SEQUENCE)
        self.listupdateid = listbox.bind(LISTUPDATE_SEQUENCE, self.listselect_event)
        self.winconfigid = acw.bind(WINCONFIG_SEQUENCE, self.winconfig_event)
        self.doubleclickid = listbox.bind(DOUBLECLICK_SEQUENCE, self.doubleclick_event)

    def winconfig_event(self, event):
        if not self.is_active():
            return
        text = self.widget
        text.see(self.startindex)
        x, y, cx, cy = text.bbox(self.startindex)
        acw = self.autocompletewindow
        acw_width, acw_height = acw.winfo_width(), acw.winfo_height()
        text_width, text_height = text.winfo_width(), text.winfo_height()
        new_x = text.winfo_rootx() + min(x, max(0, text_width - acw_width))
        new_y = text.winfo_rooty() + y
        if text_height - (y + cy) >= acw_height or y < acw_height:
            new_y += cy
        else:
            new_y -= acw_height
        acw.wm_geometry('+%d+%d' % (new_x, new_y))

    def hide_event(self, event):
        if not self.is_active():
            return
        self.hide_window()

    def listselect_event(self, event):
        if not self.is_active():
            return
        self.userwantswindow = True
        cursel = int(self.listbox.curselection()[0])
        self._change_start(self.completions[cursel])

    def doubleclick_event(self, event):
        cursel = int(self.listbox.curselection()[0])
        self._change_start(self.completions[cursel])
        self.hide_window()

    def keypress_event(self, event):
        if not self.is_active():
            return
        keysym = event.keysym
        if hasattr(event, 'mc_state'):
            state = event.mc_state
        else:
            state = 0
        if keysym != 'Tab':
            self.lastkey_was_tab = False
        if (len(keysym) == 1 or keysym in ('underscore', 'BackSpace') or self.mode == COMPLETE_FILES and keysym in ('period', 'minus')) and not state & ~MC_SHIFT:
            if len(keysym) == 1:
                self._change_start(self.start + keysym)
            elif keysym == 'underscore':
                self._change_start(self.start + '_')
            elif keysym == 'period':
                self._change_start(self.start + '.')
            elif keysym == 'minus':
                self._change_start(self.start + '-')
            else:
                if len(self.start) == 0:
                    self.hide_window()
                    return
                self._change_start(self.start[:-1])
            self.lasttypedstart = self.start
            self.listbox.select_clear(0, int(self.listbox.curselection()[0]))
            self.listbox.select_set(self._binary_search(self.start))
            self._selection_changed()
            return 'break'
        if keysym == 'Return':
            self.hide_window()
            return
        if self.mode == COMPLETE_ATTRIBUTES and keysym in ('period', 'space', 'parenleft', 'parenright', 'bracketleft', 'bracketright') or self.mode == COMPLETE_FILES and keysym in ('slash', 'backslash', 'quotedbl', 'apostrophe') and not state & ~MC_SHIFT:
            cursel = int(self.listbox.curselection()[0])
            if self.completions[cursel][:len(self.start)] == self.start and (self.mode == COMPLETE_ATTRIBUTES or self.start):
                self._change_start(self.completions[cursel])
            self.hide_window()
            return
        if keysym in ('Home', 'End', 'Prior', 'Next', 'Up', 'Down') and not state:
            self.userwantswindow = True
            cursel = int(self.listbox.curselection()[0])
            if keysym == 'Home':
                newsel = 0
            elif keysym == 'End':
                newsel = len(self.completions) - 1
            elif keysym in ('Prior', 'Next'):
                jump = self.listbox.nearest(self.listbox.winfo_height()) - self.listbox.nearest(0)
                if keysym == 'Prior':
                    newsel = max(0, cursel - jump)
                else:
                    newsel = min(len(self.completions) - 1, cursel + jump)
            elif keysym == 'Up':
                newsel = max(0, cursel - 1)
            else:
                newsel = min(len(self.completions) - 1, cursel + 1)
            self.listbox.select_clear(cursel)
            self.listbox.select_set(newsel)
            self._selection_changed()
            self._change_start(self.completions[newsel])
            return 'break'
        if keysym == 'Tab' and not state:
            if self.lastkey_was_tab:
                cursel = int(self.listbox.curselection()[0])
                self._change_start(self.completions[cursel])
                self.hide_window()
                return 'break'
            else:
                self.userwantswindow = True
                self.lastkey_was_tab = True
                return
        else:
            if any((s in keysym for s in ('Shift', 'Control', 'Alt', 'Meta', 'Command', 'Option'))):
                return
            self.hide_window()
            return

    def keyrelease_event(self, event):
        if not self.is_active():
            return
        if self.widget.index('insert') != self.widget.index('%s+%dc' % (self.startindex, len(self.start))):
            self.hide_window()

    def is_active(self):
        return self.autocompletewindow is not None

    def complete(self):
        self._change_start(self._complete_string(self.start))

    def hide_window(self):
        if not self.is_active():
            return
        else:
            for seq in HIDE_SEQUENCES:
                self.widget.event_delete(HIDE_VIRTUAL_EVENT_NAME, seq)

            self.widget.unbind(HIDE_VIRTUAL_EVENT_NAME, self.hideid)
            self.hideid = None
            for seq in KEYPRESS_SEQUENCES:
                self.widget.event_delete(KEYPRESS_VIRTUAL_EVENT_NAME, seq)

            self.widget.unbind(KEYPRESS_VIRTUAL_EVENT_NAME, self.keypressid)
            self.keypressid = None
            self.widget.event_delete(KEYRELEASE_VIRTUAL_EVENT_NAME, KEYRELEASE_SEQUENCE)
            self.widget.unbind(KEYRELEASE_VIRTUAL_EVENT_NAME, self.keyreleaseid)
            self.keyreleaseid = None
            self.listbox.unbind(LISTUPDATE_SEQUENCE, self.listupdateid)
            self.listupdateid = None
            self.autocompletewindow.unbind(WINCONFIG_SEQUENCE, self.winconfigid)
            self.winconfigid = None
            self.scrollbar.destroy()
            self.scrollbar = None
            self.listbox.destroy()
            self.listbox = None
            self.autocompletewindow.destroy()
            self.autocompletewindow = None
            return
