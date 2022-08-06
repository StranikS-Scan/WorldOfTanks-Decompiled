# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/macosxSupport.py
import sys
import Tkinter
from os import path
import warnings

def runningAsOSXApp():
    warnings.warn('runningAsOSXApp() is deprecated, use isAquaTk()', DeprecationWarning, stacklevel=2)
    return isAquaTk()


def isCarbonAquaTk(root):
    warnings.warn('isCarbonAquaTk(root) is deprecated, use isCarbonTk()', DeprecationWarning, stacklevel=2)
    return isCarbonTk()


_tk_type = None

def _initializeTkVariantTests(root):
    global _tk_type
    if sys.platform == 'darwin':
        ws = root.tk.call('tk', 'windowingsystem')
        if 'x11' in ws:
            _tk_type = 'xquartz'
        elif 'aqua' not in ws:
            _tk_type = 'other'
        elif 'AppKit' in root.tk.call('winfo', 'server', '.'):
            _tk_type = 'cocoa'
        else:
            _tk_type = 'carbon'
    else:
        _tk_type = 'other'


def isAquaTk():
    return _tk_type == 'cocoa' or _tk_type == 'carbon'


def isCarbonTk():
    return _tk_type == 'carbon'


def isCocoaTk():
    return _tk_type == 'cocoa'


def isXQuartz():
    return _tk_type == 'xquartz'


def tkVersionWarning(root):
    if isCocoaTk():
        patchlevel = root.tk.call('info', 'patchlevel')
        if patchlevel not in ('8.5.7', '8.5.9'):
            return False
        return 'WARNING: The version of Tcl/Tk ({0}) in use may be unstable.\\nVisit http://www.python.org/download/mac/tcltk/ for current information.'.format(patchlevel)
    else:
        return False


def addOpenEventSupport(root, flist):

    def doOpenFile(*args):
        for fn in args:
            flist.open(fn)

    root.createcommand('::tk::mac::OpenDocument', doOpenFile)


def hideTkConsole(root):
    try:
        root.tk.call('console', 'hide')
    except Tkinter.TclError:
        pass


def overrideRootMenu(root, flist):
    from Tkinter import Menu
    from idlelib import Bindings
    from idlelib import WindowList
    closeItem = Bindings.menudefs[0][1][-2]
    del Bindings.menudefs[0][1][-3:]
    Bindings.menudefs[0][1].insert(6, closeItem)
    del Bindings.menudefs[-1][1][0:2]
    del Bindings.menudefs[-2][1][0]
    menubar = Menu(root)
    root.configure(menu=menubar)
    menudict = {}
    menudict['windows'] = menu = Menu(menubar, name='windows', tearoff=0)
    menubar.add_cascade(label='Window', menu=menu, underline=0)

    def postwindowsmenu(menu=menu):
        end = menu.index('end')
        if end is None:
            end = -1
        if end > 0:
            menu.delete(0, end)
        WindowList.add_windows_to_menu(menu)
        return

    WindowList.register_callback(postwindowsmenu)

    def about_dialog(event=None):
        from idlelib import aboutDialog
        aboutDialog.AboutDialog(root, 'About IDLE')

    def config_dialog(event=None):
        from idlelib import configDialog
        root.instance_dict = flist.inversedict
        configDialog.ConfigDialog(root, 'Settings')

    def help_dialog(event=None):
        from idlelib import help
        help.show_idlehelp(root)

    root.bind('<<about-idle>>', about_dialog)
    root.bind('<<open-config-dialog>>', config_dialog)
    root.createcommand('::tk::mac::ShowPreferences', config_dialog)
    if flist:
        root.bind('<<close-all-windows>>', flist.close_all_callback)
        root.createcommand('exit', flist.close_all_callback)
    if isCarbonTk():
        menudict['application'] = menu = Menu(menubar, name='apple', tearoff=0)
        menubar.add_cascade(label='IDLE', menu=menu)
        Bindings.menudefs.insert(0, ('application', [('About IDLE', '<<about-idle>>'), None]))
        tkversion = root.tk.eval('info patchlevel')
        if tuple(map(int, tkversion.split('.'))) < (8, 4, 14):
            Bindings.menudefs[0][1].append(('_Preferences....', '<<open-config-dialog>>'))
    if isCocoaTk():
        root.createcommand('tkAboutDialog', about_dialog)
        root.createcommand('::tk::mac::ShowHelp', help_dialog)
        del Bindings.menudefs[-1][1][0]
    return


def setupApp(root, flist):
    _initializeTkVariantTests(root)
    if isAquaTk():
        hideTkConsole(root)
        overrideRootMenu(root, flist)
        addOpenEventSupport(root, flist)
