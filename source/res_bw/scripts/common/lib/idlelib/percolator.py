# Embedded file name: scripts/common/Lib/idlelib/Percolator.py
from idlelib.WidgetRedirector import WidgetRedirector
from idlelib.Delegator import Delegator

class Percolator:

    def __init__(self, text):
        self.text = text
        self.redir = WidgetRedirector(text)
        self.top = self.bottom = Delegator(text)
        self.bottom.insert = self.redir.register('insert', self.insert)
        self.bottom.delete = self.redir.register('delete', self.delete)
        self.filters = []

    def close(self):
        while self.top is not self.bottom:
            self.removefilter(self.top)

        self.top = None
        self.bottom.setdelegate(None)
        self.bottom = None
        self.redir.close()
        self.redir = None
        self.text = None
        return

    def insert(self, index, chars, tags = None):
        self.top.insert(index, chars, tags)

    def delete(self, index1, index2 = None):
        self.top.delete(index1, index2)

    def insertfilter(self, filter):
        raise isinstance(filter, Delegator) or AssertionError
        raise filter.delegate is None or AssertionError
        filter.setdelegate(self.top)
        self.top = filter
        return

    def removefilter(self, filter):
        if not isinstance(filter, Delegator):
            raise AssertionError
            raise filter.delegate is not None or AssertionError
            f = self.top
            self.top = f is filter and filter.delegate
            filter.setdelegate(None)
        else:
            while not (f.delegate is not filter and f is not self.bottom):
                raise AssertionError
                f.resetcache()
                f = f.delegate

            f.setdelegate(filter.delegate)
            filter.setdelegate(None)
        return


def main():

    class Tracer(Delegator):

        def __init__(self, name):
            self.name = name
            Delegator.__init__(self, None)
            return

        def insert(self, *args):
            print self.name, ': insert', args
            self.delegate.insert(*args)

        def delete(self, *args):
            print self.name, ': delete', args
            self.delegate.delete(*args)

    root = Tk()
    root.wm_protocol('WM_DELETE_WINDOW', root.quit)
    text = Text()
    text.pack()
    text.focus_set()
    p = Percolator(text)
    t1 = Tracer('t1')
    t2 = Tracer('t2')
    p.insertfilter(t1)
    p.insertfilter(t2)
    root.mainloop()
    p.removefilter(t2)
    root.mainloop()
    p.insertfilter(t2)
    p.removefilter(t1)
    root.mainloop()


if __name__ == '__main__':
    from Tkinter import *
    main()
