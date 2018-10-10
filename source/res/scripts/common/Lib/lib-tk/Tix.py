# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib-tk/Tix.py
from Tkinter import *
from Tkinter import _flatten, _cnfmerge, _default_root
if TkVersion < 3.999:
    raise ImportError, 'This version of Tix.py requires Tk 4.0 or higher'
import _tkinter
WINDOW = 'window'
TEXT = 'text'
STATUS = 'status'
IMMEDIATE = 'immediate'
IMAGE = 'image'
IMAGETEXT = 'imagetext'
BALLOON = 'balloon'
AUTO = 'auto'
ACROSSTOP = 'acrosstop'
ASCII = 'ascii'
CELL = 'cell'
COLUMN = 'column'
DECREASING = 'decreasing'
INCREASING = 'increasing'
INTEGER = 'integer'
MAIN = 'main'
MAX = 'max'
REAL = 'real'
ROW = 'row'
S_REGION = 's-region'
X_REGION = 'x-region'
Y_REGION = 'y-region'
TCL_DONT_WAIT = 2
TCL_WINDOW_EVENTS = 4
TCL_FILE_EVENTS = 8
TCL_TIMER_EVENTS = 16
TCL_IDLE_EVENTS = 32
TCL_ALL_EVENTS = 0
import Tkinter, os

class tixCommand:

    def tix_addbitmapdir(self, directory):
        return self.tk.call('tix', 'addbitmapdir', directory)

    def tix_cget(self, option):
        return self.tk.call('tix', 'cget', option)

    def tix_configure(self, cnf=None, **kw):
        if kw:
            cnf = _cnfmerge((cnf, kw))
        elif cnf:
            cnf = _cnfmerge(cnf)
        if cnf is None:
            return self._getconfigure('tix', 'configure')
        else:
            return self._getconfigure1('tix', 'configure', '-' + cnf) if isinstance(cnf, StringType) else self.tk.call(('tix', 'configure') + self._options(cnf))

    def tix_filedialog(self, dlgclass=None):
        if dlgclass is not None:
            return self.tk.call('tix', 'filedialog', dlgclass)
        else:
            return self.tk.call('tix', 'filedialog')
            return

    def tix_getbitmap(self, name):
        return self.tk.call('tix', 'getbitmap', name)

    def tix_getimage(self, name):
        return self.tk.call('tix', 'getimage', name)

    def tix_option_get(self, name):
        return self.tk.call('tix', 'option', 'get', name)

    def tix_resetoptions(self, newScheme, newFontSet, newScmPrio=None):
        if newScmPrio is not None:
            return self.tk.call('tix', 'resetoptions', newScheme, newFontSet, newScmPrio)
        else:
            return self.tk.call('tix', 'resetoptions', newScheme, newFontSet)
            return


class Tk(Tkinter.Tk, tixCommand):

    def __init__(self, screenName=None, baseName=None, className='Tix'):
        Tkinter.Tk.__init__(self, screenName, baseName, className)
        tixlib = os.environ.get('TIX_LIBRARY')
        self.tk.eval('global auto_path; lappend auto_path [file dir [info nameof]]')
        if tixlib is not None:
            self.tk.eval('global auto_path; lappend auto_path {%s}' % tixlib)
            self.tk.eval('global tcl_pkgPath; lappend tcl_pkgPath {%s}' % tixlib)
        self.tk.eval('package require Tix')
        return

    def destroy(self):
        self.protocol('WM_DELETE_WINDOW', '')
        Tkinter.Tk.destroy(self)


class Form:

    def config(self, cnf={}, **kw):
        self.tk.call('tixForm', self._w, *self._options(cnf, kw))

    form = config

    def __setitem__(self, key, value):
        Form.form(self, {key: value})

    def check(self):
        return self.tk.call('tixForm', 'check', self._w)

    def forget(self):
        self.tk.call('tixForm', 'forget', self._w)

    def grid(self, xsize=0, ysize=0):
        if not xsize and not ysize:
            x = self.tk.call('tixForm', 'grid', self._w)
            y = self.tk.splitlist(x)
            z = ()
            for x in y:
                z = z + (self.tk.getint(x),)

            return z
        return self.tk.call('tixForm', 'grid', self._w, xsize, ysize)

    def info(self, option=None):
        if not option:
            return self.tk.call('tixForm', 'info', self._w)
        if option[0] != '-':
            option = '-' + option
        return self.tk.call('tixForm', 'info', self._w, option)

    def slaves(self):
        return map(self._nametowidget, self.tk.splitlist(self.tk.call('tixForm', 'slaves', self._w)))


