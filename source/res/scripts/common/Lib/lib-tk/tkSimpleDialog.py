# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib-tk/tkSimpleDialog.py
from Tkinter import *

class Dialog(Toplevel):

    def __init__(self, parent, title=None):
        Toplevel.__init__(self, parent)
        self.withdraw()
        if parent.winfo_viewable():
            self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol('WM_DELETE_WINDOW', self.cancel)
        if self.parent is not None:
            self.geometry('+%d+%d' % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.deiconify()
        self.initial_focus.focus_set()
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)
        return

    def destroy(self):
        self.initial_focus = None
        Toplevel.destroy(self)
        return

    def body(self, master):
        pass

    def buttonbox(self):
        box = Frame(self)
        w = Button(box, text='OK', width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text='Cancel', width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)
        box.pack()

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()
        try:
            self.apply()
        finally:
            self.cancel()

    def cancel(self, event=None):
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()
        return

    def validate(self):
        pass

    def apply(self):
        pass


class _QueryDialog(Dialog):

    def __init__(self, title, prompt, initialvalue=None, minvalue=None, maxvalue=None, parent=None):
        if not parent:
            import Tkinter
            parent = Tkinter._default_root
        self.prompt = prompt
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.initialvalue = initialvalue
        Dialog.__init__(self, parent, title)

    def destroy(self):
        self.entry = None
        Dialog.destroy(self)
        return

    def body(self, master):
        w = Label(master, text=self.prompt, justify=LEFT)
        w.grid(row=0, padx=5, sticky=W)
        self.entry = Entry(master, name='entry')
        self.entry.grid(row=1, padx=5, sticky=W + E)
        if self.initialvalue is not None:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, END)
        return self.entry

    def validate(self):
        import tkMessageBox
        try:
            result = self.getresult()
        except ValueError:
            tkMessageBox.showwarning('Illegal value', self.errormessage + '\nPlease try again', parent=self)
            return 0

        if self.minvalue is not None and result < self.minvalue:
            tkMessageBox.showwarning('Too small', 'The allowed minimum value is %s. Please try again.' % self.minvalue, parent=self)
            return 0
        elif self.maxvalue is not None and result > self.maxvalue:
            tkMessageBox.showwarning('Too large', 'The allowed maximum value is %s. Please try again.' % self.maxvalue, parent=self)
            return 0
        else:
            self.result = result
            return 1


class _QueryInteger(_QueryDialog):
    errormessage = 'Not an integer.'

    def getresult(self):
        return int(self.entry.get())


def askinteger(title, prompt, **kw):
    d = _QueryInteger(title, prompt, **kw)
    return d.result


class _QueryFloat(_QueryDialog):
    errormessage = 'Not a floating point value.'

    def getresult(self):
        return float(self.entry.get())


def askfloat(title, prompt, **kw):
    d = _QueryFloat(title, prompt, **kw)
    return d.result


class _QueryString(_QueryDialog):

    def __init__(self, *args, **kw):
        if 'show' in kw:
            self.__show = kw['show']
            del kw['show']
        else:
            self.__show = None
        _QueryDialog.__init__(self, *args, **kw)
        return

    def body(self, master):
        entry = _QueryDialog.body(self, master)
        if self.__show is not None:
            entry.configure(show=self.__show)
        return entry

    def getresult(self):
        return self.entry.get()


def askstring(title, prompt, **kw):
    d = _QueryString(title, prompt, **kw)
    return d.result


if __name__ == '__main__':
    root = Tk()
    root.update()
    print askinteger('Spam', 'Egg count', initialvalue=144)
    print askfloat('Spam', 'Egg weight\n(in tons)', minvalue=1, maxvalue=100)
    print askstring('Spam', 'Egg label')
