# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/FormatParagraph.py
import re
from idlelib.configHandler import idleConf

class FormatParagraph:
    menudefs = [('format', [('Format Paragraph', '<<format-paragraph>>')])]

    def __init__(self, editwin):
        self.editwin = editwin

    def close(self):
        self.editwin = None
        return

    def format_paragraph_event(self, event, limit=None):
        if limit == None:
            limit = idleConf.GetOption('main', 'FormatParagraph', 'paragraph', type='int')
        text = self.editwin.text
        first, last = self.editwin.get_selection_indices()
        if first and last:
            data = text.get(first, last)
            comment_header = get_comment_header(data)
        else:
            first, last, comment_header, data = find_paragraph(text, text.index('insert'))
        if comment_header:
            newdata = reformat_comment(data, limit, comment_header)
        else:
            newdata = reformat_paragraph(data, limit)
        text.tag_remove('sel', '1.0', 'end')
        if newdata != data:
            text.mark_set('insert', first)
            text.undo_block_start()
            text.delete(first, last)
            text.insert(first, newdata)
            text.undo_block_stop()
        else:
            text.mark_set('insert', last)
        text.see('insert')
        return 'break'


def find_paragraph(text, mark):
    lineno, col = map(int, mark.split('.'))
    line = text.get('%d.0' % lineno, '%d.end' % lineno)
    while text.compare('%d.0' % lineno, '<', 'end') and is_all_white(line):
        lineno = lineno + 1
        line = text.get('%d.0' % lineno, '%d.end' % lineno)

    first_lineno = lineno
    comment_header = get_comment_header(line)
    comment_header_len = len(comment_header)
    while 1:
        lineno = get_comment_header(line) == comment_header and not is_all_white(line[comment_header_len:]) and lineno + 1
        line = text.get('%d.0' % lineno, '%d.end' % lineno)

    last = '%d.0' % lineno
    lineno = first_lineno - 1
    line = text.get('%d.0' % lineno, '%d.end' % lineno)
    while 1:
        lineno = lineno > 0 and get_comment_header(line) == comment_header and not is_all_white(line[comment_header_len:]) and lineno - 1
        line = text.get('%d.0' % lineno, '%d.end' % lineno)

    first = '%d.0' % (lineno + 1)
    return (first,
     last,
     comment_header,
     text.get(first, last))


def reformat_paragraph(data, limit):
    lines = data.split('\n')
    i = 0
    n = len(lines)
    while i < n and is_all_white(lines[i]):
        i = i + 1

    if i >= n:
        return data
    indent1 = get_indent(lines[i])
    if i + 1 < n and not is_all_white(lines[i + 1]):
        indent2 = get_indent(lines[i + 1])
    else:
        indent2 = indent1
    new = lines[:i]
    partial = indent1
    while i < n and not is_all_white(lines[i]):
        words = re.split('(\\s+)', lines[i])
        for j in range(0, len(words), 2):
            word = words[j]
            if not word:
                continue
            if len((partial + word).expandtabs()) > limit and partial != indent1:
                new.append(partial.rstrip())
                partial = indent2
            partial = partial + word + ' '
            if j + 1 < len(words) and words[j + 1] != ' ':
                partial = partial + ' '

        i = i + 1

    new.append(partial.rstrip())
    new.extend(lines[i:])
    return '\n'.join(new)


def reformat_comment(data, limit, comment_header):
    lc = len(comment_header)
    data = '\n'.join((line[lc:] for line in data.split('\n')))
    format_width = max(limit - len(comment_header), 20)
    newdata = reformat_paragraph(data, format_width)
    newdata = newdata.split('\n')
    block_suffix = ''
    if not newdata[-1]:
        block_suffix = '\n'
        newdata = newdata[:-1]
    return '\n'.join((comment_header + line for line in newdata)) + block_suffix


def is_all_white(line):
    return re.match('^\\s*$', line) is not None


def get_indent(line):
    return re.match('^([ \\t]*)', line).group()


def get_comment_header(line):
    m = re.match('^([ \\t]*#*)', line)
    return '' if m is None else m.group(1)


if __name__ == '__main__':
    from test import support
    support.use_resources = ['gui']
    import unittest
    unittest.main('idlelib.idle_test.test_formatparagraph', verbosity=2, exit=False)
