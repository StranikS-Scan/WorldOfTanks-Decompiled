# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib-tk/ttk.py
__version__ = '0.3.1'
__author__ = 'Guilherme Polo <ggpolo@gmail.com>'
__all__ = ['Button',
 'Checkbutton',
 'Combobox',
 'Entry',
 'Frame',
 'Label',
 'Labelframe',
 'LabelFrame',
 'Menubutton',
 'Notebook',
 'Panedwindow',
 'PanedWindow',
 'Progressbar',
 'Radiobutton',
 'Scale',
 'Scrollbar',
 'Separator',
 'Sizegrip',
 'Style',
 'Treeview',
 'LabeledScale',
 'OptionMenu',
 'tclobjs_to_py',
 'setup_master']
import Tkinter
from Tkinter import _flatten, _join, _stringify, _splitdict
_REQUIRE_TILE = True if Tkinter.TkVersion < 8.5 else False

def _load_tile(master):
    if _REQUIRE_TILE:
        import os
        tilelib = os.environ.get('TILE_LIBRARY')
        if tilelib:
            master.tk.eval('global auto_path; lappend auto_path {%s}' % tilelib)
        master.tk.eval('package require tile')
        master._tile_loaded = True


def _format_optvalue(value, script=False):
    if script:
        value = _stringify(value)
    elif isinstance(value, (list, tuple)):
        value = _join(value)
    return value


def _format_optdict(optdict, script=False, ignore=None):
    opts = []
    for opt, value in optdict.iteritems():
        if not ignore or opt not in ignore:
            opts.append('-%s' % opt)
            if value is not None:
                opts.append(_format_optvalue(value, script))

    return _flatten(opts)


def _mapdict_values(items):
    opt_val = []
    for item in items:
        state = item[:-1]
        val = item[-1]
        state[0]
        if len(state) == 1:
            state = state[0] or ''
        else:
            state = ' '.join(state)
        opt_val.append(state)
        if val is not None:
            opt_val.append(val)

    return opt_val


def _format_mapdict(mapdict, script=False):
    opts = []
    for opt, value in mapdict.iteritems():
        opts.extend(('-%s' % opt, _format_optvalue(_mapdict_values(value), script)))

    return _flatten(opts)


def _format_elemcreate(etype, script=False, *args, **kw):
    spec = None
    opts = ()
    if etype in ('image', 'vsapi'):
        if etype == 'image':
            iname = args[0]
            imagespec = _join(_mapdict_values(args[1:]))
            spec = '%s %s' % (iname, imagespec)
        else:
            class_name, part_id = args[:2]
            statemap = _join(_mapdict_values(args[2:]))
            spec = '%s %s %s' % (class_name, part_id, statemap)
        opts = _format_optdict(kw, script)
    elif etype == 'from':
        spec = args[0]
        if len(args) > 1:
            opts = (_format_optvalue(args[1], script),)
    if script:
        spec = '{%s}' % spec
        opts = ' '.join(opts)
    return (spec, opts)


def _format_layoutlist(layout, indent=0, indent_size=2):
    script = []
    for layout_elem in layout:
        elem, opts = layout_elem
        opts = opts or {}
        fopts = ' '.join(_format_optdict(opts, True, ('children',)))
        head = '%s%s%s' % (' ' * indent, elem, ' %s' % fopts if fopts else '')
        if 'children' in opts:
            script.append(head + ' -children {')
            indent += indent_size
            newscript, indent = _format_layoutlist(opts['children'], indent, indent_size)
            script.append(newscript)
            indent -= indent_size
            script.append('%s}' % (' ' * indent))
        script.append(head)

    return ('\n'.join(script), indent)


def _script_from_settings(settings):
    script = []
    for name, opts in settings.iteritems():
        if opts.get('configure'):
            s = ' '.join(_format_optdict(opts['configure'], True))
            script.append('ttk::style configure %s %s;' % (name, s))
        if opts.get('map'):
            s = ' '.join(_format_mapdict(opts['map'], True))
            script.append('ttk::style map %s %s;' % (name, s))
        if 'layout' in opts:
            if not opts['layout']:
                s = 'null'
            else:
                s, _ = _format_layoutlist(opts['layout'])
            script.append('ttk::style layout %s {\n%s\n}' % (name, s))
        if opts.get('element create'):
            eopts = opts['element create']
            etype = eopts[0]
            argc = 1
            while argc < len(eopts) and not hasattr(eopts[argc], 'iteritems'):
                argc += 1

            elemargs = eopts[1:argc]
            elemkw = eopts[argc] if argc < len(eopts) and eopts[argc] else {}
            spec, opts = _format_elemcreate(etype, True, *elemargs, **elemkw)
            script.append('ttk::style element create %s %s %s %s' % (name,
             etype,
             spec,
             opts))

    return '\n'.join(script)


