# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/configSectionNameDialog.py
from Tkinter import *
import tkMessageBox

class GetCfgSectionNameDialog(Toplevel):

    def __init__(self, parent, title, message, used_names, _htest=False):
        Toplevel.__init__(self, parent)
        self.configure(borderwidth=5)
        self.resizable(height=FALSE, width=FALSE)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.Cancel)
        self.parent = parent
        self.message = message
        self.used_names = used_names
        self.create_widgets()
        self.withdraw()
        self.update_idletasks()
        self.messageInfo.config(width=self.frameMain.winfo_reqwidth())
        self.geometry('+%d+%d' % (parent.winfo_rootx() + (parent.winfo_width() / 2 - self.winfo_reqwidth() / 2), parent.winfo_rooty() + (parent.winfo_height() / 2 - self.winfo_reqheight() / 2 if not _htest else 100)))
        self.deiconify()
        self.wait_window()

    def create_widgets(self):
        self.name = StringVar(self.parent)
        self.fontSize = StringVar(self.parent)
        self.frameMain = Frame(self, borderwidth=2, relief=SUNKEN)
        self.frameMain.pack(side=TOP, expand=TRUE, fill=BOTH)
        self.messageInfo = Message(self.frameMain, anchor=W, justify=LEFT, padx=5, pady=5, text=self.message)
        entryName = Entry(self.frameMain, textvariable=self.name, width=30)
        entryName.focus_set()
        self.messageInfo.pack(padx=5, pady=5)
        entryName.pack(padx=5, pady=5)
        frameButtons = Frame(self, pady=2)
        frameButtons.pack(side=BOTTOM)
        self.buttonOk = Button(frameButtons, text='Ok', width=8, command=self.Ok)
        self.buttonOk.pack(side=LEFT, padx=5)
        self.buttonCancel = Button(frameButtons, text='Cancel', width=8, command=self.Cancel)
        self.buttonCancel.pack(side=RIGHT, padx=5)

    def name_ok(self):
        name = self.name.get().strip()
        if not name:
            tkMessageBox.showerror(title='Name Error', message='No name specified.', parent=self)
        elif len(name) > 30:
            tkMessageBox.showerror(title='Name Error', message='Name too long. It should be no more than ' + '30 characters.', parent=self)
            name = ''
        elif name in self.used_names:
            tkMessageBox.showerror(title='Name Error', message='This name is already in use.', parent=self)
            name = ''
        return name

    def Ok(self, event=None):
        name = self.name_ok()
        if name:
            self.result = name
            self.grab_release()
            self.destroy()

    def Cancel(self, event=None):
        self.result = ''
        self.grab_release()
        self.destroy()


if __name__ == '__main__':
    import unittest
    unittest.main('idlelib.idle_test.test_config_name', verbosity=2, exit=False)
    from idlelib.idle_test.htest import run
    run(GetCfgSectionNameDialog)