Tkinter.Widget.__bases__ = Tkinter.Widget.__bases__ + (Form,)

class TixWidget(Tkinter.Widget):

    def __init__(self, master=None, widgetName=None, static_options=None, cnf={}, kw={}):
        if kw:
            cnf = _cnfmerge((cnf, kw))
        else:
            cnf = _cnfmerge(cnf)
        extra = ()
        if static_options:
            static_options.append('options')
        else:
            static_options = ['options']
        for k, v in cnf.items()[:]:
            if k in static_options:
                extra = extra + ('-' + k, v)
                del cnf[k]

        self.widgetName = widgetName
        Widget._setup(self, master, cnf)
        if widgetName:
            self.tk.call(widgetName, self._w, *extra)
        if cnf:
            Widget.config(self, cnf)
        self.subwidget_list = {}

    def __getattr__(self, name):
        if name in self.subwidget_list:
            return self.subwidget_list[name]
        raise AttributeError, name

    def set_silent(self, value):
        self.tk.call('tixSetSilent', self._w, value)

    def subwidget(self, name):
        n = self._subwidget_name(name)
        if not n:
            raise TclError, 'Subwidget ' + name + ' not child of ' + self._name
        n = n[len(self._w) + 1:]
        return self._nametowidget(n)

    def subwidgets_all(self):
        names = self._subwidget_names()
        if not names:
            return []
        retlist = []
        for name in names:
            name = name[len(self._w) + 1:]
            try:
                retlist.append(self._nametowidget(name))
            except:
                pass

        return retlist

    def _subwidget_name(self, name):
        try:
            return self.tk.call(self._w, 'subwidget', name)
        except TclError:
            return None

        return None

    def _subwidget_names(self):
        try:
            x = self.tk.call(self._w, 'subwidgets', '-all')
            return self.tk.splitlist(x)
        except TclError:
            return None

        return None

    def config_all(self, option, value):
        if option == '':
            return
        if not isinstance(option, StringType):
            option = repr(option)
        if not isinstance(value, StringType):
            value = repr(value)
        names = self._subwidget_names()
        for name in names:
            self.tk.call(name, 'configure', '-' + option, value)

    def image_create(self, imgtype, cnf={}, master=None, **kw):
        if not master:
            master = Tkinter._default_root
            if not master:
                raise RuntimeError, 'Too early to create image'
        if kw and cnf:
            cnf = _cnfmerge((cnf, kw))
        elif kw:
            cnf = kw
        options = ()
        for k, v in cnf.items():
            if hasattr(v, '__call__'):
                v = self._register(v)
            options = options + ('-' + k, v)

        return master.tk.call(('image', 'create', imgtype) + options)

    def image_delete(self, imgname):
        try:
            self.tk.call('image', 'delete', imgname)
        except TclError:
            pass


class TixSubWidget(TixWidget):

    def __init__(self, master, name, destroy_physically=1, check_intermediate=1):
        if check_intermediate:
            path = master._subwidget_name(name)
            try:
                path = path[len(master._w) + 1:]
                plist = path.split('.')
            except:
                plist = []

        if not check_intermediate:
            TixWidget.__init__(self, master, None, None, {'name': name})
        else:
            parent = master
            for i in range(len(plist) - 1):
                n = '.'.join(plist[:i + 1])
                try:
                    w = master._nametowidget(n)
                    parent = w
                except KeyError:
                    parent = TixSubWidget(parent, plist[i], destroy_physically=0, check_intermediate=0)

            if plist:
                name = plist[-1]
            TixWidget.__init__(self, parent, None, None, {'name': name})
        self.destroy_physically = destroy_physically
        return

    def destroy(self):
        for c in self.children.values():
            c.destroy()

        if self._name in self.master.children:
            del self.master.children[self._name]
        if self._name in self.master.subwidget_list:
            del self.master.subwidget_list[self._name]
        if self.destroy_physically:
            self.tk.call('destroy', self._w)


