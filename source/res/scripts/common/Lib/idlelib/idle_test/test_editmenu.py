# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle_test/test_editmenu.py
from test.test_support import requires
import Tkinter as tk
import unittest
from idlelib import PyShell

class PasteTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = root = tk.Tk()
        root.withdraw()
        PyShell.fix_x11_paste(root)
        cls.text = tk.Text(root)
        cls.entry = tk.Entry(root)
        cls.spin = tk.Spinbox(root)
        root.clipboard_clear()
        root.clipboard_append('two')

    @classmethod
    def tearDownClass(cls):
        del cls.text
        del cls.entry
        del cls.spin
        cls.root.clipboard_clear()
        cls.root.update_idletasks()
        cls.root.update()
        cls.root.destroy()
        del cls.root

    def test_paste_text_no_selection(self):
        text = self.text
        tag, ans = ('', 'onetwo\n')
        text.delete('1.0', 'end')
        text.insert('1.0', 'one', tag)
        text.event_generate('<<Paste>>')
        self.assertEqual(text.get('1.0', 'end'), ans)

    def test_paste_text_selection(self):
        text = self.text
        tag, ans = ('sel', 'two\n')
        text.delete('1.0', 'end')
        text.insert('1.0', 'one', tag)
        text.event_generate('<<Paste>>')
        self.assertEqual(text.get('1.0', 'end'), ans)

    def test_paste_entry_no_selection(self):
        entry = self.entry
        end, ans = (0, 'onetwo')
        entry.delete(0, 'end')
        entry.insert(0, 'one')
        entry.select_range(0, end)
        entry.event_generate('<<Paste>>')
        self.assertEqual(entry.get(), ans)

    def test_paste_entry_selection(self):
        entry = self.entry
        end, ans = ('end', 'two')
        entry.delete(0, 'end')
        entry.insert(0, 'one')
        entry.select_range(0, end)
        entry.event_generate('<<Paste>>')
        self.assertEqual(entry.get(), ans)

    def test_paste_spin_no_selection(self):
        spin = self.spin
        end, ans = (0, 'onetwo')
        spin.delete(0, 'end')
        spin.insert(0, 'one')
        spin.selection('range', 0, end)
        spin.event_generate('<<Paste>>')
        self.assertEqual(spin.get(), ans)

    def test_paste_spin_selection(self):
        spin = self.spin
        end, ans = ('end', 'two')
        spin.delete(0, 'end')
        spin.insert(0, 'one')
        spin.selection('range', 0, end)
        spin.event_generate('<<Paste>>')
        self.assertEqual(spin.get(), ans)


if __name__ == '__main__':
    unittest.main(verbosity=2)
