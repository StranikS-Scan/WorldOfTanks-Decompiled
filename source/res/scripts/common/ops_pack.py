# Embedded file name: scripts/common/ops_pack.py
import struct
from external_strings_utils import truncate_utf8

def packPascalString(s):
    if isinstance(s, unicode):
        s = s.encode('utf8')
    s = truncate_utf8(s, 255)
    buffer = struct.pack('<B', len(s))
    buffer += s
    return buffer


def unpackPascalString(bufferString, offset = 0):
    lenString = struct.unpack_from('<B', bufferString, offset)[0]
    start = offset + 1
    fin = start + lenString
    retString = bufferString[start:fin]
    return (retString, lenString + 1)


def initOpsFormatDef(opsFormatDefs):
    for opCode in opsFormatDefs.keys():
        opDef = opsFormatDefs[opCode]
        unpackFormat, methodName = opDef[:2]
        specialFormat = opDef[2] if len(opDef) > 2 else ''
        additionals = opDef[3] if len(opDef) > 3 else []
        calcSize = 0
        packFormat = ''
        if unpackFormat or specialFormat:
            packFormat = '<B' + unpackFormat
            calcSize = struct.calcsize(packFormat)
            unpackFormat = '<' + unpackFormat
        if specialFormat:
            ofs = 0
            for formatSymbol in specialFormat:
                adds = additionals[ofs]
                if formatSymbol in ('T', 'L'):
                    lenFormat, elementFormat = adds
                    lenFormat = '<' + lenFormat
                    additionals[ofs] = (lenFormat,
                     elementFormat,
                     struct.calcsize(lenFormat),
                     struct.calcsize('<' + elementFormat))
                elif formatSymbol == 'N':
                    lenFormat, elementFormat = adds
                    lenFormat = '<' + lenFormat
                    elementFormat = '<' + elementFormat
                    additionals[ofs] = (lenFormat,
                     elementFormat,
                     struct.calcsize(lenFormat),
                     struct.calcsize(elementFormat))
                elif formatSymbol == 'D':
                    lenFormat, keyFormat, valFormat = adds
                    lenFormat = '<' + lenFormat
                    additionals[ofs] = (lenFormat,
                     keyFormat,
                     valFormat,
                     struct.calcsize(lenFormat),
                     struct.calcsize('<' + keyFormat),
                     struct.calcsize('<' + valFormat))
                elif formatSymbol in ('M',):
                    lenFormat, elementFormat, fieldNames = adds
                    lenFormat = '<' + lenFormat
                    elementFormat = '<' + elementFormat
                    additionals[ofs] = (lenFormat,
                     elementFormat,
                     fieldNames,
                     struct.calcsize(lenFormat),
                     struct.calcsize(elementFormat))
                ofs += 1

        opsFormatDefs[opCode] = (unpackFormat,
         methodName,
         specialFormat,
         additionals,
         calcSize,
         packFormat)

    return opsFormatDefs


class OpsPacker:

    def __init__(self):
        self._packedOps = ''

    def storeOp(self, op, *args):
        self._packedOps += self._getOpPack(op, *args)

    def _getOpPack(self, op, *args):
        unpackFormat, methodName, specialFormat, additionals, sz, packFormat = self._opsFormatDefs[op]
        specialCount = len(specialFormat)
        fixedArgs = args[:-specialCount] if specialCount else args
        pack = struct.pack(packFormat, op, *fixedArgs)
        if specialCount:
            specialArgs = args[-specialCount:]
            ofs = 0
            for formatSym in specialFormat:
                adds = additionals[ofs]
                arg = specialArgs[ofs]
                ofs += 1
                if formatSym == 'S':
                    pack += packPascalString(arg)
                elif formatSym in ('T', 'L'):
                    lenFormat, elemFormat = adds[:2]
                    lenElements = len(arg)
                    format = lenFormat + str(lenElements) + elemFormat
                    pack += struct.pack(format, lenElements, *arg)
                elif formatSym == 'N':
                    lenFormat, elemFormat = adds[:2]
                    lenElements = len(arg)
                    pack += struct.pack(lenFormat, lenElements)
                    for elements in arg:
                        pack += struct.pack(elemFormat, *elements)

                elif formatSym == 'D':
                    lenFormat, keyFormat, valFormat = adds[:3]
                    keys = arg.keys()
                    lenElements = len(keys)
                    format = lenFormat + str(lenElements) + keyFormat
                    pack += struct.pack(format, lenElements, *keys)
                    format = '<' + str(lenElements) + valFormat
                    pack += struct.pack(format, *arg.values())
                elif formatSym == 'M':
                    lenFormat, elemFormat, subkeyNames = adds[:3]
                    lenElements = len(arg)
                    pack += struct.pack(lenFormat, lenElements)
                    for key, subdict in arg.iteritems():
                        vals = []
                        for subkey in subkeyNames:
                            vals.append(subdict.get(subkey, 0))

                        pack += struct.pack(elemFormat, key, *vals)

                else:
                    raise 0 or AssertionError

        return pack

    def _appendOp(self, op, packedArgs):
        pack = struct.pack('<B', op)
        self._packedOps += pack + packedArgs

    def popPackedOps(self):
        res = self._packedOps
        self._packedOps = ''
        return res


