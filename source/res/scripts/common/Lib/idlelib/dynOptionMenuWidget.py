# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/dynOptionMenuWidget.py
import copy
from Tkinter import OptionMenu, _setit, StringVar, Button

class DynOptionMenu(OptionMenu):

    def __init__(self, master, variable, value, *values, **kwargs):
        kwargsCopy = copy.copy(kwargs)
        if 'highlightthickness' in kwargs.keys():
            del kwargs['highlightthickness']
        OptionMenu.__init__(self, master, variable, value, *values, **kwargs)
        self.config(highlightthickness=kwargsCopy.get('highlightthickness'))
        self.variable = variable
        self.command = kwargs.get('command')

    def SetMenu(self, valueList, value=None):
        self['menu'].delete(0, 'end')
        for item in valueList:
            self['menu'].add_command(label=item, command=_setit(self.variable, item, self.command))

        if value:
            self.variable.set(value)


def _dyn_option_menu(parent):
    from Tkinter import Toplevel
    top = Toplevel()
    top.title('Tets dynamic option menu')
    top.geometry('200x100+%d+%d' % (parent.winfo_rootx() + 200, parent.winfo_rooty() + 150))
    top.focus_set()
    var = StringVar(top)
    var.set('Old option set')
    dyn = DynOptionMenu(top, var, 'old1', 'old2', 'old3', 'old4')
    dyn.pack()

    def update():
        dyn.SetMenu(['new1',
         'new2',
         'new3',
         'new4'], value='new option set')

    button = Button(top, text='Change option set', command=update)
    button.pack()


if __name__ == '__main__':
    from idlelib.idle_test.htest import run
    run(_dyn_option_menu)
