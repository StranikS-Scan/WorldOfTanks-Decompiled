# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/RstripExtension.py


class RstripExtension:
    menudefs = [('format', [None, ('Strip trailing whitespace', '<<do-rstrip>>')])]

    def __init__(self, editwin):
        self.editwin = editwin
        self.editwin.text.bind('<<do-rstrip>>', self.do_rstrip)

    def do_rstrip(self, event=None):
        text = self.editwin.text
        undo = self.editwin.undo
        undo.undo_block_start()
        end_line = int(float(text.index('end')))
        for cur in range(1, end_line):
            txt = text.get('%i.0' % cur, '%i.end' % cur)
            raw = len(txt)
            cut = len(txt.rstrip())
            if cut < raw:
                text.delete('%i.%i' % (cur, cut), '%i.end' % cur)

        undo.undo_block_stop()


if __name__ == '__main__':
    import unittest
    unittest.main('idlelib.idle_test.test_rstrip', verbosity=2, exit=False)
