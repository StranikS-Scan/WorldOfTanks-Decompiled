# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/MimeWriter.py
import mimetools
__all__ = ['MimeWriter']
import warnings
warnings.warn('the MimeWriter module is deprecated; use the email package instead', DeprecationWarning, 2)

class MimeWriter:

    def __init__(self, fp):
        self._fp = fp
        self._headers = []

    def addheader(self, key, value, prefix=0):
        lines = value.split('\n')
        while lines and not lines[-1]:
            del lines[-1]

        while lines and not lines[0]:
            del lines[0]

        for i in range(1, len(lines)):
            lines[i] = '    ' + lines[i].strip()

        value = '\n'.join(lines) + '\n'
        line = key + ': ' + value
        if prefix:
            self._headers.insert(0, line)
        else:
            self._headers.append(line)

    def flushheaders(self):
        self._fp.writelines(self._headers)
        self._headers = []

    def startbody(self, ctype, plist=[], prefix=1):
        for name, value in plist:
            ctype = ctype + ';\n %s="%s"' % (name, value)

        self.addheader('Content-Type', ctype, prefix=prefix)
        self.flushheaders()
        self._fp.write('\n')
        return self._fp

    def startmultipartbody(self, subtype, boundary=None, plist=[], prefix=1):
        self._boundary = boundary or mimetools.choose_boundary()
        return self.startbody('multipart/' + subtype, [('boundary', self._boundary)] + plist, prefix=prefix)

    def nextpart(self):
        self._fp.write('\n--' + self._boundary + '\n')
        return self.__class__(self._fp)

    def lastpart(self):
        self._fp.write('\n--' + self._boundary + '--\n')


if __name__ == '__main__':
    import test.test_MimeWriter