class OpsUnpacker:

    def storeOp(self, op, *args):
        pass

    def _appendOp(self, op, packedArgs):
        pass

    def _onUnpackedOp(self, opCode):
        pass

    def unpackOps(self, packedOps = ''):
        invokedOps = set()
        while len(packedOps):
            opCode = struct.unpack_from('<B', packedOps)[0]
            try:
                unpackFormat, methodName, specialFormat, additionals, calcSize, packFormat = self._opsFormatDefs[opCode]
            except:
                raise Exception, '%s unpackOps: unknown opcode %s' % (self.__class__, opCode)

            method = getattr(self, methodName)
            if unpackFormat or specialFormat:
                if unpackFormat:
                    args = struct.unpack_from(unpackFormat, packedOps, 1)
                packOfs = calcSize
                if specialFormat:
                    args = list(args)
                    ofs = 0
                    for formatSymbol in specialFormat:
                        adds = additionals[ofs]
                        if formatSymbol == 'S':
                            arg, lenString = unpackPascalString(packedOps, packOfs)
                            packOfs += lenString
                        elif formatSymbol in ('T', 'L'):
                            headerFormat, elemFormat, headerSize, elemSize = adds
                            lenElements = struct.unpack_from(headerFormat, packedOps, packOfs)[0]
                            packOfs += headerSize
                            elementsFormat = '<%i' % lenElements + elemFormat
                            elements = struct.unpack_from(elementsFormat, packedOps, packOfs)
                            packOfs += lenElements * elemSize
                            if formatSymbol == 'T':
                                arg = set(elements)
                            elif formatSymbol == 'L':
                                arg = list(elements)
                        elif formatSymbol == 'N':
                            headerFormat, elemFormat, headerSize, elemSize = adds
                            lenElements = struct.unpack_from(headerFormat, packedOps, packOfs)[0]
                            packOfs += headerSize
                            arg = []
                            for i in xrange(lenElements):
                                elements = struct.unpack_from(elemFormat, packedOps, packOfs)
                                arg.append(elements)
                                packOfs += elemSize

                        elif formatSymbol == 'D':
                            lenFormat, keyFormat, valFormat, lenSize, keySize, valSize = adds
                            lenElements = struct.unpack_from(lenFormat, packedOps, packOfs)[0]
                            packOfs += lenSize
                            format = '<%i' % lenElements + keyFormat
                            keys = struct.unpack_from(format, packedOps, packOfs)
                            packOfs += lenElements * keySize
                            format = '<%i' % lenElements + valFormat
                            values = struct.unpack_from(format, packedOps, packOfs)
                            packOfs += lenElements * valSize
                            arg = dict(zip(keys, values))
                        elif formatSymbol == 'M':
                            lenFormat, elemFormat, subkeyNames, lenSize, elemSize = adds
                            lenElements = struct.unpack_from(lenFormat, packedOps, packOfs)[0]
                            packOfs += lenSize
                            arg = {}
                            for i in xrange(lenElements):
                                values = struct.unpack_from(elemFormat, packedOps, packOfs)
                                key = values[0]
                                subkeyOfs = 1
                                subdict = {}
                                for subkey in subkeyNames:
                                    subdict[subkey] = values[subkeyOfs]
                                    subkeyOfs += 1

                                packOfs += elemSize
                                arg[key] = subdict

                        args.append(arg)
                        ofs += 1

                packedOps = packedOps[packOfs:]
                method(*args)
            else:
                packedOps = method(packedOps[1:])
            invokedOps.add(opCode)

        return invokedOps
