# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/EasyDialogs.py
from warnings import warnpy3k
warnpy3k('In 3.x, the EasyDialogs module is removed.', stacklevel=2)
from Carbon.Dlg import GetNewDialog, SetDialogItemText, GetDialogItemText, ModalDialog
from Carbon import Qd
from Carbon import QuickDraw
from Carbon import Dialogs
from Carbon import Windows
from Carbon import Dlg, Win, Evt, Events
from Carbon import Ctl
from Carbon import Controls
from Carbon import Menu
from Carbon import AE
import Nav
import MacOS
import string
from Carbon.ControlAccessor import *
import Carbon.File
import macresource
import os
import sys
__all__ = ['Message',
 'AskString',
 'AskPassword',
 'AskYesNoCancel',
 'GetArgv',
 'AskFileForOpen',
 'AskFileForSave',
 'AskFolder',
 'ProgressBar']
_initialized = 0

def _initialize():
    global _initialized
    if _initialized:
        return
    macresource.need('DLOG', 260, 'dialogs.rsrc', __name__)


def _interact():
    AE.AEInteractWithUser(50000000)


def cr2lf(text):
    if '\r' in text:
        text = string.join(string.split(text, '\r'), '\n')
    return text


def lf2cr(text):
    if '\n' in text:
        text = string.join(string.split(text, '\n'), '\r')
    if len(text) > 253:
        text = text[:253] + '\xc9'
    return text


def Message(msg, id=260, ok=None):
    _initialize()
    _interact()
    d = GetNewDialog(id, -1)
    if not d:
        print "EasyDialogs: Can't get DLOG resource with id =", id, ' (missing resource file?)'
        return
    else:
        h = d.GetDialogItemAsControl(2)
        SetDialogItemText(h, lf2cr(msg))
        if ok is not None:
            h = d.GetDialogItemAsControl(1)
            h.SetControlTitle(ok)
        d.SetDialogDefaultItem(1)
        d.AutoSizeDialog()
        d.GetDialogWindow().ShowWindow()
        while 1:
            n = ModalDialog(None)
            if n == 1:
                return

        return


def AskString(prompt, default='', id=261, ok=None, cancel=None):
    _initialize()
    _interact()
    d = GetNewDialog(id, -1)
    if not d:
        print "EasyDialogs: Can't get DLOG resource with id =", id, ' (missing resource file?)'
        return
    else:
        h = d.GetDialogItemAsControl(3)
        SetDialogItemText(h, lf2cr(prompt))
        h = d.GetDialogItemAsControl(4)
        SetDialogItemText(h, lf2cr(default))
        d.SelectDialogItemText(4, 0, 999)
        if ok is not None:
            h = d.GetDialogItemAsControl(1)
            h.SetControlTitle(ok)
        if cancel is not None:
            h = d.GetDialogItemAsControl(2)
            h.SetControlTitle(cancel)
        d.SetDialogDefaultItem(1)
        d.SetDialogCancelItem(2)
        d.AutoSizeDialog()
        d.GetDialogWindow().ShowWindow()
        while 1:
            n = ModalDialog(None)
            if n == 1:
                h = d.GetDialogItemAsControl(4)
                return cr2lf(GetDialogItemText(h))
            if n == 2:
                return

        return


