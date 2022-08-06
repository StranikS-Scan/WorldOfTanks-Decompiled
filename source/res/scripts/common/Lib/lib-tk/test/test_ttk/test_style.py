# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib-tk/test/test_ttk/test_style.py
import unittest
import Tkinter as tkinter
import ttk
from test.test_support import requires, run_unittest
from test_ttk.support import AbstractTkTest
requires('gui')

class StyleTest(AbstractTkTest, unittest.TestCase):

    def setUp(self):
        super(StyleTest, self).setUp()
        self.style = ttk.Style(self.root)

    def test_configure(self):
        style = self.style
        style.configure('TButton', background='yellow')
        self.assertEqual(style.configure('TButton', 'background'), 'yellow')
        self.assertIsInstance(style.configure('TButton'), dict)

    def test_map(self):
        style = self.style
        style.map('TButton', background=[('active', 'background', 'blue')])
        self.assertEqual(style.map('TButton', 'background'), [('active', 'background', 'blue')] if self.wantobjects else [('active background', 'blue')])
        self.assertIsInstance(style.map('TButton'), dict)

    def test_lookup(self):
        style = self.style
        style.configure('TButton', background='yellow')
        style.map('TButton', background=[('active', 'background', 'blue')])
        self.assertEqual(style.lookup('TButton', 'background'), 'yellow')
        self.assertEqual(style.lookup('TButton', 'background', ['active', 'background']), 'blue')
        self.assertEqual(style.lookup('TButton', 'optionnotdefined', default='iknewit'), 'iknewit')

    def test_layout(self):
        style = self.style
        self.assertRaises(tkinter.TclError, style.layout, 'NotALayout')
        tv_style = style.layout('Treeview')
        style.layout('Treeview', '')
        self.assertEqual(style.layout('Treeview'), [('null', {'sticky': 'nswe'})])
        style.layout('Treeview', tv_style)
        self.assertEqual(style.layout('Treeview'), tv_style)
        self.assertIsInstance(style.layout('TButton'), list)
        self.assertRaises(tkinter.TclError, style.layout, 'Treeview', [('name', {'option': 'inexistent'})])

    def test_theme_use(self):
        self.assertRaises(tkinter.TclError, self.style.theme_use, 'nonexistingname')
        curr_theme = self.style.theme_use()
        new_theme = None
        for theme in self.style.theme_names():
            if theme != curr_theme:
                new_theme = theme
                self.style.theme_use(theme)
                break
        else:
            return

        self.assertFalse(curr_theme == new_theme)
        self.assertFalse(new_theme != self.style.theme_use())
        self.style.theme_use(curr_theme)
        return


tests_gui = (StyleTest,)
if __name__ == '__main__':
    run_unittest(*tests_gui)
