# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/IdleHistory.py
from idlelib.configHandler import idleConf

class History:

    def __init__(self, text):
        self.text = text
        self.history = []
        self.prefix = None
        self.pointer = None
        self.cyclic = idleConf.GetOption('main', 'History', 'cyclic', 1, 'bool')
        text.bind('<<history-previous>>', self.history_prev)
        text.bind('<<history-next>>', self.history_next)
        return

    def history_next(self, event):
        self.fetch(reverse=False)

    def history_prev(self, event):
        self.fetch(reverse=True)

    def fetch(self, reverse):
        nhist = len(self.history)
        pointer = self.pointer
        prefix = self.prefix
        if pointer is not None and prefix is not None:
            if self.text.compare('insert', '!=', 'end-1c') or self.text.get('iomark', 'end-1c') != self.history[pointer]:
                pointer = prefix = None
                self.text.mark_set('insert', 'end-1c')
        if pointer is None or prefix is None:
            prefix = self.text.get('iomark', 'end-1c')
            if reverse:
                pointer = nhist
            elif self.cyclic:
                pointer = -1
            else:
                self.text.bell()
                return
        nprefix = len(prefix)
        while 1:
            pointer += -1 if reverse else 1
            if pointer < 0 or pointer >= nhist:
                self.text.bell()
                if not self.cyclic and pointer < 0:
                    return
                if self.text.get('iomark', 'end-1c') != prefix:
                    self.text.delete('iomark', 'end-1c')
                    self.text.insert('iomark', prefix)
                pointer = prefix = None
                break
            item = self.history[pointer]
            if item[:nprefix] == prefix and len(item) > nprefix:
                self.text.delete('iomark', 'end-1c')
                self.text.insert('iomark', item)
                break

        self.text.see('insert')
        self.text.tag_remove('sel', '1.0', 'end')
        self.pointer = pointer
        self.prefix = prefix
        return

    def store(self, source):
        source = source.strip()
        if len(source) > 2:
            try:
                self.history.remove(source)
            except ValueError:
                pass

            self.history.append(source)
        self.pointer = None
        self.prefix = None
        return


if __name__ == '__main__':
    from unittest import main
    main('idlelib.idle_test.test_idlehistory', verbosity=2, exit=False)