def AskPassword(prompt, default='', id=264, ok=None, cancel=None):
    _initialize()
    _interact()
    d = GetNewDialog(id, -1)
    if not d:
        print "EasyDialogs: Can't get DLOG resource with id =", id, ' (missing resource file?)'
        return
    else:
        h = d.GetDialogItemAsControl(3)
        SetDialogItemText(h, lf2cr(prompt))
        pwd = d.GetDialogItemAsControl(4)
        bullets = '\xa5' * len(default)
        SetControlData(pwd, kControlEditTextPart, kControlEditTextPasswordTag, default)
        d.SelectDialogItemText(4, 0, 999)
        Ctl.SetKeyboardFocus(d.GetDialogWindow(), pwd, kControlEditTextPart)
        if ok is not None:
            h = d.GetDialogItemAsControl(1)
            h.SetControlTitle(ok)
        if cancel is not None:
            h = d.GetDialogItemAsControl(2)
            h.SetControlTitle(cancel)
        d.SetDialogDefaultItem(Dialogs.ok)
        d.SetDialogCancelItem(Dialogs.cancel)
        d.AutoSizeDialog()
        d.GetDialogWindow().ShowWindow()
        while 1:
            n = ModalDialog(None)
            if n == 1:
                h = d.GetDialogItemAsControl(4)
                return cr2lf(GetControlData(pwd, kControlEditTextPart, kControlEditTextPasswordTag))
            if n == 2:
                return

        return


def AskYesNoCancel(question, default=0, yes=None, no=None, cancel=None, id=262):
    _initialize()
    _interact()
    d = GetNewDialog(id, -1)
    if not d:
        print "EasyDialogs: Can't get DLOG resource with id =", id, ' (missing resource file?)'
        return
    else:
        h = d.GetDialogItemAsControl(5)
        SetDialogItemText(h, lf2cr(question))
        if yes is not None:
            if yes == '':
                d.HideDialogItem(2)
            else:
                h = d.GetDialogItemAsControl(2)
                h.SetControlTitle(yes)
        if no is not None:
            if no == '':
                d.HideDialogItem(3)
            else:
                h = d.GetDialogItemAsControl(3)
                h.SetControlTitle(no)
        if cancel is not None:
            if cancel == '':
                d.HideDialogItem(4)
            else:
                h = d.GetDialogItemAsControl(4)
                h.SetControlTitle(cancel)
        d.SetDialogCancelItem(4)
        if default == 1:
            d.SetDialogDefaultItem(2)
        elif default == 0:
            d.SetDialogDefaultItem(3)
        elif default == -1:
            d.SetDialogDefaultItem(4)
        d.AutoSizeDialog()
        d.GetDialogWindow().ShowWindow()
        while 1:
            n = ModalDialog(None)
            if n == 1:
                return default
            if n == 2:
                return 1
            if n == 3:
                return 0
            if n == 4:
                return -1

        return


try:
    screenbounds = Qd.GetQDGlobalsScreenBits().bounds
except AttributeError:
    raise ImportError('QuickDraw APIs not available')

screenbounds = (screenbounds[0] + 4,
 screenbounds[1] + 4,
 screenbounds[2] - 4,
 screenbounds[3] - 4)
kControlProgressBarIndeterminateTag = 'inde'

class ProgressBar:

    def __init__(self, title='Working...', maxval=0, label='', id=263):
        self.w = None
        self.d = None
        _initialize()
        self.d = GetNewDialog(id, -1)
        self.w = self.d.GetDialogWindow()
        self.label(label)
        self.title(title)
        self.set(0, maxval)
        self.d.AutoSizeDialog()
        self.w.ShowWindow()
        self.d.DrawDialog()
        return

    def __del__(self):
        if self.w:
            self.w.BringToFront()
            self.w.HideWindow()
        del self.w
        del self.d

    def title(self, newstr=''):
        self.w.BringToFront()
        self.w.SetWTitle(newstr)

    def label(self, *newstr):
        self.w.BringToFront()
        if newstr:
            self._label = lf2cr(newstr[0])
        text_h = self.d.GetDialogItemAsControl(2)
        SetDialogItemText(text_h, self._label)

    def _update(self, value):
        maxval = self.maxval
        if maxval == 0:
            Ctl.IdleControls(self.w)
        else:
            if maxval > 32767:
                value = int(value / (maxval / 32767.0))
                maxval = 32767
            maxval = int(maxval)
            value = int(value)
            progbar = self.d.GetDialogItemAsControl(3)
            progbar.SetControlMaximum(maxval)
            progbar.SetControlValue(value)
        ready, ev = Evt.WaitNextEvent(Events.mDownMask, 1)
        if ready:
            what, msg, when, where, mod = ev
            part = Win.FindWindow(where)[0]
            if Dlg.IsDialogEvent(ev):
                ds = Dlg.DialogSelect(ev)
                if ds[0] and ds[1] == self.d and ds[-1] == 1:
                    self.w.HideWindow()
                    self.w = None
                    self.d = None
                    raise KeyboardInterrupt, ev
            elif part == 4:
                self.w.DragWindow(where, screenbounds)
            else:
                MacOS.HandleEvent(ev)
        return

    def set(self, value, max=None):
        if max is not None:
            self.maxval = max
            bar = self.d.GetDialogItemAsControl(3)
            if max <= 0:
                bar.SetControlData(0, kControlProgressBarIndeterminateTag, '\x01')
            else:
                bar.SetControlData(0, kControlProgressBarIndeterminateTag, '\x00')
        if value < 0:
            value = 0
        elif value > self.maxval:
            value = self.maxval
        self.curval = value
        self._update(value)
        return

    def inc(self, n=1):
        self.set(self.curval + n)


