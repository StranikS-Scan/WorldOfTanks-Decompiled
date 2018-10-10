# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/mimetypes.py
import os
import sys
import posixpath
import urllib
try:
    import _winreg
except ImportError:
    _winreg = None

__all__ = ['guess_type',
 'guess_extension',
 'guess_all_extensions',
 'add_type',
 'read_mime_types',
 'init']
knownfiles = ['/etc/mime.types',
 '/etc/httpd/mime.types',
 '/etc/httpd/conf/mime.types',
 '/etc/apache/mime.types',
 '/etc/apache2/mime.types',
 '/usr/local/etc/httpd/conf/mime.types',
 '/usr/local/lib/netscape/mime.types',
 '/usr/local/etc/httpd/conf/mime.types',
 '/usr/local/etc/mime.types']
inited = False
_db = None

class MimeTypes:

    def __init__(self, filenames=(), strict=True):
        global inited
        if not inited:
            init()
        self.encodings_map = encodings_map.copy()
        self.suffix_map = suffix_map.copy()
        self.types_map = ({}, {})
        self.types_map_inv = ({}, {})
        for ext, type in types_map.items():
            self.add_type(type, ext, True)

        for ext, type in common_types.items():
            self.add_type(type, ext, False)

        for name in filenames:
            self.read(name, strict)

    def add_type(self, type, ext, strict=True):
        self.types_map[strict][ext] = type
        exts = self.types_map_inv[strict].setdefault(type, [])
        if ext not in exts:
            exts.append(ext)

    def guess_type(self, url, strict=True):
        scheme, url = urllib.splittype(url)
        if scheme == 'data':
            comma = url.find(',')
            if comma < 0:
                return (None, None)
            semi = url.find(';', 0, comma)
            if semi >= 0:
                type = url[:semi]
            else:
                type = url[:comma]
            if '=' in type or '/' not in type:
                type = 'text/plain'
            return (type, None)
        else:
            base, ext = posixpath.splitext(url)
            while ext in self.suffix_map:
                base, ext = posixpath.splitext(base + self.suffix_map[ext])

            if ext in self.encodings_map:
                encoding = self.encodings_map[ext]
                base, ext = posixpath.splitext(base)
            else:
                encoding = None
            types_map = self.types_map[True]
            if ext in types_map:
                return (types_map[ext], encoding)
            if ext.lower() in types_map:
                return (types_map[ext.lower()], encoding)
            if strict:
                return (None, encoding)
            types_map = self.types_map[False]
            if ext in types_map:
                return (types_map[ext], encoding)
            if ext.lower() in types_map:
                return (types_map[ext.lower()], encoding)
            return (None, encoding)
            return

    def guess_all_extensions(self, type, strict=True):
        type = type.lower()
        extensions = self.types_map_inv[True].get(type, [])
        if not strict:
            for ext in self.types_map_inv[False].get(type, []):
                if ext not in extensions:
                    extensions.append(ext)

        return extensions

    def guess_extension(self, type, strict=True):
        extensions = self.guess_all_extensions(type, strict)
        return None if not extensions else extensions[0]

    def read(self, filename, strict=True):
        with open(filename) as fp:
            self.readfp(fp, strict)

    def readfp(self, fp, strict=True):
        while 1:
            line = fp.readline()
            if not line:
                break
            words = line.split()
            for i in range(len(words)):
                if words[i][0] == '#':
                    del words[i:]
                    break

            if not words:
                continue
            type, suffixes = words[0], words[1:]
            for suff in suffixes:
                self.add_type(type, '.' + suff, strict)

    def read_windows_registry(self, strict=True):
        if not _winreg:
            return

        def enum_types(mimedb):
            i = 0
            while True:
                try:
                    yield _winreg.EnumKey(mimedb, i)
                except EnvironmentError:
                    break

                i += 1

        with _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '') as hkcr:
            for subkeyname in enum_types(hkcr):
                if not subkeyname.startswith('.'):
                    continue
                with _winreg.OpenKey(hkcr, subkeyname) as subkey:
                    try:
                        mimetype, datatype = _winreg.QueryValueEx(subkey, 'Content Type')
                    except EnvironmentError:
                        continue

                    if datatype != _winreg.REG_SZ:
                        continue
                    self.add_type(mimetype, subkeyname, strict)