class DisplayStyle:

    def __init__(self, itemtype, cnf={}, **kw):
        master = _default_root
        if not master and 'refwindow' in cnf:
            master = cnf['refwindow']
        elif not master and 'refwindow' in kw:
            master = kw['refwindow']
        elif not master:
            raise RuntimeError, 'Too early to create display style: no root window'
        self.tk = master.tk
        self.stylename = self.tk.call('tixDisplayStyle', itemtype, *self._options(cnf, kw))

    def __str__(self):
        return self.stylename

    def _options(self, cnf, kw):
        if kw and cnf:
            cnf = _cnfmerge((cnf, kw))
        elif kw:
            cnf = kw
        opts = ()
        for k, v in cnf.items():
            opts = opts + ('-' + k, v)

        return opts

    def delete(self):
        self.tk.call(self.stylename, 'delete')

    def __setitem__(self, key, value):
        self.tk.call(self.stylename, 'configure', '-%s' % key, value)

    def config(self, cnf={}, **kw):
        return self._getconfigure(self.stylename, 'configure', *self._options(cnf, kw))

    def __getitem__(self, key):
        return self.tk.call(self.stylename, 'cget', '-%s' % key)


class Balloon(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        static = ['options',
         'installcolormap',
         'initwait',
         'statusbar',
         'cursor']
        TixWidget.__init__(self, master, 'tixBalloon', static, cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label', destroy_physically=0)
        self.subwidget_list['message'] = _dummyLabel(self, 'message', destroy_physically=0)

    def bind_widget(self, widget, cnf={}, **kw):
        self.tk.call(self._w, 'bind', widget._w, *self._options(cnf, kw))

    def unbind_widget(self, widget):
        self.tk.call(self._w, 'unbind', widget._w)


class ButtonBox(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixButtonBox', ['orientation', 'options'], cnf, kw)

    def add(self, name, cnf={}, **kw):
        btn = self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = _dummyButton(self, name)
        return btn

    def invoke(self, name):
        if name in self.subwidget_list:
            self.tk.call(self._w, 'invoke', name)


class ComboBox(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixComboBox', ['editable',
         'dropdown',
         'fancy',
         'options'], cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')
        self.subwidget_list['arrow'] = _dummyButton(self, 'arrow')
        self.subwidget_list['slistbox'] = _dummyScrolledListBox(self, 'slistbox')
        try:
            self.subwidget_list['tick'] = _dummyButton(self, 'tick')
            self.subwidget_list['cross'] = _dummyButton(self, 'cross')
        except TypeError:
            pass

    def add_history(self, str):
        self.tk.call(self._w, 'addhistory', str)

    def append_history(self, str):
        self.tk.call(self._w, 'appendhistory', str)

    def insert(self, index, str):
        self.tk.call(self._w, 'insert', index, str)

    def pick(self, index):
        self.tk.call(self._w, 'pick', index)


class Control(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixControl', ['options'], cnf, kw)
        self.subwidget_list['incr'] = _dummyButton(self, 'incr')
        self.subwidget_list['decr'] = _dummyButton(self, 'decr')
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')

    def decrement(self):
        self.tk.call(self._w, 'decr')

    def increment(self):
        self.tk.call(self._w, 'incr')

    def invoke(self):
        self.tk.call(self._w, 'invoke')

    def update(self):
        self.tk.call(self._w, 'update')


class DirList(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirList', ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    def chdir(self, dir):
        self.tk.call(self._w, 'chdir', dir)


class DirTree(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirTree', ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    def chdir(self, dir):
        self.tk.call(self._w, 'chdir', dir)


class DirSelectBox(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirSelectBox', ['options'], cnf, kw)
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['dircbx'] = _dummyFileComboBox(self, 'dircbx')


class ExFileSelectBox(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixExFileSelectBox', ['options'], cnf, kw)
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['hidden'] = _dummyCheckbutton(self, 'hidden')
        self.subwidget_list['types'] = _dummyComboBox(self, 'types')
        self.subwidget_list['dir'] = _dummyComboBox(self, 'dir')
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['file'] = _dummyComboBox(self, 'file')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')

    def filter(self):
        self.tk.call(self._w, 'filter')

    def invoke(self):
        self.tk.call(self._w, 'invoke')


class DirSelectDialog(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirSelectDialog', ['options'], cnf, kw)
        self.subwidget_list['dirbox'] = _dummyDirSelectBox(self, 'dirbox')

    def popup(self):
        self.tk.call(self._w, 'popup')

    def popdown(self):
        self.tk.call(self._w, 'popdown')


class ExFileSelectDialog(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixExFileSelectDialog', ['options'], cnf, kw)
        self.subwidget_list['fsbox'] = _dummyExFileSelectBox(self, 'fsbox')

    def popup(self):
        self.tk.call(self._w, 'popup')

    def popdown(self):
        self.tk.call(self._w, 'popdown')


class FileSelectBox(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileSelectBox', ['options'], cnf, kw)
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')
        self.subwidget_list['filter'] = _dummyComboBox(self, 'filter')
        self.subwidget_list['selection'] = _dummyComboBox(self, 'selection')

    def apply_filter(self):
        self.tk.call(self._w, 'filter')

    def invoke(self):
        self.tk.call(self._w, 'invoke')


class FileSelectDialog(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileSelectDialog', ['options'], cnf, kw)
        self.subwidget_list['btns'] = _dummyStdButtonBox(self, 'btns')
        self.subwidget_list['fsbox'] = _dummyFileSelectBox(self, 'fsbox')

    def popup(self):
        self.tk.call(self._w, 'popup')

    def popdown(self):
        self.tk.call(self._w, 'popdown')


class FileEntry(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileEntry', ['dialogtype', 'options'], cnf, kw)
        self.subwidget_list['button'] = _dummyButton(self, 'button')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')

    def invoke(self):
        self.tk.call(self._w, 'invoke')

    def file_dialog(self):
        pass


class HList(TixWidget, XView, YView):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixHList', ['columns', 'options'], cnf, kw)

    def add(self, entry, cnf={}, **kw):
        return self.tk.call(self._w, 'add', entry, *self._options(cnf, kw))

    def add_child(self, parent=None, cnf={}, **kw):
        if not parent:
            parent = ''
        return self.tk.call(self._w, 'addchild', parent, *self._options(cnf, kw))

    def anchor_set(self, entry):
        self.tk.call(self._w, 'anchor', 'set', entry)

    def anchor_clear(self):
        self.tk.call(self._w, 'anchor', 'clear')

    def column_width(self, col=0, width=None, chars=None):
        if not chars:
            return self.tk.call(self._w, 'column', 'width', col, width)
        else:
            return self.tk.call(self._w, 'column', 'width', col, '-char', chars)

    def delete_all(self):
        self.tk.call(self._w, 'delete', 'all')

    def delete_entry(self, entry):
        self.tk.call(self._w, 'delete', 'entry', entry)

    def delete_offsprings(self, entry):
        self.tk.call(self._w, 'delete', 'offsprings', entry)

    def delete_siblings(self, entry):
        self.tk.call(self._w, 'delete', 'siblings', entry)

    def dragsite_set(self, index):
        self.tk.call(self._w, 'dragsite', 'set', index)

    def dragsite_clear(self):
        self.tk.call(self._w, 'dragsite', 'clear')

    def dropsite_set(self, index):
        self.tk.call(self._w, 'dropsite', 'set', index)

    def dropsite_clear(self):
        self.tk.call(self._w, 'dropsite', 'clear')

    def header_create(self, col, cnf={}, **kw):
        self.tk.call(self._w, 'header', 'create', col, *self._options(cnf, kw))

    def header_configure(self, col, cnf={}, **kw):
        if cnf is None:
            return self._getconfigure(self._w, 'header', 'configure', col)
        else:
            self.tk.call(self._w, 'header', 'configure', col, *self._options(cnf, kw))
            return

    def header_cget(self, col, opt):
        return self.tk.call(self._w, 'header', 'cget', col, opt)

    def header_exists(self, col):
        return self.tk.call(self._w, 'header', 'exists', col)

    def header_delete(self, col):
        self.tk.call(self._w, 'header', 'delete', col)

    def header_size(self, col):
        return self.tk.call(self._w, 'header', 'size', col)

    def hide_entry(self, entry):
        self.tk.call(self._w, 'hide', 'entry', entry)

    def indicator_create(self, entry, cnf={}, **kw):
        self.tk.call(self._w, 'indicator', 'create', entry, *self._options(cnf, kw))

    def indicator_configure(self, entry, cnf={}, **kw):
        if cnf is None:
            return self._getconfigure(self._w, 'indicator', 'configure', entry)
        else:
            self.tk.call(self._w, 'indicator', 'configure', entry, *self._options(cnf, kw))
            return

    def indicator_cget(self, entry, opt):
        return self.tk.call(self._w, 'indicator', 'cget', entry, opt)

    def indicator_exists(self, entry):
        return self.tk.call(self._w, 'indicator', 'exists', entry)

    def indicator_delete(self, entry):
        self.tk.call(self._w, 'indicator', 'delete', entry)

    def indicator_size(self, entry):
        return self.tk.call(self._w, 'indicator', 'size', entry)

    def info_anchor(self):
        return self.tk.call(self._w, 'info', 'anchor')

    def info_bbox(self, entry):
        return self._getints(self.tk.call(self._w, 'info', 'bbox', entry)) or None

    def info_children(self, entry=None):
        c = self.tk.call(self._w, 'info', 'children', entry)
        return self.tk.splitlist(c)

    def info_data(self, entry):
        return self.tk.call(self._w, 'info', 'data', entry)

    def info_dragsite(self):
        return self.tk.call(self._w, 'info', 'dragsite')

    def info_dropsite(self):
        return self.tk.call(self._w, 'info', 'dropsite')

    def info_exists(self, entry):
        return self.tk.call(self._w, 'info', 'exists', entry)

    def info_hidden(self, entry):
        return self.tk.call(self._w, 'info', 'hidden', entry)

    def info_next(self, entry):
        return self.tk.call(self._w, 'info', 'next', entry)

    def info_parent(self, entry):
        return self.tk.call(self._w, 'info', 'parent', entry)

    def info_prev(self, entry):
        return self.tk.call(self._w, 'info', 'prev', entry)

    def info_selection(self):
        c = self.tk.call(self._w, 'info', 'selection')
        return self.tk.splitlist(c)

    def item_cget(self, entry, col, opt):
        return self.tk.call(self._w, 'item', 'cget', entry, col, opt)

    def item_configure(self, entry, col, cnf={}, **kw):
        if cnf is None:
            return self._getconfigure(self._w, 'item', 'configure', entry, col)
        else:
            self.tk.call(self._w, 'item', 'configure', entry, col, *self._options(cnf, kw))
            return

    def item_create(self, entry, col, cnf={}, **kw):
        self.tk.call(self._w, 'item', 'create', entry, col, *self._options(cnf, kw))

    def item_exists(self, entry, col):
        return self.tk.call(self._w, 'item', 'exists', entry, col)

    def item_delete(self, entry, col):
        self.tk.call(self._w, 'item', 'delete', entry, col)

    def entrycget(self, entry, opt):
        return self.tk.call(self._w, 'entrycget', entry, opt)

    def entryconfigure(self, entry, cnf={}, **kw):
        if cnf is None:
            return self._getconfigure(self._w, 'entryconfigure', entry)
        else:
            self.tk.call(self._w, 'entryconfigure', entry, *self._options(cnf, kw))
            return

    def nearest(self, y):
        return self.tk.call(self._w, 'nearest', y)

    def see(self, entry):
        self.tk.call(self._w, 'see', entry)

    def selection_clear(self, cnf={}, **kw):
        self.tk.call(self._w, 'selection', 'clear', *self._options(cnf, kw))

    def selection_includes(self, entry):
        return self.tk.call(self._w, 'selection', 'includes', entry)

    def selection_set(self, first, last=None):
        self.tk.call(self._w, 'selection', 'set', first, last)

    def show_entry(self, entry):
        return self.tk.call(self._w, 'show', 'entry', entry)


class InputOnly(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixInputOnly', None, cnf, kw)
        return


class LabelEntry(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixLabelEntry', ['labelside', 'options'], cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')


class LabelFrame(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixLabelFrame', ['labelside', 'options'], cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['frame'] = _dummyFrame(self, 'frame')


class ListNoteBook(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixListNoteBook', ['options'], cnf, kw)
        self.subwidget_list['pane'] = _dummyPanedWindow(self, 'pane', destroy_physically=0)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['shlist'] = _dummyScrolledHList(self, 'shlist')

    def add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name)
        return self.subwidget_list[name]

    def page(self, name):
        return self.subwidget(name)

    def pages(self):
        names = self.tk.split(self.tk.call(self._w, 'pages'))
        ret = []
        for x in names:
            ret.append(self.subwidget(x))

        return ret

    def raise_page(self, name):
        self.tk.call(self._w, 'raise', name)


class Meter(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixMeter', ['options'], cnf, kw)


class NoteBook(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixNoteBook', ['options'], cnf, kw)
        self.subwidget_list['nbframe'] = TixSubWidget(self, 'nbframe', destroy_physically=0)

    def add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name)
        return self.subwidget_list[name]

    def delete(self, name):
        self.tk.call(self._w, 'delete', name)
        self.subwidget_list[name].destroy()
        del self.subwidget_list[name]

    def page(self, name):
        return self.subwidget(name)

    def pages(self):
        names = self.tk.split(self.tk.call(self._w, 'pages'))
        ret = []
        for x in names:
            ret.append(self.subwidget(x))

        return ret

    def raise_page(self, name):
        self.tk.call(self._w, 'raise', name)

    def raised(self):
        return self.tk.call(self._w, 'raised')


class NoteBookFrame(TixWidget):
    pass


class OptionMenu(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixOptionMenu', ['labelside', 'options'], cnf, kw)
        self.subwidget_list['menubutton'] = _dummyMenubutton(self, 'menubutton')
        self.subwidget_list['menu'] = _dummyMenu(self, 'menu')

    def add_command(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', 'command', name, *self._options(cnf, kw))

    def add_separator(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', 'separator', name, *self._options(cnf, kw))

    def delete(self, name):
        self.tk.call(self._w, 'delete', name)

    def disable(self, name):
        self.tk.call(self._w, 'disable', name)

    def enable(self, name):
        self.tk.call(self._w, 'enable', name)


class PanedWindow(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixPanedWindow', ['orientation', 'options'], cnf, kw)

    def add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name, check_intermediate=0)
        return self.subwidget_list[name]

    def delete(self, name):
        self.tk.call(self._w, 'delete', name)
        self.subwidget_list[name].destroy()
        del self.subwidget_list[name]

    def forget(self, name):
        self.tk.call(self._w, 'forget', name)

    def panecget(self, entry, opt):
        return self.tk.call(self._w, 'panecget', entry, opt)

    def paneconfigure(self, entry, cnf={}, **kw):
        if cnf is None:
            return self._getconfigure(self._w, 'paneconfigure', entry)
        else:
            self.tk.call(self._w, 'paneconfigure', entry, *self._options(cnf, kw))
            return

    def panes(self):
        names = self.tk.splitlist(self.tk.call(self._w, 'panes'))
        return [ self.subwidget(x) for x in names ]


class PopupMenu(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixPopupMenu', ['options'], cnf, kw)
        self.subwidget_list['menubutton'] = _dummyMenubutton(self, 'menubutton')
        self.subwidget_list['menu'] = _dummyMenu(self, 'menu')

    def bind_widget(self, widget):
        self.tk.call(self._w, 'bind', widget._w)

    def unbind_widget(self, widget):
        self.tk.call(self._w, 'unbind', widget._w)

    def post_widget(self, widget, x, y):
        self.tk.call(self._w, 'post', widget._w, x, y)


class ResizeHandle(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        flags = ['options',
         'command',
         'cursorfg',
         'cursorbg',
         'handlesize',
         'hintcolor',
         'hintwidth',
         'x',
         'y']
        TixWidget.__init__(self, master, 'tixResizeHandle', flags, cnf, kw)

    def attach_widget(self, widget):
        self.tk.call(self._w, 'attachwidget', widget._w)

    def detach_widget(self, widget):
        self.tk.call(self._w, 'detachwidget', widget._w)

    def hide(self, widget):
        self.tk.call(self._w, 'hide', widget._w)

    def show(self, widget):
        self.tk.call(self._w, 'show', widget._w)


class ScrolledHList(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledHList', ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')


class ScrolledListBox(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledListBox', ['options'], cnf, kw)
        self.subwidget_list['listbox'] = _dummyListbox(self, 'listbox')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')


class ScrolledText(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledText', ['options'], cnf, kw)
        self.subwidget_list['text'] = _dummyText(self, 'text')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')


class ScrolledTList(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledTList', ['options'], cnf, kw)
        self.subwidget_list['tlist'] = _dummyTList(self, 'tlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')


class ScrolledWindow(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledWindow', ['options'], cnf, kw)
        self.subwidget_list['window'] = _dummyFrame(self, 'window')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')


class Select(TixWidget):

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixSelect', ['allowzero',
         'radio',
         'orientation',
         'labelside',
         'options'], cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')

    def add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = _dummyButton(self, name)
        return self.subwidget_list[name]

    def invoke(self, name):
        self.tk.call(self._w, 'invoke', name)


class Shell(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixShell', ['options', 'title'], cnf, kw)


class DialogShell(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDialogShell', ['options',
         'title',
         'mapped',
         'minheight',
         'minwidth',
         'parent',
         'transient'], cnf, kw)

    def popdown(self):
        self.tk.call(self._w, 'popdown')

    def popup(self):
        self.tk.call(self._w, 'popup')

    def center(self):
        self.tk.call(self._w, 'center')


class StdButtonBox(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixStdButtonBox', ['orientation', 'options'], cnf, kw)
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['apply'] = _dummyButton(self, 'apply')
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['help'] = _dummyButton(self, 'help')

    def invoke(self, name):
        if name in self.subwidget_list:
            self.tk.call(self._w, 'invoke', name)


class TList(TixWidget, XView, YView):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixTList', ['options'], cnf, kw)

    def active_set(self, index):
        self.tk.call(self._w, 'active', 'set', index)

    def active_clear(self):
        self.tk.call(self._w, 'active', 'clear')

    def anchor_set(self, index):
        self.tk.call(self._w, 'anchor', 'set', index)

    def anchor_clear(self):
        self.tk.call(self._w, 'anchor', 'clear')

    def delete(self, from_, to=None):
        self.tk.call(self._w, 'delete', from_, to)

    def dragsite_set(self, index):
        self.tk.call(self._w, 'dragsite', 'set', index)

    def dragsite_clear(self):
        self.tk.call(self._w, 'dragsite', 'clear')

    def dropsite_set(self, index):
        self.tk.call(self._w, 'dropsite', 'set', index)

    def dropsite_clear(self):
        self.tk.call(self._w, 'dropsite', 'clear')

    def insert(self, index, cnf={}, **kw):
        self.tk.call(self._w, 'insert', index, *self._options(cnf, kw))

    def info_active(self):
        return self.tk.call(self._w, 'info', 'active')

    def info_anchor(self):
        return self.tk.call(self._w, 'info', 'anchor')

    def info_down(self, index):
        return self.tk.call(self._w, 'info', 'down', index)

    def info_left(self, index):
        return self.tk.call(self._w, 'info', 'left', index)

    def info_right(self, index):
        return self.tk.call(self._w, 'info', 'right', index)

    def info_selection(self):
        c = self.tk.call(self._w, 'info', 'selection')
        return self.tk.splitlist(c)

    def info_size(self):
        return self.tk.call(self._w, 'info', 'size')

    def info_up(self, index):
        return self.tk.call(self._w, 'info', 'up', index)

    def nearest(self, x, y):
        return self.tk.call(self._w, 'nearest', x, y)

    def see(self, index):
        self.tk.call(self._w, 'see', index)

    def selection_clear(self, cnf={}, **kw):
        self.tk.call(self._w, 'selection', 'clear', *self._options(cnf, kw))

    def selection_includes(self, index):
        return self.tk.call(self._w, 'selection', 'includes', index)

    def selection_set(self, first, last=None):
        self.tk.call(self._w, 'selection', 'set', first, last)


class Tree(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixTree', ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    def autosetmode(self):
        self.tk.call(self._w, 'autosetmode')

    def close(self, entrypath):
        self.tk.call(self._w, 'close', entrypath)

    def getmode(self, entrypath):
        return self.tk.call(self._w, 'getmode', entrypath)

    def open(self, entrypath):
        self.tk.call(self._w, 'open', entrypath)

    def setmode(self, entrypath, mode='none'):
        self.tk.call(self._w, 'setmode', entrypath, mode)


class CheckList(TixWidget):

    def __init__(self, master=None, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixCheckList', ['options', 'radio'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    def autosetmode(self):
        self.tk.call(self._w, 'autosetmode')

    def close(self, entrypath):
        self.tk.call(self._w, 'close', entrypath)

    def getmode(self, entrypath):
        return self.tk.call(self._w, 'getmode', entrypath)

    def open(self, entrypath):
        self.tk.call(self._w, 'open', entrypath)

    def getselection(self, mode='on'):
        c = self.tk.split(self.tk.call(self._w, 'getselection', mode))
        return self.tk.splitlist(c)

    def getstatus(self, entrypath):
        return self.tk.call(self._w, 'getstatus', entrypath)

    def setstatus(self, entrypath, mode='on'):
        self.tk.call(self._w, 'setstatus', entrypath, mode)


class _dummyButton(Button, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyCheckbutton(Checkbutton, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyEntry(Entry, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyFrame(Frame, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyLabel(Label, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyListbox(Listbox, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyMenu(Menu, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyMenubutton(Menubutton, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyScrollbar(Scrollbar, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyText(Text, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyScrolledListBox(ScrolledListBox, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['listbox'] = _dummyListbox(self, 'listbox')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')


class _dummyHList(HList, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyScrolledHList(ScrolledHList, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')


class _dummyTList(TList, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyComboBox(ComboBox, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, ['fancy', destroy_physically])
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')
        self.subwidget_list['arrow'] = _dummyButton(self, 'arrow')
        self.subwidget_list['slistbox'] = _dummyScrolledListBox(self, 'slistbox')
        try:
            self.subwidget_list['tick'] = _dummyButton(self, 'tick')
            self.subwidget_list['cross'] = _dummyButton(self, 'cross')
        except TypeError:
            pass


class _dummyDirList(DirList, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')


class _dummyDirSelectBox(DirSelectBox, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['dircbx'] = _dummyFileComboBox(self, 'dircbx')


class _dummyExFileSelectBox(ExFileSelectBox, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['hidden'] = _dummyCheckbutton(self, 'hidden')
        self.subwidget_list['types'] = _dummyComboBox(self, 'types')
        self.subwidget_list['dir'] = _dummyComboBox(self, 'dir')
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['file'] = _dummyComboBox(self, 'file')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')


class _dummyFileSelectBox(FileSelectBox, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')
        self.subwidget_list['filter'] = _dummyComboBox(self, 'filter')
        self.subwidget_list['selection'] = _dummyComboBox(self, 'selection')


class _dummyFileComboBox(ComboBox, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dircbx'] = _dummyComboBox(self, 'dircbx')


class _dummyStdButtonBox(StdButtonBox, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['apply'] = _dummyButton(self, 'apply')
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['help'] = _dummyButton(self, 'help')


class _dummyNoteBookFrame(NoteBookFrame, TixSubWidget):

    def __init__(self, master, name, destroy_physically=0):
        TixSubWidget.__init__(self, master, name, destroy_physically)


class _dummyPanedWindow(PanedWindow, TixSubWidget):

    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)


def OptionName(widget):
    return widget.tk.call('tixOptionName', widget._w)


def FileTypeList(dict):
    s = ''
    for type in dict.keys():
        s = s + '{{' + type + '} {' + type + ' - ' + dict[type] + '}} '

    return s


class CObjView(TixWidget):
    pass


class Grid(TixWidget, XView, YView):

    def __init__(self, master=None, cnf={}, **kw):
        static = []
        self.cnf = cnf
        TixWidget.__init__(self, master, 'tixGrid', static, cnf, kw)

    def anchor_clear(self):
        self.tk.call(self, 'anchor', 'clear')

    def anchor_get(self):
        return self._getints(self.tk.call(self, 'anchor', 'get'))

    def anchor_set(self, x, y):
        self.tk.call(self, 'anchor', 'set', x, y)

    def delete_row(self, from_, to=None):
        if to is None:
            self.tk.call(self, 'delete', 'row', from_)
        else:
            self.tk.call(self, 'delete', 'row', from_, to)
        return

    def delete_column(self, from_, to=None):
        if to is None:
            self.tk.call(self, 'delete', 'column', from_)
        else:
            self.tk.call(self, 'delete', 'column', from_, to)
        return

    def edit_apply(self):
        self.tk.call(self, 'edit', 'apply')

    def edit_set(self, x, y):
        self.tk.call(self, 'edit', 'set', x, y)

    def entrycget(self, x, y, option):
        if option and option[0] != '-':
            option = '-' + option
        return self.tk.call(self, 'entrycget', x, y, option)

    def entryconfigure(self, x, y, cnf=None, **kw):
        return self._configure(('entryconfigure', x, y), cnf, kw)

    def info_exists(self, x, y):
        return self._getboolean(self.tk.call(self, 'info', 'exists', x, y))

    def info_bbox(self, x, y):
        return self.tk.call(self, 'info', 'bbox', x, y)

    def move_column(self, from_, to, offset):
        self.tk.call(self, 'move', 'column', from_, to, offset)

    def move_row(self, from_, to, offset):
        self.tk.call(self, 'move', 'row', from_, to, offset)

    def nearest(self, x, y):
        return self._getints(self.tk.call(self, 'nearest', x, y))

    def set(self, x, y, itemtype=None, **kw):
        args = self._options(self.cnf, kw)
        if itemtype is not None:
            args = ('-itemtype', itemtype) + args
        self.tk.call(self, 'set', x, y, *args)
        return

    def size_column(self, index, **kw):
        return self.tk.split(self.tk.call(self._w, 'size', 'column', index, *self._options({}, kw)))

    def size_row(self, index, **kw):
        return self.tk.split(self.tk.call(self, 'size', 'row', index, *self._options({}, kw)))

    def unset(self, x, y):
        self.tk.call(self._w, 'unset', x, y)


class ScrolledGrid(Grid):

    def __init__(self, master=None, cnf={}, **kw):
        static = []
        self.cnf = cnf
        TixWidget.__init__(self, master, 'tixScrolledGrid', static, cnf, kw)
