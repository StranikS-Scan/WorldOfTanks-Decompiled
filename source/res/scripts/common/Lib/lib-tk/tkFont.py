# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib-tk/tkFont.py
__version__ = '0.9'
import Tkinter
NORMAL = 'normal'
ROMAN = 'roman'
BOLD = 'bold'
ITALIC = 'italic'

def nametofont(name):
    return Font(name=name, exists=True)


class Font:

    def _set(self, kw):
        options = []
        for k, v in kw.items():
            options.append('-' + k)
            options.append(str(v))

        return tuple(options)

    def _get(self, args):
        options = []
        for k in args:
            options.append('-' + k)

        return tuple(options)

    def _mkdict(self, args):
        options = {}
        for i in range(0, len(args), 2):
            options[args[i][1:]] = args[i + 1]

        return options

    def __init__(self, root=None, font=None, name=None, exists=False, **options):
        if not root:
            root = Tkinter._default_root
        if font:
            font = root.tk.splitlist(root.tk.call('font', 'actual', font))
        else:
            font = self._set(options)
        if not name:
            name = 'font' + str(id(self))
        self.name = name
        if exists:
            self.delete_font = False
            if self.name not in root.tk.call('font', 'names'):
                raise Tkinter._tkinter.TclError, 'named font %s does not already exist' % (self.name,)
            if font:
                root.tk.call('font', 'configure', self.name, *font)
        else:
            root.tk.call('font', 'create', self.name, *font)
            self.delete_font = True
        self._root = root
        self._split = root.tk.splitlist
        self._call = root.tk.call

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and isinstance(other, Font)

    def __getitem__(self, key):
        return self.cget(key)

    def __setitem__(self, key, value):
        self.configure(**{key: value})

    def __del__(self):
        try:
            if self.delete_font:
                self._call('font', 'delete', self.name)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            pass

    def copy(self):
        return Font(self._root, **self.actual())

    def actual(self, option=None):
        if option:
            return self._call('font', 'actual', self.name, '-' + option)
        else:
            return self._mkdict(self._split(self._call('font', 'actual', self.name)))

    def cget(self, option):
        return self._call('font', 'config', self.name, '-' + option)

    def config(self, **options):
        if options:
            self._call('font', 'config', self.name, *self._set(options))
        else:
            return self._mkdict(self._split(self._call('font', 'config', self.name)))

    configure = config

    def measure(self, text):
        return int(self._call('font', 'measure', self.name, text))

    def metrics(self, *options):
        if options:
            return int(self._call('font', 'metrics', self.name, self._get(options)))
        else:
            res = self._split(self._call('font', 'metrics', self.name))
            options = {}
            for i in range(0, len(res), 2):
                options[res[i][1:]] = int(res[i + 1])

            return options


def families(root=None):
    if not root:
        root = Tkinter._default_root
    return root.tk.splitlist(root.tk.call('font', 'families'))


def names(root=None):
    if not root:
        root = Tkinter._default_root
    return root.tk.splitlist(root.tk.call('font', 'names'))


if __name__ == '__main__':
    root = Tkinter.Tk()
    f = Font(family='times', size=30, weight=NORMAL)
    print f.actual()
    print f.actual('family')
    print f.actual('weight')
    print f.config()
    print f.cget('family')
    print f.cget('weight')
    print names()
    print f.measure('hello'), f.metrics('linespace')
    print f.metrics()
    f = Font(font=('Courier', 20, 'bold'))
    print f.measure('hello'), f.metrics('linespace')
    w = Tkinter.Label(root, text='Hello, world', font=f)
    w.pack()
    w = Tkinter.Button(root, text='Quit!', command=root.destroy)
    w.pack()
    fb = Font(font=w['font']).copy()
    fb.config(weight=BOLD)
    w.config(font=fb)
    Tkinter.mainloop()
