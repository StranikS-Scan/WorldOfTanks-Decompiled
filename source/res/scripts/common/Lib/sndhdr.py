# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sndhdr.py
__all__ = ['what', 'whathdr']

def what(filename):
    res = whathdr(filename)
    return res


def whathdr(filename):
    f = open(filename, 'rb')
    h = f.read(512)
    for tf in tests:
        res = tf(h, f)
        if res:
            return res

    return None


tests = []

def test_aifc(h, f):
    import aifc
    if h[:4] != 'FORM':
        return
    else:
        if h[8:12] == 'AIFC':
            fmt = 'aifc'
        elif h[8:12] == 'AIFF':
            fmt = 'aiff'
        else:
            return
        f.seek(0)
        try:
            a = aifc.openfp(f, 'r')
        except (EOFError, aifc.Error):
            return

        return (fmt,
         a.getframerate(),
         a.getnchannels(),
         a.getnframes(),
         8 * a.getsampwidth())


tests.append(test_aifc)

def test_au(h, f):
    if h[:4] == '.snd':
        f = get_long_be
    elif h[:4] in ('\x00ds.', 'dns.'):
        f = get_long_le
    else:
        return None
    type = 'au'
    hdr_size = f(h[4:8])
    data_size = f(h[8:12])
    encoding = f(h[12:16])
    rate = f(h[16:20])
    nchannels = f(h[20:24])
    sample_size = 1
    if encoding == 1:
        sample_bits = 'U'
    elif encoding == 2:
        sample_bits = 8
    elif encoding == 3:
        sample_bits = 16
        sample_size = 2
    else:
        sample_bits = '?'
    frame_size = sample_size * nchannels
    return (type,
     rate,
     nchannels,
     data_size // frame_size,
     sample_bits)


tests.append(test_au)

def test_hcom(h, f):
    if h[65:69] != 'FSSD' or h[128:132] != 'HCOM':
        return None
    else:
        divisor = get_long_be(h[144:148])
        return ('hcom',
         22050 // divisor,
         1,
         -1,
         8)


tests.append(test_hcom)

def test_voc(h, f):
    if h[:20] != 'Creative Voice File\x1a':
        return None
    else:
        sbseek = get_short_le(h[20:22])
        rate = 0
        if 0 <= sbseek < 500 and h[sbseek] == '\x01':
            ratecode = ord(h[sbseek + 4])
            rate = int(1000000.0 / (256 - ratecode))
        return ('voc',
         rate,
         1,
         -1,
         8)


tests.append(test_voc)

def test_wav(h, f):
    if h[:4] != 'RIFF' or h[8:12] != 'WAVE' or h[12:16] != 'fmt ':
        return None
    else:
        style = get_short_le(h[20:22])
        nchannels = get_short_le(h[22:24])
        rate = get_long_le(h[24:28])
        sample_bits = get_short_le(h[34:36])
        return ('wav',
         rate,
         nchannels,
         -1,
         sample_bits)


tests.append(test_wav)

def test_8svx(h, f):
    return None if h[:4] != 'FORM' or h[8:12] != '8SVX' else ('8svx', 0, 1, 0, 8)


tests.append(test_8svx)

def test_sndt(h, f):
    if h[:5] == 'SOUND':
        nsamples = get_long_le(h[8:12])
        rate = get_short_le(h[20:22])
        return ('sndt',
         rate,
         1,
         nsamples,
         8)


tests.append(test_sndt)

def test_sndr(h, f):
    if h[:2] == '\x00\x00':
        rate = get_short_le(h[2:4])
        if 4000 <= rate <= 25000:
            return ('sndr',
             rate,
             1,
             -1,
             8)


tests.append(test_sndr)

def get_long_be(s):
    return ord(s[0]) << 24 | ord(s[1]) << 16 | ord(s[2]) << 8 | ord(s[3])


def get_long_le(s):
    return ord(s[3]) << 24 | ord(s[2]) << 16 | ord(s[1]) << 8 | ord(s[0])


def get_short_be(s):
    return ord(s[0]) << 8 | ord(s[1])


def get_short_le(s):
    return ord(s[1]) << 8 | ord(s[0])


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


if __name__ == '__main__':
    test()