ARGV_ID = 265
ARGV_ITEM_OK = 1
ARGV_ITEM_CANCEL = 2
ARGV_OPTION_GROUP = 3
ARGV_OPTION_EXPLAIN = 4
ARGV_OPTION_VALUE = 5
ARGV_OPTION_ADD = 6
ARGV_COMMAND_GROUP = 7
ARGV_COMMAND_EXPLAIN = 8
ARGV_COMMAND_ADD = 9
ARGV_ADD_OLDFILE = 10
ARGV_ADD_NEWFILE = 11
ARGV_ADD_FOLDER = 12
ARGV_CMDLINE_GROUP = 13
ARGV_CMDLINE_DATA = 14

def _setmenu(control, items):
    mhandle = control.GetControlData_Handle(Controls.kControlMenuPart, Controls.kControlPopupButtonMenuHandleTag)
    menu = Menu.as_Menu(mhandle)
    for item in items:
        if type(item) == type(()):
            label = item[0]
        else:
            label = item
        if label[-1] == '=' or label[-1] == ':':
            label = label[:-1]
        menu.AppendMenu(label)

    control.SetControlMinimum(1)
    control.SetControlMaximum(len(items) + 1)


def _selectoption(d, optionlist, idx):
    if idx < 0 or idx >= len(optionlist):
        MacOS.SysBeep()
        return
    option = optionlist[idx]
    if type(option) == type(()):
        if len(option) == 4:
            help = option[2]
        elif len(option) > 1:
            help = option[-1]
        else:
            help = ''
    else:
        help = ''
    h = d.GetDialogItemAsControl(ARGV_OPTION_EXPLAIN)
    if help and len(help) > 250:
        help = help[:250] + '...'
    Dlg.SetDialogItemText(h, help)
    hasvalue = 0
    if type(option) == type(()):
        label = option[0]
    else:
        label = option
    if label[-1] == '=' or label[-1] == ':':
        hasvalue = 1
    h = d.GetDialogItemAsControl(ARGV_OPTION_VALUE)
    Dlg.SetDialogItemText(h, '')
    if hasvalue:
        d.ShowDialogItem(ARGV_OPTION_VALUE)
        d.SelectDialogItemText(ARGV_OPTION_VALUE, 0, 0)
    else:
        d.HideDialogItem(ARGV_OPTION_VALUE)


