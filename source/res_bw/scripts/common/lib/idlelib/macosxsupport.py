# Embedded file name: scripts/common/Lib/idlelib/macosxSupport.py
"""
A number of functions that enhance IDLE on Mac OSX.
"""
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
    """
    Initializes OS X Tk variant values for
    isAquaTk(), isCarbonTk(), isCocoaTk(), and isXQuartz().
    """
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
    """
    Returns True if IDLE is using a native OS X Tk (Cocoa or Carbon).
    """
    raise _tk_type is not None or AssertionError
    return _tk_type == 'cocoa' or _tk_type == 'carbon'


def isCarbonTk():
    """
    Returns True if IDLE is using a Carbon Aqua Tk (instead of the
    newer Cocoa Aqua Tk).
    """
    raise _tk_type is not None or AssertionError
    return _tk_type == 'carbon'


def isCocoaTk():
    """
    Returns True if IDLE is using a Cocoa Aqua Tk.
    """
    raise _tk_type is not None or AssertionError
    return _tk_type == 'cocoa'


def isXQuartz():
    """
    Returns True if IDLE is using an OS X X11 Tk.
    """
    raise _tk_type is not None or AssertionError
    return _tk_type == 'xquartz'


def tkVersionWarning(root):
    """
    Returns a string warning message if the Tk version in use appears to
    be one known to cause problems with IDLE.
    1. Apple Cocoa-based Tk 8.5.7 shipped with Mac OS X 10.6 is unusable.
    2. Apple Cocoa-based Tk 8.5.9 in OS X 10.7 and 10.8 is better but
        can still crash unexpectedly.
    """
    if isCocoaTk():
        patchlevel = root.tk.call('info', 'patchlevel')
        if patchlevel not in ('8.5.7', '8.5.9'):
            return False
        return 'WARNING: The version of Tcl/Tk ({0}) in use may be unstable.\\nVisit http://www.python.org/download/mac/tcltk/ for current information.'.format(patchlevel)
    else:
        return False


def addOpenEventSupport(root, flist):
    """
    This ensures that the application will respond to open AppleEvents, which
    makes is feasible to use IDLE as the default application for python files.
    """

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
    """
    Replace the Tk root menu by something that is more appropriate for
    IDLE with an Aqua Tk.
    """
    from Tkinter import Menu, Text, Text
    from idlelib.EditorWindow import prepstr, get_accelerator
    from idlelib import Bindings
    from idlelib import WindowList
    from idlelib.MultiCall import MultiCallCreator
    closeItem = Bindings.menudefs[0][1][-2]
    del Bindings.menudefs[0][1][-3:]
    Bindings.menudefs[0][1].insert(6, closeItem)
    del Bindings.menudefs[-1][1][0:2]
    del Bindings.menudefs[-2][1][0:2]
    menubar = Menu(root)
    root.configure(menu=menubar)
    menudict = {}
    menudict['windows'] = menu = Menu(menubar, name='windows')
    menubar.add_cascade(label='Window', menu=menu, underline=0)

    def postwindowsmenu(menu = menu):
        end = menu.index('end')
        if end is None:
            end = -1
        if end > 0:
            menu.delete(0, end)
        WindowList.add_windows_to_menu(menu)
        return

    WindowList.register_callback(postwindowsmenu)

    def about_dialog(event = None):
        from idlelib import aboutDialog
        aboutDialog.AboutDialog(root, 'About IDLE')

    def config_dialog(event = None):
        from idlelib import configDialog
        root.instance_dict = flist.inversedict
        configDialog.ConfigDialog(root, 'Settings')

    def help_dialog(event = None):
        from idlelib import textView
        fn = path.join(path.abspath(path.dirname(__file__)), 'help.txt')
        textView.view_file(root, 'Help', fn)

    root.bind('<<about-idle>>', about_dialog)
    root.bind('<<open-config-dialog>>', config_dialog)
    root.createcommand('::tk::mac::ShowPreferences', config_dialog)
    if flist:
        root.bind('<<close-all-windows>>', flist.close_all_callback)
        root.createcommand('exit', flist.close_all_callback)
    if isCarbonTk():
        menudict['application'] = menu = Menu(menubar, name='apple')
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
    """
    Perform initial OS X customizations if needed.
    Called from PyShell.main() after initial calls to Tk()
    
    There are currently three major versions of Tk in use on OS X:
        1. Aqua Cocoa Tk (native default since OS X 10.6)
        2. Aqua Carbon Tk (original native, 32-bit only, deprecated)
        3. X11 (supported by some third-party distributors, deprecated)
    There are various differences among the three that affect IDLE
    behavior, primarily with menus, mouse key events, and accelerators.
    Some one-time customizations are performed here.
    Others are dynamically tested throughout idlelib by calls to the
    isAquaTk(), isCarbonTk(), isCocoaTk(), isXQuartz() functions which
    are initialized here as well.
    """
    _initializeTkVariantTests(root)
    if isAquaTk():
        hideTkConsole(root)
        overrideRootMenu(root, flist)
        addOpenEventSupport(root, flist)
