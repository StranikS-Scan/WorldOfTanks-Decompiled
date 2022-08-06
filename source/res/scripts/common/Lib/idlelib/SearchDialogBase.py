# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/SearchDialogBase.py
from Tkinter import Toplevel, Frame, Entry, Label, Button, Checkbutton, Radiobutton

class SearchDialogBase:
    title = 'Search Dialog'
    icon = 'Search'
    needwrapbutton = 1

    def __init__(self, root, engine):
        self.root = root
        self.engine = engine
        self.top = None
        return

    def open(self, text, searchphrase=None):
        self.text = text
        if not self.top:
            self.create_widgets()
        else:
            self.top.deiconify()
            self.top.tkraise()
        self.top.transient(text.winfo_toplevel())
        if searchphrase:
            self.ent.delete(0, 'end')
            self.ent.insert('end', searchphrase)
        self.ent.focus_set()
        self.ent.selection_range(0, 'end')
        self.ent.icursor(0)
        self.top.grab_set()

    def close(self, event=None):
        if self.top:
            self.top.grab_release()
            self.top.transient('')
            self.top.withdraw()

    def create_widgets(self):
        top = Toplevel(self.root)
        top.bind('<Return>', self.default_command)
        top.bind('<Escape>', self.close)
        top.protocol('WM_DELETE_WINDOW', self.close)
        top.wm_title(self.title)
        top.wm_iconname(self.icon)
        self.top = top
        self.row = 0
        self.top.grid_columnconfigure(0, pad=2, weight=0)
        self.top.grid_columnconfigure(1, pad=2, minsize=100, weight=100)
        self.create_entries()
        self.create_option_buttons()
        self.create_other_buttons()
        self.create_command_buttons()

    def make_entry(self, label_text, var):
        label = Label(self.top, text=label_text)
        label.grid(row=self.row, column=0, sticky='nw')
        entry = Entry(self.top, textvariable=var, exportselection=0)
        entry.grid(row=self.row, column=1, sticky='nwe')
        self.row = self.row + 1
        return (entry, label)

    def create_entries(self):
        self.ent = self.make_entry('Find:', self.engine.patvar)[0]

    def make_frame(self, labeltext=None):
        if labeltext:
            label = Label(self.top, text=labeltext)
            label.grid(row=self.row, column=0, sticky='nw')
        else:
            label = ''
        frame = Frame(self.top)
        frame.grid(row=self.row, column=1, columnspan=1, sticky='nwe')
        self.row = self.row + 1
        return (frame, label)

    def create_option_buttons(self):
        frame = self.make_frame('Options')[0]
        engine = self.engine
        options = [(engine.revar, 'Regular expression'), (engine.casevar, 'Match case'), (engine.wordvar, 'Whole word')]
        if self.needwrapbutton:
            options.append((engine.wrapvar, 'Wrap around'))
        for var, label in options:
            btn = Checkbutton(frame, anchor='w', variable=var, text=label)
            btn.pack(side='left', fill='both')
            if var.get():
                btn.select()

        return (frame, options)

    def create_other_buttons(self):
        frame = self.make_frame('Direction')[0]
        var = self.engine.backvar
        others = [(1, 'Up'), (0, 'Down')]
        for val, label in others:
            btn = Radiobutton(frame, anchor='w', variable=var, value=val, text=label)
            btn.pack(side='left', fill='both')
            if var.get() == val:
                btn.select()

        return (frame, others)

    def make_button(self, label, command, isdef=0):
        b = Button(self.buttonframe, text=label, command=command, default=isdef and 'active' or 'normal')
        cols, rows = self.buttonframe.grid_size()
        b.grid(pady=1, row=rows, column=0, sticky='ew')
        self.buttonframe.grid(rowspan=rows + 1)
        return b

    def create_command_buttons(self):
        f = self.buttonframe = Frame(self.top)
        f.grid(row=0, column=2, padx=2, pady=2, ipadx=2, ipady=2)
        b = self.make_button('close', self.close)
        b.lower()


if __name__ == '__main__':
    import unittest
    unittest.main('idlelib.idle_test.test_searchdialogbase', verbosity=2)