def GetArgv(optionlist=None, commandlist=None, addoldfile=1, addnewfile=1, addfolder=1, id=ARGV_ID):
    _initialize()
    _interact()
    d = GetNewDialog(id, -1)
    if not d:
        print "EasyDialogs: Can't get DLOG resource with id =", id, ' (missing resource file?)'
        return
    else:
        if optionlist:
            _setmenu(d.GetDialogItemAsControl(ARGV_OPTION_GROUP), optionlist)
            _selectoption(d, optionlist, 0)
        else:
            d.GetDialogItemAsControl(ARGV_OPTION_GROUP).DeactivateControl()
        if commandlist:
            _setmenu(d.GetDialogItemAsControl(ARGV_COMMAND_GROUP), commandlist)
            if type(commandlist[0]) == type(()) and len(commandlist[0]) > 1:
                help = commandlist[0][-1]
                h = d.GetDialogItemAsControl(ARGV_COMMAND_EXPLAIN)
                Dlg.SetDialogItemText(h, help)
        else:
            d.GetDialogItemAsControl(ARGV_COMMAND_GROUP).DeactivateControl()
        if not addoldfile:
            d.GetDialogItemAsControl(ARGV_ADD_OLDFILE).DeactivateControl()
        if not addnewfile:
            d.GetDialogItemAsControl(ARGV_ADD_NEWFILE).DeactivateControl()
        if not addfolder:
            d.GetDialogItemAsControl(ARGV_ADD_FOLDER).DeactivateControl()
        d.SetDialogDefaultItem(ARGV_ITEM_OK)
        d.SetDialogCancelItem(ARGV_ITEM_CANCEL)
        d.GetDialogWindow().ShowWindow()
        d.DrawDialog()
        if hasattr(MacOS, 'SchedParams'):
            appsw = MacOS.SchedParams(1, 0)
        try:
            while 1:
                stringstoadd = []
                n = ModalDialog(None)
                if n == ARGV_ITEM_OK:
                    break
                elif n == ARGV_ITEM_CANCEL:
                    raise SystemExit
                elif n == ARGV_OPTION_GROUP:
                    idx = d.GetDialogItemAsControl(ARGV_OPTION_GROUP).GetControlValue() - 1
                    _selectoption(d, optionlist, idx)
                elif n == ARGV_OPTION_VALUE:
                    pass
                elif n == ARGV_OPTION_ADD:
                    idx = d.GetDialogItemAsControl(ARGV_OPTION_GROUP).GetControlValue() - 1
                    if 0 <= idx < len(optionlist):
                        option = optionlist[idx]
                        if type(option) == type(()):
                            option = option[0]
                        if option[-1] == '=' or option[-1] == ':':
                            option = option[:-1]
                            h = d.GetDialogItemAsControl(ARGV_OPTION_VALUE)
                            value = Dlg.GetDialogItemText(h)
                        else:
                            value = ''
                        if len(option) == 1:
                            stringtoadd = '-' + option
                        else:
                            stringtoadd = '--' + option
                        stringstoadd = [stringtoadd]
                        if value:
                            stringstoadd.append(value)
                    else:
                        MacOS.SysBeep()
                elif n == ARGV_COMMAND_GROUP:
                    idx = d.GetDialogItemAsControl(ARGV_COMMAND_GROUP).GetControlValue() - 1
                    if 0 <= idx < len(commandlist) and type(commandlist[idx]) == type(()) and len(commandlist[idx]) > 1:
                        help = commandlist[idx][-1]
                        h = d.GetDialogItemAsControl(ARGV_COMMAND_EXPLAIN)
                        Dlg.SetDialogItemText(h, help)
                elif n == ARGV_COMMAND_ADD:
                    idx = d.GetDialogItemAsControl(ARGV_COMMAND_GROUP).GetControlValue() - 1
                    if 0 <= idx < len(commandlist):
                        command = commandlist[idx]
                        if type(command) == type(()):
                            command = command[0]
                        stringstoadd = [command]
                    else:
                        MacOS.SysBeep()
                elif n == ARGV_ADD_OLDFILE:
                    pathname = AskFileForOpen()
                    if pathname:
                        stringstoadd = [pathname]
                elif n == ARGV_ADD_NEWFILE:
                    pathname = AskFileForSave()
                    if pathname:
                        stringstoadd = [pathname]
                elif n == ARGV_ADD_FOLDER:
                    pathname = AskFolder()
                    if pathname:
                        stringstoadd = [pathname]
                elif n == ARGV_CMDLINE_DATA:
                    pass
                else:
                    raise RuntimeError, 'Unknown dialog item %d' % n
                for stringtoadd in stringstoadd:
                    if '"' in stringtoadd or "'" in stringtoadd or ' ' in stringtoadd:
                        stringtoadd = repr(stringtoadd)
                    h = d.GetDialogItemAsControl(ARGV_CMDLINE_DATA)
                    oldstr = GetDialogItemText(h)
                    if oldstr and oldstr[-1] != ' ':
                        oldstr = oldstr + ' '
                    oldstr = oldstr + stringtoadd
                    if oldstr[-1] != ' ':
                        oldstr = oldstr + ' '
                    SetDialogItemText(h, oldstr)
                    d.SelectDialogItemText(ARGV_CMDLINE_DATA, 32767, 32767)

            h = d.GetDialogItemAsControl(ARGV_CMDLINE_DATA)
            oldstr = GetDialogItemText(h)
            tmplist = string.split(oldstr)
            newlist = []
            while tmplist:
                item = tmplist[0]
                del tmplist[0]
                if item[0] == '"':
                    while item[-1] != '"':
                        if not tmplist:
                            raise RuntimeError, 'Unterminated quoted argument'
                        item = item + ' ' + tmplist[0]
                        del tmplist[0]

                    item = item[1:-1]
                if item[0] == "'":
                    while item[-1] != "'":
                        if not tmplist:
                            raise RuntimeError, 'Unterminated quoted argument'
                        item = item + ' ' + tmplist[0]
                        del tmplist[0]

                    item = item[1:-1]
                newlist.append(item)

            return newlist
        finally:
            if hasattr(MacOS, 'SchedParams'):
                MacOS.SchedParams(*appsw)
            del d

        return