def _list_from_statespec(stuple):
    nval = []
    for val in stuple:
        typename = getattr(val, 'typename', None)
        if typename is None:
            nval.append(val)
        val = str(val)
        if typename == 'StateSpec':
            val = val.split()
        nval.append(val)

    it = iter(nval)
    return [ _flatten(spec) for spec in zip(it, it) ]


def _list_from_layouttuple(tk, ltuple):
    ltuple = tk.splitlist(ltuple)
    res = []
    indx = 0
    while indx < len(ltuple):
        name = ltuple[indx]
        opts = {}
        res.append((name, opts))
        indx += 1
        while indx < len(ltuple):
            opt, val = ltuple[indx:indx + 2]
            if not opt.startswith('-'):
                break
            opt = opt[1:]
            indx += 2
            if opt == 'children':
                val = _list_from_layouttuple(tk, val)
            opts[opt] = val

    return res


def _val_or_dict(tk, options, *args):
    options = _format_optdict(options)
    res = tk.call(*(args + options))
    return res if len(options) % 2 else _splitdict(tk, res, conv=_tclobj_to_py)


def _convert_stringval(value):
    value = unicode(value)
    try:
        value = int(value)
    except (ValueError, TypeError):
        pass

    return value


def _to_number(x):
    if isinstance(x, str):
        if '.' in x:
            x = float(x)
        else:
            x = int(x)
    return x


def _tclobj_to_py(val):
    if val and hasattr(val, '__len__') and not isinstance(val, basestring):
        if getattr(val[0], 'typename', None) == 'StateSpec':
            val = _list_from_statespec(val)
        else:
            val = map(_convert_stringval, val)
    elif hasattr(val, 'typename'):
        val = _convert_stringval(val)
    return val


def tclobjs_to_py(adict):
    for opt, val in adict.items():
        adict[opt] = _tclobj_to_py(val)

    return adict


def setup_master(master=None):
    if master is None:
        if Tkinter._support_default_root:
            master = Tkinter._default_root or Tkinter.Tk()
        else:
            raise RuntimeError('No master specified and Tkinter is configured to not support default root')
    return master


class Style(object):
    _name = 'ttk::style'

    def __init__(self, master=None):
        master = setup_master(master)
        if not getattr(master, '_tile_loaded', False):
            _load_tile(master)
        self.master = master
        self.tk = self.master.tk

    def configure(self, style, query_opt=None, **kw):
        if query_opt is not None:
            kw[query_opt] = None
        return _val_or_dict(self.tk, kw, self._name, 'configure', style)

    def map(self, style, query_opt=None, **kw):
        return _list_from_statespec(self.tk.splitlist(self.tk.call(self._name, 'map', style, '-%s' % query_opt))) if query_opt is not None else _splitdict(self.tk, self.tk.call(self._name, 'map', style, *_format_mapdict(kw)), conv=_tclobj_to_py)

    def lookup(self, style, option, state=None, default=None):
        state = ' '.join(state) if state else ''
        return self.tk.call(self._name, 'lookup', style, '-%s' % option, state, default)

    def layout(self, style, layoutspec=None):
        lspec = None
        if layoutspec:
            lspec = _format_layoutlist(layoutspec)[0]
        elif layoutspec is not None:
            lspec = 'null'
        return _list_from_layouttuple(self.tk, self.tk.call(self._name, 'layout', style, lspec))

    def element_create(self, elementname, etype, *args, **kw):
        spec, opts = _format_elemcreate(etype, False, *args, **kw)
        self.tk.call(self._name, 'element', 'create', elementname, etype, spec, *opts)

    def element_names(self):
        return self.tk.splitlist(self.tk.call(self._name, 'element', 'names'))

    def element_options(self, elementname):
        return self.tk.splitlist(self.tk.call(self._name, 'element', 'options', elementname))

    def theme_create(self, themename, parent=None, settings=None):
        script = _script_from_settings(settings) if settings else ''
        if parent:
            self.tk.call(self._name, 'theme', 'create', themename, '-parent', parent, '-settings', script)
        else:
            self.tk.call(self._name, 'theme', 'create', themename, '-settings', script)

    def theme_settings(self, themename, settings):
        script = _script_from_settings(settings)
        self.tk.call(self._name, 'theme', 'settings', themename, script)

    def theme_names(self):
        return self.tk.splitlist(self.tk.call(self._name, 'theme', 'names'))

    def theme_use(self, themename=None):
        if themename is None:
            return self.tk.eval('return $ttk::currentTheme')
        else:
            self.tk.call('ttk::setTheme', themename)
            return