def guess_type(url, strict=True):
    global _db
    if _db is None:
        init()
    return _db.guess_type(url, strict)


def guess_all_extensions(type, strict=True):
    if _db is None:
        init()
    return _db.guess_all_extensions(type, strict)


def guess_extension(type, strict=True):
    if _db is None:
        init()
    return _db.guess_extension(type, strict)


def add_type(type, ext, strict=True):
    if _db is None:
        init()
    return _db.add_type(type, ext, strict)


def init(files=None):
    global types_map
    global inited
    global encodings_map
    global _db
    global common_types
    global suffix_map
    inited = True
    db = MimeTypes()
    if files is None:
        if _winreg:
            db.read_windows_registry()
        files = knownfiles
    for file in files:
        if os.path.isfile(file):
            db.read(file)

    encodings_map = db.encodings_map
    suffix_map = db.suffix_map
    types_map = db.types_map[True]
    common_types = db.types_map[False]
    _db = db
    return


def read_mime_types(file):
    try:
        f = open(file)
    except IOError:
        return

    with f:
        db = MimeTypes()
        db.readfp(f, True)
        return db.types_map[True]
    return


def _default_mime_types():
    global encodings_map
    global types_map
    global suffix_map
    global common_types
    suffix_map = {'.tgz': '.tar.gz',
     '.taz': '.tar.gz',
     '.tz': '.tar.gz',
     '.tbz2': '.tar.bz2',
     '.txz': '.tar.xz'}
    encodings_map = {'.gz': 'gzip',
     '.Z': 'compress',
     '.bz2': 'bzip2',
     '.xz': 'xz'}
    types_map = {'.a': 'application/octet-stream',
     '.ai': 'application/postscript',
     '.aif': 'audio/x-aiff',
     '.aifc': 'audio/x-aiff',
     '.aiff': 'audio/x-aiff',
     '.au': 'audio/basic',
     '.avi': 'video/x-msvideo',
     '.bat': 'text/plain',
     '.bcpio': 'application/x-bcpio',
     '.bin': 'application/octet-stream',
     '.bmp': 'image/x-ms-bmp',
     '.c': 'text/plain',
     '.cdf': 'application/x-cdf',
     '.cdf': 'application/x-netcdf',
     '.cpio': 'application/x-cpio',
     '.csh': 'application/x-csh',
     '.css': 'text/css',
     '.dll': 'application/octet-stream',
     '.doc': 'application/msword',
     '.dot': 'application/msword',
     '.dvi': 'application/x-dvi',
     '.eml': 'message/rfc822',
     '.eps': 'application/postscript',
     '.etx': 'text/x-setext',
     '.exe': 'application/octet-stream',
     '.gif': 'image/gif',
     '.gtar': 'application/x-gtar',
     '.h': 'text/plain',
     '.hdf': 'application/x-hdf',
     '.htm': 'text/html',
     '.html': 'text/html',
     '.ico': 'image/vnd.microsoft.icon',
     '.ief': 'image/ief',
     '.jpe': 'image/jpeg',
     '.jpeg': 'image/jpeg',
     '.jpg': 'image/jpeg',
     '.js': 'application/javascript',
     '.ksh': 'text/plain',
     '.latex': 'application/x-latex',
     '.m1v': 'video/mpeg',
     '.man': 'application/x-troff-man',
     '.me': 'application/x-troff-me',
     '.mht': 'message/rfc822',
     '.mhtml': 'message/rfc822',
     '.mif': 'application/x-mif',
     '.mov': 'video/quicktime',
     '.movie': 'video/x-sgi-movie',
     '.mp2': 'audio/mpeg',
     '.mp3': 'audio/mpeg',
     '.mp4': 'video/mp4',
     '.mpa': 'video/mpeg',
     '.mpe': 'video/mpeg',
     '.mpeg': 'video/mpeg',
     '.mpg': 'video/mpeg',
     '.ms': 'application/x-troff-ms',
     '.nc': 'application/x-netcdf',
     '.nws': 'message/rfc822',
     '.o': 'application/octet-stream',
     '.obj': 'application/octet-stream',
     '.oda': 'application/oda',
     '.p12': 'application/x-pkcs12',
     '.p7c': 'application/pkcs7-mime',
     '.pbm': 'image/x-portable-bitmap',
     '.pdf': 'application/pdf',
     '.pfx': 'application/x-pkcs12',
     '.pgm': 'image/x-portable-graymap',
     '.pl': 'text/plain',
     '.png': 'image/png',
     '.pnm': 'image/x-portable-anymap',
     '.pot': 'application/vnd.ms-powerpoint',
     '.ppa': 'application/vnd.ms-powerpoint',
     '.ppm': 'image/x-portable-pixmap',
     '.pps': 'application/vnd.ms-powerpoint',
     '.ppt': 'application/vnd.ms-powerpoint',
     '.ps': 'application/postscript',
     '.pwz': 'application/vnd.ms-powerpoint',
     '.py': 'text/x-python',
     '.pyc': 'application/x-python-code',
     '.pyo': 'application/x-python-code',
     '.qt': 'video/quicktime',
     '.ra': 'audio/x-pn-realaudio',
     '.ram': 'application/x-pn-realaudio',
     '.ras': 'image/x-cmu-raster',
     '.rdf': 'application/xml',
     '.rgb': 'image/x-rgb',
     '.roff': 'application/x-troff',
     '.rtx': 'text/richtext',
     '.sgm': 'text/x-sgml',
     '.sgml': 'text/x-sgml',
     '.sh': 'application/x-sh',
     '.shar': 'application/x-shar',
     '.snd': 'audio/basic',
     '.so': 'application/octet-stream',
     '.src': 'application/x-wais-source',
     '.sv4cpio': 'application/x-sv4cpio',
     '.sv4crc': 'application/x-sv4crc',
     '.swf': 'application/x-shockwave-flash',
     '.t': 'application/x-troff',
     '.tar': 'application/x-tar',
     '.tcl': 'application/x-tcl',
     '.tex': 'application/x-tex',
     '.texi': 'application/x-texinfo',
     '.texinfo': 'application/x-texinfo',
     '.tif': 'image/tiff',
     '.tiff': 'image/tiff',
     '.tr': 'application/x-troff',
     '.tsv': 'text/tab-separated-values',
     '.txt': 'text/plain',
     '.ustar': 'application/x-ustar',
     '.vcf': 'text/x-vcard',
     '.wav': 'audio/x-wav',
     '.wiz': 'application/msword',
     '.wsdl': 'application/xml',
     '.xbm': 'image/x-xbitmap',
     '.xlb': 'application/vnd.ms-excel',
     '.xls': 'application/excel',
     '.xls': 'application/vnd.ms-excel',
     '.xml': 'text/xml',
     '.xpdl': 'application/xml',
     '.xpm': 'image/x-xpixmap',
     '.xsl': 'application/xml',
     '.xwd': 'image/x-xwindowdump',
     '.zip': 'application/zip'}
    common_types = {'.jpg': 'image/jpg',
     '.mid': 'audio/midi',
     '.midi': 'audio/midi',
     '.pct': 'image/pict',
     '.pic': 'image/pict',
     '.pict': 'image/pict',
     '.rtf': 'application/rtf',
     '.xul': 'text/xul'}


_default_mime_types()
if __name__ == '__main__':
    import getopt
    USAGE = 'Usage: mimetypes.py [options] type\n\nOptions:\n    --help / -h       -- print this message and exit\n    --lenient / -l    -- additionally search of some common, but non-standard\n                         types.\n    --extension / -e  -- guess extension instead of type\n\nMore than one type argument may be given.\n'

    def usage(code, msg=''):
        print USAGE
        if msg:
            print msg
        sys.exit(code)


    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hle', ['help', 'lenient', 'extension'])
    except getopt.error as msg:
        usage(1, msg)

    strict = 1
    extension = 0
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        if opt in ('-l', '--lenient'):
            strict = 0
        if opt in ('-e', '--extension'):
            extension = 1

    for gtype in args:
        if extension:
            guess = guess_extension(gtype, strict)
            if not guess:
                print "I don't know anything about type", gtype
            else:
                print guess
        guess, encoding = guess_type(gtype, strict)
        if not guess:
            print "I don't know anything about type", gtype
        print 'type:', guess, 'encoding:', encoding
