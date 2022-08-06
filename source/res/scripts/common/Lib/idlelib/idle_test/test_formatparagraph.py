# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle_test/test_formatparagraph.py
import unittest
from idlelib import FormatParagraph as fp
from idlelib.EditorWindow import EditorWindow
from Tkinter import Tk, Text
from test.test_support import requires

class Is_Get_Test(unittest.TestCase):
    test_comment = '# This is a comment'
    test_nocomment = 'This is not a comment'
    trailingws_comment = '# This is a comment   '
    leadingws_comment = '    # This is a comment'
    leadingws_nocomment = '    This is not a comment'

    def test_is_all_white(self):
        self.assertTrue(fp.is_all_white(''))
        self.assertTrue(fp.is_all_white('\t\n\r\x0c\x0b'))
        self.assertFalse(fp.is_all_white(self.test_comment))

    def test_get_indent(self):
        Equal = self.assertEqual
        Equal(fp.get_indent(self.test_comment), '')
        Equal(fp.get_indent(self.trailingws_comment), '')
        Equal(fp.get_indent(self.leadingws_comment), '    ')
        Equal(fp.get_indent(self.leadingws_nocomment), '    ')

    def test_get_comment_header(self):
        Equal = self.assertEqual
        Equal(fp.get_comment_header(self.test_comment), '#')
        Equal(fp.get_comment_header(self.trailingws_comment), '#')
        Equal(fp.get_comment_header(self.leadingws_comment), '    #')
        Equal(fp.get_comment_header(self.leadingws_nocomment), '    ')
        Equal(fp.get_comment_header(self.test_nocomment), '')


class FindTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from idlelib.idle_test.mock_tk import Text
        cls.text = Text()

    def runcase(self, inserttext, stopline, expected):
        text = self.text
        text.insert('1.0', inserttext)
        for line in range(1, stopline):
            linelength = int(text.index('%d.end' % line).split('.')[1])
            for col in (0, linelength // 2, linelength):
                tempindex = '%d.%d' % (line, col)
                self.assertEqual(fp.find_paragraph(text, tempindex), expected)

        text.delete('1.0', 'end')

    def test_find_comment(self):
        comment = '# Comment block with no blank lines before\n# Comment line\n\n'
        self.runcase(comment, 3, ('1.0',
         '3.0',
         '#',
         comment[0:58]))
        comment = '\n# Comment block with whitespace line before and after\n# Comment line\n\n'
        self.runcase(comment, 4, ('2.0',
         '4.0',
         '#',
         comment[1:70]))
        comment = '\n    # Indented comment block with whitespace before and after\n    # Comment line\n\n'
        self.runcase(comment, 4, ('2.0',
         '4.0',
         '    #',
         comment[1:82]))
        comment = '\n# Single line comment\n\n'
        self.runcase(comment, 3, ('2.0',
         '3.0',
         '#',
         comment[1:23]))
        comment = '\n    # Single line comment with leading whitespace\n\n'
        self.runcase(comment, 3, ('2.0',
         '3.0',
         '    #',
         comment[1:51]))
        comment = '\n# Comment immediately followed by code\nx = 42\n\n'
        self.runcase(comment, 3, ('2.0',
         '3.0',
         '#',
         comment[1:40]))
        comment = '\n    # Indented comment immediately followed by code\nx = 42\n\n'
        self.runcase(comment, 3, ('2.0',
         '3.0',
         '    #',
         comment[1:53]))
        comment = '\n# Comment immediately followed by indented code\n    x = 42\n\n'
        self.runcase(comment, 3, ('2.0',
         '3.0',
         '#',
         comment[1:49]))

    def test_find_paragraph(self):
        teststring = '"""String with no blank lines before\nString line\n"""\n\n'
        self.runcase(teststring, 4, ('1.0',
         '4.0',
         '',
         teststring[0:53]))
        teststring = '\n"""String with whitespace line before and after\nString line.\n"""\n\n'
        self.runcase(teststring, 5, ('2.0',
         '5.0',
         '',
         teststring[1:66]))
        teststring = '\n    """Indented string with whitespace before and after\n    Comment string.\n    """\n\n'
        self.runcase(teststring, 5, ('2.0',
         '5.0',
         '    ',
         teststring[1:85]))
        teststring = '\n"""Single line string."""\n\n'
        self.runcase(teststring, 3, ('2.0',
         '3.0',
         '',
         teststring[1:27]))
        teststring = '\n    """Single line string with leading whitespace."""\n\n'
        self.runcase(teststring, 3, ('2.0',
         '3.0',
         '    ',
         teststring[1:55]))


class ReformatFunctionTest(unittest.TestCase):

    def test_reformat_paragraph(self):
        Equal = self.assertEqual
        reform = fp.reformat_paragraph
        hw = 'O hello world'
        Equal(reform(' ', 1), ' ')
        Equal(reform('Hello    world', 20), 'Hello  world')
        Equal(reform(hw, 1), 'O\nhello\nworld')
        Equal(reform(hw, 6), 'O\nhello\nworld')
        Equal(reform(hw, 7), 'O hello\nworld')
        Equal(reform(hw, 12), 'O hello\nworld')
        Equal(reform(hw, 13), 'O hello world')
        hw = '\nO hello world'
        Equal(reform(hw, 1), '\nO\nhello\nworld')
        Equal(reform(hw, 6), '\nO\nhello\nworld')
        Equal(reform(hw, 7), '\nO hello\nworld')
        Equal(reform(hw, 12), '\nO hello\nworld')
        Equal(reform(hw, 13), '\nO hello world')


class ReformatCommentTest(unittest.TestCase):

    def test_reformat_comment(self):
        Equal = self.assertEqual
        test_string = '    """this is a test of a reformat for a triple quoted string will it reformat to less than 70 characters for me?"""'
        result = fp.reformat_comment(test_string, 70, '    ')
        expected = '    """this is a test of a reformat for a triple quoted string will it\n    reformat to less than 70 characters for me?"""'
        Equal(result, expected)
        test_comment = '# this is a test of a reformat for a triple quoted string will it reformat to less than 70 characters for me?'
        result = fp.reformat_comment(test_comment, 70, '#')
        expected = '# this is a test of a reformat for a triple quoted string will it\n# reformat to less than 70 characters for me?'
        Equal(result, expected)


class FormatClassTest(unittest.TestCase):

    def test_init_close(self):
        instance = fp.FormatParagraph('editor')
        self.assertEqual(instance.editwin, 'editor')
        instance.close()
        self.assertEqual(instance.editwin, None)
        return


class TextWrapper:

    def __init__(self, master):
        self.text = Text(master=master)

    def __getattr__(self, name):
        return getattr(self.text, name)

    def undo_block_start(self):
        pass

    def undo_block_stop(self):
        pass


class Editor:

    def __init__(self, root):
        self.text = TextWrapper(root)

    get_selection_indices = EditorWindow.get_selection_indices.im_func


class FormatEventTest(unittest.TestCase):
    test_string = "    '''this is a test of a reformat for a triple quoted string will it reformat to less than 70 characters for me?'''\n"
    multiline_test_string = "    '''The first line is under the max width.\n    The second line's length is way over the max width. It goes on and on until it is over 100 characters long.\n    Same thing with the third line. It is also way over the max width, but FormatParagraph will fix it.\n    '''\n"
    multiline_test_comment = "# The first line is under the max width.\n# The second line's length is way over the max width. It goes on and on until it is over 100 characters long.\n# Same thing with the third line. It is also way over the max width, but FormatParagraph will fix it.\n# The fourth line is short like the first line."

    @classmethod
    def setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        editor = Editor(root=cls.root)
        cls.text = editor.text.text
        cls.formatter = fp.FormatParagraph(editor).format_paragraph_event

    @classmethod
    def tearDownClass(cls):
        del cls.text
        del cls.formatter
        cls.root.destroy()
        del cls.root

    def test_short_line(self):
        self.text.insert('1.0', 'Short line\n')
        self.formatter('Dummy')
        self.assertEqual(self.text.get('1.0', 'insert'), 'Short line\n')
        self.text.delete('1.0', 'end')

    def test_long_line(self):
        text = self.text
        text.insert('1.0', self.test_string)
        text.mark_set('insert', '1.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        expected = "    '''this is a test of a reformat for a triple quoted string will it\n    reformat to less than 70 characters for me?'''\n"
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')
        text.insert('1.0', self.test_string)
        text.tag_add('sel', '1.11', '1.end')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        expected = "    '''this is a test of a reformat for a triple quoted string will it reformat\n to less than 70 characters for me?'''"
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

    def test_multiple_lines(self):
        text = self.text
        text.insert('1.0', self.multiline_test_string)
        text.tag_add('sel', '2.0', '4.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('2.0', 'insert')
        expected = "    The second line's length is way over the max width. It goes on and\n    on until it is over 100 characters long. Same thing with the third\n    line. It is also way over the max width, but FormatParagraph will\n    fix it.\n"
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')

    def test_comment_block(self):
        text = self.text
        text.insert('1.0', self.multiline_test_comment)
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        expected = "# The first line is under the max width. The second line's length is\n# way over the max width. It goes on and on until it is over 100\n# characters long. Same thing with the third line. It is also way over\n# the max width, but FormatParagraph will fix it. The fourth line is\n# short like the first line.\n"
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')
        text.insert('1.0', self.multiline_test_comment)
        text.tag_add('sel', '2.0', '3.0')
        self.formatter('ParameterDoesNothing', limit=70)
        result = text.get('1.0', 'insert')
        expected = "# The first line is under the max width.\n# The second line's length is way over the max width. It goes on and\n# on until it is over 100 characters long.\n"
        self.assertEqual(result, expected)
        text.delete('1.0', 'end')


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
