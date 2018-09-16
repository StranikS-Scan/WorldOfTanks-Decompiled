# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/imghdr.py
__all__ = ['what']

def what(file, h=None):
    f = None
    try:
        if h is None:
            if isinstance(file, basestring):
                f = open(file, 'rb')
                h = f.read(32)
            else:
                location = file.tell()
                h = file.read(32)
                file.seek(location)
        for tf in tests:
            res = tf(h, f)
            if res:
                return res

    finally:
        if f:
            f.close()

    return


tests = []

def test_jpeg(h, f):
    return 'jpeg' if h[6:10] == 'JFIF' else None


tests.append(test_jpeg)

def test_exif(h, f):
    return 'jpeg' if h[6:10] == 'Exif' else None


tests.append(test_exif)

def test_png(h, f):
    return 'png' if h[:8] == '\x89PNG\r\n\x1a\n' else None


tests.append(test_png)

def test_gif(h, f):
    return 'gif' if h[:6] in ('GIF87a', 'GIF89a') else None


tests.append(test_gif)

def test_tiff(h, f):
    return 'tiff' if h[:2] in ('MM', 'II') else None


tests.append(test_tiff)

def test_rgb(h, f):
    return 'rgb' if h[:2] == '\x01\xda' else None


tests.append(test_rgb)

def test_pbm(h, f):
    return 'pbm' if len(h) >= 3 and h[0] == 'P' and h[1] in '14' and h[2] in ' \t\n\r' else None


tests.append(test_pbm)

def test_pgm(h, f):
    return 'pgm' if len(h) >= 3 and h[0] == 'P' and h[1] in '25' and h[2] in ' \t\n\r' else None


tests.append(test_pgm)

def test_ppm(h, f):
    return 'ppm' if len(h) >= 3 and h[0] == 'P' and h[1] in '36' and h[2] in ' \t\n\r' else None


tests.append(test_ppm)

def test_rast(h, f):
    return 'rast' if h[:4] == 'Y\xa6j\x95' else None


tests.append(test_rast)

def test_xbm(h, f):
    s = '#define '
    return 'xbm' if h[:len(s)] == s else None


tests.append(test_xbm)

def test_bmp(h, f):
    return 'bmp' if h[:2] == 'BM' else None


tests.append(test_bmp)

def test():
    import sys
    recursive = 0
    if sys.argv[1:] and sys.argv[1] == '-r':
        del sys.argv[1:2]
        recursive = 1
    try:
        if sys.argv[1:]:
            testall(sys.argv[1:], recursive, 1)
        else:
            testall(['.'], recursive, 1)
    except KeyboardInterrupt:
        sys.stderr.write('\n[Interrupted]\n')
        sys.exit(1)


def testall(list, recursive, toplevel):
    import sys
    import os
    for filename in list:
        if os.path.isdir(filename):
            print filename + '/:',
            if recursive or toplevel:
                print 'recursing down:'
                import glob
                names = glob.glob(os.path.join(filename, '*'))
                testall(names, recursive, 0)
            else:
                print '*** directory (use -r) ***'
        print filename + ':',
        sys.stdout.flush()
        try:
            print what(filename)
        except IOError:
            print '*** not found ***'
