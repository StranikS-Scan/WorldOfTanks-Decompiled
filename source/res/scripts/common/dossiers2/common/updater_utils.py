# Embedded file name: scripts/common/dossiers2/common/updater_utils.py
import struct

def buildBlocksLayout(buildersLayout):
    return [ builder.name for builder in buildersLayout ]


def buildAllRecordsFormat(block, recordsInfo):
    return dict([ (recordInfo[1], recordInfo[3]) for recordInfo in recordsInfo if recordInfo[0] == block and recordInfo[2] == 'p' ])


def buildRecordsPacking(records, layout, formats):
    offset = 0
    packing = {}
    for record in layout:
        format = formats[record]
        if record in records:
            packing[record] = (offset, format)
        offset += struct.calcsize('<' + format)

    return packing


def buildLayoutWithFormat(block, layout, recordsInfo):
    indices = dict(((rec[:2], idx) for idx, rec in enumerate(recordsInfo)))
    return [ (record, recordsInfo[indices[block, record]][3]) for record in layout ]


def getHeader(updateCtx):
    updateCtx['headerFormat'] = headerFormat = '<%s%d%s' % (updateCtx['versionFormat'], len(updateCtx['blocksLayout']), updateCtx['blockSizeFormat'])
    updateCtx['headerLength'] = struct.calcsize(headerFormat)
    updateCtx['header'] = list(struct.unpack_from(headerFormat, updateCtx['dossierCompDescr']))


def getStaticSizeBlockRecordValues(updateCtx, block, recordsPacking):
    blockIndex = updateCtx['blocksLayout'].index(block)
    if updateCtx['header'][blockIndex + 1] == 0:
        return {}
    blockOffset = updateCtx['headerLength'] + sum(updateCtx['header'][1:blockIndex + 1])
    res = {}
    for record, (offset, format) in recordsPacking.iteritems():
        res[record] = struct.unpack_from('<' + format, updateCtx['dossierCompDescr'], blockOffset + offset)[0]

    return res


def setStaticSizeBlockRecordValues(updateCtx, block, recordsPacking, recordsValues):
    blockIndex = updateCtx['blocksLayout'].index(block)
    if updateCtx['header'][blockIndex + 1] == 0:
        return {}
    blockOffset = updateCtx['headerLength'] + sum(updateCtx['header'][1:blockIndex + 1])
    for key, value in recordsValues.iteritems():
        offset, format = recordsPacking[key]
        data = struct.pack('<' + format, value)
        updateCtx['dossierCompDescr'] = updateCtx['dossierCompDescr'][:blockOffset + offset] + data + updateCtx['dossierCompDescr'][blockOffset + offset + len(data):]


def getNewStaticSizeBlockValues(layoutWithFormat, defaults):
    blockFormat = '<' + ''.join([ format for record, format in layoutWithFormat ])
    blockValues = [ defaults.get(record, 0) for record, format in layoutWithFormat ]
    return (blockFormat, blockValues)


def getNewBinarySetBlockValues(layout, values):
    blockValues = []
    bit = 0
    byte = 0
    for name in layout:
        bit += 1
        byte >>= 1
        byte |= 128 if bool(values.get(name, 0)) else 0
        if bit == 8:
            blockValues.append(byte)
            bit = 0
            byte = 0

    if bit > 0:
        byte >>= 8 - bit
        blockValues.append(byte)
    while len(blockValues) > 0 and blockValues[-1] == 0:
        blockValues.pop()

    blockFormat = '<%dB' % len(blockValues)
    return (blockFormat, blockValues)


def setVersion(updateCtx, version):
    versionFormat = '<' + updateCtx['versionFormat']
    versionLength = struct.calcsize(versionFormat)
    updateCtx['dossierCompDescr'] = struct.pack(versionFormat, version) + updateCtx['dossierCompDescr'][versionLength:]


def addBlock(updateCtx, block, blockFormat = '', blockValues = None):
    blockSize = struct.calcsize(blockFormat) if bool(blockFormat) else 0
    header = updateCtx['header']
    header.append(blockSize)
    updateCtx['headerFormat'] += updateCtx['blockSizeFormat']
    updateCtx['dossierCompDescr'] = struct.pack(updateCtx['headerFormat'], *header) + updateCtx['dossierCompDescr'][updateCtx['headerLength']:]
    updateCtx['blocksLayout'].append(block)
    updateCtx['headerLength'] += struct.calcsize('<' + updateCtx['blockSizeFormat'])
    if blockSize != 0:
        updateCtx['dossierCompDescr'] += struct.pack(blockFormat, *blockValues)


def addRecords(updateCtx, block, recordFormats, defaults):
    header = updateCtx['header']
    blockIndex = updateCtx['blocksLayout'].index(block)
    blockSize = header[blockIndex + 1]
    if blockSize == 0:
        return
    blockOffset = updateCtx['headerLength'] + sum(header[1:blockIndex + 1])
    subBlockFormat = '<' + ''.join([ format for record, format in recordFormats ])
    subBlockValues = [ defaults.get(record, 0) for record, format in recordFormats ]
    dossierCompDescr = updateCtx['dossierCompDescr']
    dossierCompDescr = dossierCompDescr[:blockOffset + blockSize] + struct.pack(subBlockFormat, *subBlockValues) + dossierCompDescr[blockOffset + blockSize:]
    header[blockIndex + 1] += struct.calcsize(subBlockFormat)
    updateCtx['dossierCompDescr'] = struct.pack(updateCtx['headerFormat'], *header) + dossierCompDescr[updateCtx['headerLength']:]


def removeRecords(updateCtx, block, recordsPacking):
    header = updateCtx['header']
    blockIndex = updateCtx['blocksLayout'].index(block)
    if header[blockIndex + 1] == 0:
        return
    blockOffset = updateCtx['headerLength'] + sum(header[1:blockIndex + 1])
    l = [ (offset, struct.calcsize('<' + format)) for record, (offset, format) in recordsPacking.iteritems() ]
    l.sort()
    totalSizeDec = 0
    dossierCompDescr = updateCtx['dossierCompDescr']
    for offset, size in l:
        dossierCompDescr = dossierCompDescr[:blockOffset + offset - totalSizeDec] + dossierCompDescr[blockOffset + offset - totalSizeDec + size:]
        totalSizeDec += size

    header[blockIndex + 1] -= totalSizeDec
    updateCtx['dossierCompDescr'] = struct.pack(updateCtx['headerFormat'], *header) + dossierCompDescr[updateCtx['headerLength']:]