class Widget(Tkinter.Widget):

    def __init__(self, master, widgetname, kw=None):
        master = setup_master(master)
        if not getattr(master, '_tile_loaded', False):
            _load_tile(master)
        Tkinter.Widget.__init__(self, master, widgetname, kw=kw)

    def identify(self, x, y):
        return self.tk.call(self._w, 'identify', x, y)

    def instate(self, statespec, callback=None, *args, **kw):
        ret = self.tk.getboolean(self.tk.call(self._w, 'instate', ' '.join(statespec)))
        return callback(*args, **kw) if ret and callback else ret

    def state(self, statespec=None):
        if statespec is not None:
            statespec = ' '.join(statespec)
        return self.tk.splitlist(str(self.tk.call(self._w, 'state', statespec)))


class Button(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::button', kw)

    def invoke(self):
        return self.tk.call(self._w, 'invoke')


class Checkbutton(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::checkbutton', kw)

    def invoke(self):
        return self.tk.call(self._w, 'invoke')


class Entry(Widget, Tkinter.Entry):

    def __init__(self, master=None, widget=None, **kw):
        Widget.__init__(self, master, widget or 'ttk::entry', kw)

    def bbox(self, index):
        return self._getints(self.tk.call(self._w, 'bbox', index))

    def identify(self, x, y):
        return self.tk.call(self._w, 'identify', x, y)

    def validate(self):
        return self.tk.getboolean(self.tk.call(self._w, 'validate'))


class Combobox(Entry):

    def __init__(self, master=None, **kw):
        Entry.__init__(self, master, 'ttk::combobox', **kw)

    def current(self, newindex=None):
        return self.tk.getint(self.tk.call(self._w, 'current')) if newindex is None else self.tk.call(self._w, 'current', newindex)

    def set(self, value):
        self.tk.call(self._w, 'set', value)


class Frame(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::frame', kw)


class Label(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::label', kw)


class Labelframe(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::labelframe', kw)


LabelFrame = Labelframe

class Menubutton(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::menubutton', kw)


class Notebook(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::notebook', kw)

    def add(self, child, **kw):
        self.tk.call(self._w, 'add', child, *_format_optdict(kw))

    def forget(self, tab_id):
        self.tk.call(self._w, 'forget', tab_id)

    def hide(self, tab_id):
        self.tk.call(self._w, 'hide', tab_id)

    def identify(self, x, y):
        return self.tk.call(self._w, 'identify', x, y)

    def index(self, tab_id):
        return self.tk.getint(self.tk.call(self._w, 'index', tab_id))

    def insert(self, pos, child, **kw):
        self.tk.call(self._w, 'insert', pos, child, *_format_optdict(kw))

    def select(self, tab_id=None):
        return self.tk.call(self._w, 'select', tab_id)

    def tab(self, tab_id, option=None, **kw):
        if option is not None:
            kw[option] = None
        return _val_or_dict(self.tk, kw, self._w, 'tab', tab_id)

    def tabs(self):
        return self.tk.splitlist(self.tk.call(self._w, 'tabs') or ())

    def enable_traversal(self):
        self.tk.call('ttk::notebook::enableTraversal', self._w)


class Panedwindow(Widget, Tkinter.PanedWindow):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::panedwindow', kw)

    forget = Tkinter.PanedWindow.forget

    def insert(self, pos, child, **kw):
        self.tk.call(self._w, 'insert', pos, child, *_format_optdict(kw))

    def pane(self, pane, option=None, **kw):
        if option is not None:
            kw[option] = None
        return _val_or_dict(self.tk, kw, self._w, 'pane', pane)

    def sashpos(self, index, newpos=None):
        return self.tk.getint(self.tk.call(self._w, 'sashpos', index, newpos))


PanedWindow = Panedwindow

class Progressbar(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::progressbar', kw)

    def start(self, interval=None):
        self.tk.call(self._w, 'start', interval)

    def step(self, amount=None):
        self.tk.call(self._w, 'step', amount)

    def stop(self):
        self.tk.call(self._w, 'stop')


class Radiobutton(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::radiobutton', kw)

    def invoke(self):
        return self.tk.call(self._w, 'invoke')


class Scale(Widget, Tkinter.Scale):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::scale', kw)

    def configure(self, cnf=None, **kw):
        if cnf:
            kw.update(cnf)
        Widget.configure(self, **kw)
        if any(['from' in kw, 'from_' in kw, 'to' in kw]):
            self.event_generate('<<RangeChanged>>')

    def get(self, x=None, y=None):
        return self.tk.call(self._w, 'get', x, y)


class Scrollbar(Widget, Tkinter.Scrollbar):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::scrollbar', kw)


class Separator(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::separator', kw)


class Sizegrip(Widget):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::sizegrip', kw)


class Treeview(Widget, Tkinter.XView, Tkinter.YView):

    def __init__(self, master=None, **kw):
        Widget.__init__(self, master, 'ttk::treeview', kw)

    def bbox(self, item, column=None):
        return self._getints(self.tk.call(self._w, 'bbox', item, column)) or ''

    def get_children(self, item=None):
        return self.tk.splitlist(self.tk.call(self._w, 'children', item or '') or ())

    def set_children(self, item, *newchildren):
        self.tk.call(self._w, 'children', item, newchildren)

    def column(self, column, option=None, **kw):
        if option is not None:
            kw[option] = None
        return _val_or_dict(self.tk, kw, self._w, 'column', column)

    def delete(self, *items):
        self.tk.call(self._w, 'delete', items)

    def detach(self, *items):
        self.tk.call(self._w, 'detach', items)

    def exists(self, item):
        return self.tk.getboolean(self.tk.call(self._w, 'exists', item))

    def focus(self, item=None):
        return self.tk.call(self._w, 'focus', item)

    def heading(self, column, option=None, **kw):
        cmd = kw.get('command')
        if cmd and not isinstance(cmd, basestring):
            kw['command'] = self.master.register(cmd, self._substitute)
        if option is not None:
            kw[option] = None
        return _val_or_dict(self.tk, kw, self._w, 'heading', column)

    def identify(self, component, x, y):
        return self.tk.call(self._w, 'identify', component, x, y)

    def identify_row(self, y):
        return self.identify('row', 0, y)

    def identify_column(self, x):
        return self.identify('column', x, 0)

    def identify_region(self, x, y):
        return self.identify('region', x, y)

    def identify_element(self, x, y):
        return self.identify('element', x, y)

    def index(self, item):
        return self.tk.getint(self.tk.call(self._w, 'index', item))

    def insert(self, parent, index, iid=None, **kw):
        opts = _format_optdict(kw)
        if iid is not None:
            res = self.tk.call(self._w, 'insert', parent, index, '-id', iid, *opts)
        else:
            res = self.tk.call(self._w, 'insert', parent, index, *opts)
        return res

    def item(self, item, option=None, **kw):
        if option is not None:
            kw[option] = None
        return _val_or_dict(self.tk, kw, self._w, 'item', item)

    def move(self, item, parent, index):
        self.tk.call(self._w, 'move', item, parent, index)

    reattach = move

    def next(self, item):
        return self.tk.call(self._w, 'next', item)

    def parent(self, item):
        return self.tk.call(self._w, 'parent', item)

    def prev(self, item):
        return self.tk.call(self._w, 'prev', item)

    def see(self, item):
        self.tk.call(self._w, 'see', item)

    def selection(self, selop=None, items=None):
        if isinstance(items, basestring):
            items = (items,)
        return self.tk.splitlist(self.tk.call(self._w, 'selection', selop, items))

    def selection_set(self, items):
        self.selection('set', items)

    def selection_add(self, items):
        self.selection('add', items)

    def selection_remove(self, items):
        self.selection('remove', items)

    def selection_toggle(self, items):
        self.selection('toggle', items)

    def set(self, item, column=None, value=None):
        res = self.tk.call(self._w, 'set', item, column, value)
        if column is None and value is None:
            return _splitdict(self.tk, res, cut_minus=False, conv=_tclobj_to_py)
        else:
            return res
            return

    def tag_bind(self, tagname, sequence=None, callback=None):
        self._bind((self._w,
         'tag',
         'bind',
         tagname), sequence, callback, add=0)

    def tag_configure(self, tagname, option=None, **kw):
        if option is not None:
            kw[option] = None
        return _val_or_dict(self.tk, kw, self._w, 'tag', 'configure', tagname)

    def tag_has(self, tagname, item=None):
        if item is None:
            return self.tk.splitlist(self.tk.call(self._w, 'tag', 'has', tagname))
        else:
            return self.tk.getboolean(self.tk.call(self._w, 'tag', 'has', tagname, item))
            return


class LabeledScale(Frame, object):

    def __init__(self, master=None, variable=None, from_=0, to=10, **kw):
        self._label_top = kw.pop('compound', 'top') == 'top'
        Frame.__init__(self, master, **kw)
        self._variable = variable or Tkinter.IntVar(master)
        self._variable.set(from_)
        self._last_valid = from_
        self.label = Label(self)
        self.scale = Scale(self, variable=self._variable, from_=from_, to=to)
        self.scale.bind('<<RangeChanged>>', self._adjust)
        scale_side = 'bottom' if self._label_top else 'top'
        label_side = 'top' if scale_side == 'bottom' else 'bottom'
        self.scale.pack(side=scale_side, fill='x')
        tmp = Label(self).pack(side=label_side)
        self.label.place(anchor='n' if label_side == 'top' else 's')
        self.__tracecb = self._variable.trace_variable('w', self._adjust)
        self.bind('<Configure>', self._adjust)
        self.bind('<Map>', self._adjust)

    def destroy(self):
        try:
            self._variable.trace_vdelete('w', self.__tracecb)
        except AttributeError:
            pass
        else:
            del self._variable

        Frame.destroy(self)
        self.label = None
        self.scale = None
        return

    def _adjust(self, *args):

        def adjust_label():
            self.update_idletasks()
            x, y = self.scale.coords()
            if self._label_top:
                y = self.scale.winfo_y() - self.label.winfo_reqheight()
            else:
                y = self.scale.winfo_reqheight() + self.label.winfo_reqheight()
            self.label.place_configure(x=x, y=y)

        from_ = _to_number(self.scale['from'])
        to = _to_number(self.scale['to'])
        if to < from_:
            from_, to = to, from_
        newval = self._variable.get()
        if not from_ <= newval <= to:
            self.value = self._last_valid
            return
        self._last_valid = newval
        self.label['text'] = newval
        self.after_idle(adjust_label)

    def _get_value(self):
        return self._variable.get()

    def _set_value(self, val):
        self._variable.set(val)

    value = property(_get_value, _set_value)


class OptionMenu(Menubutton):

    def __init__(self, master, variable, default=None, *values, **kwargs):
        kw = {'textvariable': variable,
         'style': kwargs.pop('style', None),
         'direction': kwargs.pop('direction', None)}
        Menubutton.__init__(self, master, **kw)
        self['menu'] = Tkinter.Menu(self, tearoff=False)
        self._variable = variable
        self._callback = kwargs.pop('command', None)
        if kwargs:
            raise Tkinter.TclError('unknown option -%s' % kwargs.iterkeys().next())
        self.set_menu(default, *values)
        return

    def __getitem__(self, item):
        return self.nametowidget(Menubutton.__getitem__(self, item)) if item == 'menu' else Menubutton.__getitem__(self, item)

    def set_menu(self, default=None, *values):
        menu = self['menu']
        menu.delete(0, 'end')
        for val in values:
            menu.add_radiobutton(label=val, command=Tkinter._setit(self._variable, val, self._callback), variable=self._variable)

        if default:
            self._variable.set(default)

    def destroy(self):
        try:
            del self._variable
        except AttributeError:
            pass

        Menubutton.destroy(self)