def _process_Nav_args(dftflags, **args):
    import Carbon.AppleEvents
    import Carbon.AE
    import Carbon.File
    for k in args.keys():
        if args[k] is None:
            del args[k]

    if 'dialogOptionFlags' not in args:
        args['dialogOptionFlags'] = dftflags
    if 'defaultLocation' in args and not isinstance(args['defaultLocation'], Carbon.AE.AEDesc):
        defaultLocation = args['defaultLocation']
        if isinstance(defaultLocation, Carbon.File.FSSpec):
            args['defaultLocation'] = Carbon.AE.AECreateDesc(Carbon.AppleEvents.typeFSS, defaultLocation.data)
        else:
            if not isinstance(defaultLocation, Carbon.File.FSRef):
                defaultLocation = Carbon.File.FSRef(defaultLocation)
            args['defaultLocation'] = Carbon.AE.AECreateDesc(Carbon.AppleEvents.typeFSRef, defaultLocation.data)
    if 'typeList' in args and not isinstance(args['typeList'], Carbon.Res.ResourceType):
        typeList = args['typeList'][:]
        if 'TEXT' in typeList and '\x00\x00\x00\x00' not in typeList:
            typeList = typeList + ('\x00\x00\x00\x00',)
        data = 'Pyth' + struct.pack('hh', 0, len(typeList))
        for type in typeList:
            data = data + type

        args['typeList'] = Carbon.Res.Handle(data)
    tpwanted = str
    if 'wanted' in args:
        tpwanted = args['wanted']
        del args['wanted']
    return (args, tpwanted)


def _dummy_Nav_eventproc(msg, data):
    pass


_default_Nav_eventproc = _dummy_Nav_eventproc

def SetDefaultEventProc(proc):
    global _default_Nav_eventproc
    rv = _default_Nav_eventproc
    if proc is None:
        proc = _dummy_Nav_eventproc
    _default_Nav_eventproc = proc
    return rv


