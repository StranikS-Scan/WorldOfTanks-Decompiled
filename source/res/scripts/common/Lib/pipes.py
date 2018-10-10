# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/pipes.py
import re
import os
import tempfile
import string
__all__ = ['Template']
FILEIN_FILEOUT = 'ff'
STDIN_FILEOUT = '-f'
FILEIN_STDOUT = 'f-'
STDIN_STDOUT = '--'
SOURCE = '.-'
SINK = '-.'
stepkinds = [FILEIN_FILEOUT,
 STDIN_FILEOUT,
 FILEIN_STDOUT,
 STDIN_STDOUT,
 SOURCE,
 SINK]

class Template:

    def __init__(self):
        self.debugging = 0
        self.reset()

    def __repr__(self):
        return '<Template instance, steps=%r>' % (self.steps,)

    def reset(self):
        self.steps = []

    def clone(self):
        t = Template()
        t.steps = self.steps[:]
        t.debugging = self.debugging
        return t

    def debug(self, flag):
        self.debugging = flag

    def append(self, cmd, kind):
        if type(cmd) is not type(''):
            raise TypeError, 'Template.append: cmd must be a string'
        if kind not in stepkinds:
            raise ValueError, 'Template.append: bad kind %r' % (kind,)
        if kind == SOURCE:
            raise ValueError, 'Template.append: SOURCE can only be prepended'
        if self.steps and self.steps[-1][1] == SINK:
            raise ValueError, 'Template.append: already ends with SINK'
        if kind[0] == 'f' and not re.search('\\$IN\\b', cmd):
            raise ValueError, 'Template.append: missing $IN in cmd'
        if kind[1] == 'f' and not re.search('\\$OUT\\b', cmd):
            raise ValueError, 'Template.append: missing $OUT in cmd'
        self.steps.append((cmd, kind))

    def prepend(self, cmd, kind):
        if type(cmd) is not type(''):
            raise TypeError, 'Template.prepend: cmd must be a string'
        if kind not in stepkinds:
            raise ValueError, 'Template.prepend: bad kind %r' % (kind,)
        if kind == SINK:
            raise ValueError, 'Template.prepend: SINK can only be appended'
        if self.steps and self.steps[0][1] == SOURCE:
            raise ValueError, 'Template.prepend: already begins with SOURCE'
        if kind[0] == 'f' and not re.search('\\$IN\\b', cmd):
            raise ValueError, 'Template.prepend: missing $IN in cmd'
        if kind[1] == 'f' and not re.search('\\$OUT\\b', cmd):
            raise ValueError, 'Template.prepend: missing $OUT in cmd'
        self.steps.insert(0, (cmd, kind))

    def open(self, file, rw):
        if rw == 'r':
            return self.open_r(file)
        if rw == 'w':
            return self.open_w(file)
        raise ValueError, "Template.open: rw must be 'r' or 'w', not %r" % (rw,)

    def open_r(self, file):
        if not self.steps:
            return open(file, 'r')
        if self.steps[-1][1] == SINK:
            raise ValueError, 'Template.open_r: pipeline ends width SINK'
        cmd = self.makepipeline(file, '')
        return os.popen(cmd, 'r')

    def open_w(self, file):
        if not self.steps:
            return open(file, 'w')
        if self.steps[0][1] == SOURCE:
            raise ValueError, 'Template.open_w: pipeline begins with SOURCE'
        cmd = self.makepipeline('', file)
        return os.popen(cmd, 'w')

    def copy(self, infile, outfile):
        return os.system(self.makepipeline(infile, outfile))

    def makepipeline(self, infile, outfile):
        cmd = makepipeline(infile, self.steps, outfile)
        if self.debugging:
            print cmd
            cmd = 'set -x; ' + cmd
        return cmd


def makepipeline(infile, steps, outfile):
    list = []
    for cmd, kind in steps:
        list.append(['',
         cmd,
         kind,
         ''])

    if not list:
        list.append(['',
         'cat',
         '--',
         ''])
    cmd, kind = list[0][1:3]
    if kind[0] == 'f' and not infile:
        list.insert(0, ['',
         'cat',
         '--',
         ''])
    list[0][0] = infile
    cmd, kind = list[-1][1:3]
    if kind[1] == 'f' and not outfile:
        list.append(['',
         'cat',
         '--',
         ''])
    list[-1][-1] = outfile
    garbage = []
    for i in range(1, len(list)):
        lkind = list[i - 1][2]
        rkind = list[i][2]
        if lkind[1] == 'f' or rkind[0] == 'f':
            fd, temp = tempfile.mkstemp()
            os.close(fd)
            garbage.append(temp)
            list[i - 1][-1] = list[i][0] = temp

    for item in list:
        inf, cmd, kind, outf = item
        if kind[1] == 'f':
            cmd = 'OUT=' + quote(outf) + '; ' + cmd
        if kind[0] == 'f':
            cmd = 'IN=' + quote(inf) + '; ' + cmd
        if kind[0] == '-' and inf:
            cmd = cmd + ' <' + quote(inf)
        if kind[1] == '-' and outf:
            cmd = cmd + ' >' + quote(outf)
        item[1] = cmd

    cmdlist = list[0][1]
    for item in list[1:]:
        cmd, kind = item[1:3]
        if item[0] == '':
            if 'f' in kind:
                cmd = '{ ' + cmd + '; }'
            cmdlist = cmdlist + ' |\n' + cmd
        cmdlist = cmdlist + '\n' + cmd

    if garbage:
        rmcmd = 'rm -f'
        for file in garbage:
            rmcmd = rmcmd + ' ' + quote(file)

        trapcmd = 'trap ' + quote(rmcmd + '; exit') + ' 1 2 3 13 14 15'
        cmdlist = trapcmd + '\n' + cmdlist + '\n' + rmcmd
    return cmdlist


_safechars = frozenset(string.ascii_letters + string.digits + '@%_-+=:,./')

def quote(file):
    for c in file:
        if c not in _safechars:
            break
    else:
        if not file:
            return "''"
        return file

    return "'" + file.replace("'", '\'"\'"\'') + "'"
