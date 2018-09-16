# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Protocol/Chaffing.py
__revision__ = '$Id$'
from Crypto.Util.number import bytes_to_long

class Chaff:

    def __init__(self, factor=1.0, blocksper=1):
        if not 0.0 <= factor <= 1.0:
            raise ValueError, "'factor' must be between 0.0 and 1.0"
        if blocksper < 0:
            raise ValueError, "'blocksper' must be zero or more"
        self.__factor = factor
        self.__blocksper = blocksper

    def chaff(self, blocks):
        chaffedblocks = []
        count = len(blocks) * self.__factor
        blocksper = range(self.__blocksper)
        for i, wheat in zip(range(len(blocks)), blocks):
            if i < count:
                serial, data, mac = wheat
                datasize = len(data)
                macsize = len(mac)
                addwheat = 1
                for j in blocksper:
                    import sys
                    chaffdata = self._randnum(datasize)
                    chaffmac = self._randnum(macsize)
                    chaff = (serial, chaffdata, chaffmac)
                    if addwheat and bytes_to_long(self._randnum(16)) & 64:
                        chaffedblocks.append(wheat)
                        addwheat = 0
                    chaffedblocks.append(chaff)

                if addwheat:
                    chaffedblocks.append(wheat)
            chaffedblocks.append(wheat)

        return chaffedblocks

    def _randnum(self, size):
        from Crypto import Random
        return Random.new().read(size)


if __name__ == '__main__':
    text = 'We hold these truths to be self-evident, that all men are created equal, that\nthey are endowed by their Creator with certain unalienable Rights, that among\nthese are Life, Liberty, and the pursuit of Happiness. That to secure these\nrights, Governments are instituted among Men, deriving their just powers from\nthe consent of the governed. That whenever any Form of Government becomes\ndestructive of these ends, it is the Right of the People to alter or to\nabolish it, and to institute new Government, laying its foundation on such\nprinciples and organizing its powers in such form, as to them shall seem most\nlikely to effect their Safety and Happiness.\n'
    print 'Original text:\n=========='
    print text
    print '=========='
    blocks = []
    size = 40
    for i in range(0, len(text), size):
        blocks.append(text[i:i + size])

    print 'Calculating MACs...'
    from Crypto.Hash import HMAC, SHA
    key = 'Jefferson'
    macs = [ HMAC.new(key, block, digestmod=SHA).digest() for block in blocks ]
    source = []
    m = zip(range(len(blocks)), blocks, macs)
    print m
    for i, data, mac in m:
        source.append((i, data, mac))

    print 'Adding chaff...'
    c = Chaff(factor=0.5, blocksper=2)
    chaffed = c.chaff(source)
    from base64 import encodestring
    wheat = []
    print 'chaffed message blocks:'
    for i, data, mac in chaffed:
        h = HMAC.new(key, data, digestmod=SHA)
        pmac = h.digest()
        if pmac == mac:
            tag = '-->'
            wheat.append(data)
        else:
            tag = '   '
        print tag, '%3d' % i,
        print repr(data), encodestring(mac)[:-1]

    print 'Undigesting wheat...'
    newtext = ''.join(wheat)
    if newtext == text:
        print 'They match!'
    else:
        print 'They differ!'