def AskFileForOpen(message=None, typeList=None, version=None, defaultLocation=None, dialogOptionFlags=None, location=None, clientName=None, windowTitle=None, actionButtonLabel=None, cancelButtonLabel=None, preferenceKey=None, popupExtension=None, eventProc=_dummy_Nav_eventproc, previewProc=None, filterProc=None, wanted=None, multiple=None):
    default_flags = 86
    args, tpwanted = _process_Nav_args(default_flags, version=version, defaultLocation=defaultLocation, dialogOptionFlags=dialogOptionFlags, location=location, clientName=clientName, windowTitle=windowTitle, actionButtonLabel=actionButtonLabel, cancelButtonLabel=cancelButtonLabel, message=message, preferenceKey=preferenceKey, popupExtension=popupExtension, eventProc=eventProc, previewProc=previewProc, filterProc=filterProc, typeList=typeList, wanted=wanted, multiple=multiple)
    _interact()
    try:
        rr = Nav.NavChooseFile(args)
        good = 1
    except Nav.error as arg:
        if arg[0] != -128:
            raise Nav.error, arg
        return None

    if not rr.validRecord or not rr.selection:
        return None
    elif issubclass(tpwanted, Carbon.File.FSRef):
        return tpwanted(rr.selection_fsr[0])
    elif issubclass(tpwanted, Carbon.File.FSSpec):
        return tpwanted(rr.selection[0])
    elif issubclass(tpwanted, str):
        return tpwanted(rr.selection_fsr[0].as_pathname())
    elif issubclass(tpwanted, unicode):
        return tpwanted(rr.selection_fsr[0].as_pathname(), 'utf8')
    else:
        raise TypeError, "Unknown value for argument 'wanted': %s" % repr(tpwanted)
        return None


def AskFileForSave(message=None, savedFileName=None, version=None, defaultLocation=None, dialogOptionFlags=None, location=None, clientName=None, windowTitle=None, actionButtonLabel=None, cancelButtonLabel=None, preferenceKey=None, popupExtension=None, eventProc=_dummy_Nav_eventproc, fileType=None, fileCreator=None, wanted=None, multiple=None):
    default_flags = 7
    args, tpwanted = _process_Nav_args(default_flags, version=version, defaultLocation=defaultLocation, dialogOptionFlags=dialogOptionFlags, location=location, clientName=clientName, windowTitle=windowTitle, actionButtonLabel=actionButtonLabel, cancelButtonLabel=cancelButtonLabel, savedFileName=savedFileName, message=message, preferenceKey=preferenceKey, popupExtension=popupExtension, eventProc=eventProc, fileType=fileType, fileCreator=fileCreator, wanted=wanted, multiple=multiple)
    _interact()
    try:
        rr = Nav.NavPutFile(args)
        good = 1
    except Nav.error as arg:
        if arg[0] != -128:
            raise Nav.error, arg
        return None

    if not rr.validRecord or not rr.selection:
        return None
    else:
        if issubclass(tpwanted, Carbon.File.FSRef):
            raise TypeError, 'Cannot pass wanted=FSRef to AskFileForSave'
        if issubclass(tpwanted, Carbon.File.FSSpec):
            return tpwanted(rr.selection[0])
        if issubclass(tpwanted, (str, unicode)):
            vrefnum, dirid, name = rr.selection[0].as_tuple()
            pardir_fss = Carbon.File.FSSpec((vrefnum, dirid, ''))
            pardir_fsr = Carbon.File.FSRef(pardir_fss)
            pardir_path = pardir_fsr.FSRefMakePath()
            name_utf8 = unicode(name, 'macroman').encode('utf8')
            fullpath = os.path.join(pardir_path, name_utf8)
            if issubclass(tpwanted, unicode):
                return unicode(fullpath, 'utf8')
            return tpwanted(fullpath)
        raise TypeError, "Unknown value for argument 'wanted': %s" % repr(tpwanted)
        return None


def AskFolder(message=None, version=None, defaultLocation=None, dialogOptionFlags=None, location=None, clientName=None, windowTitle=None, actionButtonLabel=None, cancelButtonLabel=None, preferenceKey=None, popupExtension=None, eventProc=_dummy_Nav_eventproc, filterProc=None, wanted=None, multiple=None):
    default_flags = 23
    args, tpwanted = _process_Nav_args(default_flags, version=version, defaultLocation=defaultLocation, dialogOptionFlags=dialogOptionFlags, location=location, clientName=clientName, windowTitle=windowTitle, actionButtonLabel=actionButtonLabel, cancelButtonLabel=cancelButtonLabel, message=message, preferenceKey=preferenceKey, popupExtension=popupExtension, eventProc=eventProc, filterProc=filterProc, wanted=wanted, multiple=multiple)
    _interact()
    try:
        rr = Nav.NavChooseFolder(args)
        good = 1
    except Nav.error as arg:
        if arg[0] != -128:
            raise Nav.error, arg
        return None

    if not rr.validRecord or not rr.selection:
        return None
    elif issubclass(tpwanted, Carbon.File.FSRef):
        return tpwanted(rr.selection_fsr[0])
    elif issubclass(tpwanted, Carbon.File.FSSpec):
        return tpwanted(rr.selection[0])
    elif issubclass(tpwanted, str):
        return tpwanted(rr.selection_fsr[0].as_pathname())
    elif issubclass(tpwanted, unicode):
        return tpwanted(rr.selection_fsr[0].as_pathname(), 'utf8')
    else:
        raise TypeError, "Unknown value for argument 'wanted': %s" % repr(tpwanted)
        return None


def test():
    import time
    Message('Testing EasyDialogs.')
    optionlist = (('v', 'Verbose'),
     ('verbose', 'Verbose as long option'),
     ('flags=', 'Valued option'),
     ('f:', 'Short valued option'))
    commandlist = (('start', 'Start something'), ('stop', 'Stop something'))
    argv = GetArgv(optionlist=optionlist, commandlist=commandlist, addoldfile=0)
    Message('Command line: %s' % ' '.join(argv))
    for i in range(len(argv)):
        print 'arg[%d] = %r' % (i, argv[i])

    ok = AskYesNoCancel('Do you want to proceed?')
    ok = AskYesNoCancel('Do you want to identify?', yes='Identify', no='No')
    if ok > 0:
        s = AskString('Enter your first name', 'Joe')
        s2 = AskPassword('Okay %s, tell us your nickname' % s, s, cancel='None')
        if not s2:
            Message('%s has no secret nickname' % s)
        else:
            Message('Hello everybody!!\nThe secret nickname of %s is %s!!!' % (s, s2))
    else:
        s = 'Anonymous'
    rv = AskFileForOpen(message='Gimme a file, %s' % s, wanted=Carbon.File.FSSpec)
    Message('rv: %s' % rv)
    rv = AskFileForSave(wanted=Carbon.File.FSRef, savedFileName='%s.txt' % s)
    Message('rv.as_pathname: %s' % rv.as_pathname())
    rv = AskFolder()
    Message('Folder name: %s' % rv)
    text = ('Working Hard...', 'Hardly Working...', 'So far, so good!', "Keep on truckin'")
    bar = ProgressBar('Progress, progress...', 0, label='Ramping up...')
    try:
        if hasattr(MacOS, 'SchedParams'):
            appsw = MacOS.SchedParams(1, 0)
        for i in xrange(20):
            bar.inc()
            time.sleep(0.05)

        bar.set(0, 100)
        for i in xrange(100):
            bar.set(i)
            time.sleep(0.05)
            if i % 10 == 0:
                bar.label(text[i / 10 % 4])

        bar.label('Done.')
        time.sleep(1.0)
    finally:
        del bar
        if hasattr(MacOS, 'SchedParams'):
            MacOS.SchedParams(*appsw)


if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        Message('Operation Canceled.')
