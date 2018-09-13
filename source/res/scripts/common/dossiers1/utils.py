# Embedded file name: scripts/common/dossiers1/utils.py
from struct import unpack
from items import vehicles
from debug_utils import *
RECORD_DEFAULT_VALUES = {'vehTypeFrags': {},
 'a15x15Cut': {},
 'rareAchievements': list()}

def buildStaticRecordPositions(recordsLayout, recordPackings):
    positions = {}
    sum = 0
    for record in recordsLayout[0]:
        positions[record] = sum
        recordPacking = recordPackings[record]
        raise recordPacking[0] == 'p' or recordPacking[0] == 's' or recordPacking[0] == 'b' or AssertionError
        if recordPacking[0] == 'b':
            continue
        sum += recordPacking[2]

    positions['_staticRecordsSize'] = sum
    return positions


def buildStaticRecordsFmt(recordsLayout, recordPackings):
    fmt = '<'
    for record in recordsLayout[0]:
        packing = recordPackings[record]
        if packing[0] == 'b':
            continue
        fmt += packing[1]

    return fmt


def _getTupleValues(data):
    return data


def _getTupleData(values):
    return values


def getRareAchievementsFmtValues(achievements):
    count = len(achievements)
    fmt = 'H%dI' % (count,)
    values = [count]
    values += achievements
    return (fmt, values, 2 + 4 * count)


def unpackRareAchievements(compDescr, offset):
    count = unpack('<H', compDescr[offset:offset + 2])[0]
    next_offset = offset + 2 + 4 * count
    values = unpack('<%dI' % (count,), compDescr[offset + 2:next_offset])
    return (list(values), next_offset)


def getVehTypeFragsFmtValues(vehTypeFrags):
    count = len(vehTypeFrags)
    fmt = 'H%dI%dH' % (count, count)
    values = [count]
    values += vehTypeFrags.keys()
    values += vehTypeFrags.values()
    return (fmt, values, 2 + 6 * count)


def unpackVehTypeFrags(compDescr, offset):
    count = unpack('<H', compDescr[offset:offset + 2])[0]
    next_offset = offset + 2 + 6 * count
    values = unpack('<%dI%dH' % (count, count), compDescr[offset + 2:next_offset])
    data = {}
    for i in xrange(count):
        data[values[i]] = values[count + i]

    return (data, next_offset)


def getA15x15CutFmtValues(a15x15Cut):
    count = len(a15x15Cut)
    fmt = 'H%dI' % (5 * count,)
    values = [count]
    for vehTypeCompDescr, (battlesCount, wins, markOfMastery, avgXP) in a15x15Cut.iteritems():
        values += (vehTypeCompDescr,
         battlesCount,
         wins,
         markOfMastery,
         avgXP)

    return (fmt, values, 2 + 20 * count)


def unpackA15x15Cut(compDescr, offset):
    count = unpack('<H', compDescr[offset:offset + 2])[0]
    next_offset = offset + 2 + 20 * count
    values = unpack('<%dI' % (5 * count,), compDescr[offset + 2:next_offset])
    data = {}
    for i in xrange(count):
        idx = 5 * i
        data[values[idx]] = (values[idx + 1],
         values[idx + 2],
         values[idx + 3],
         values[idx + 4])

    return (data, next_offset)


def extendRecordPacking(recordsLayout, recordName, record_packing):
    dynRecordsCount = len(recordsLayout[1])
    record_packing[recordName] = ('s',
     '%dH' % dynRecordsCount,
     dynRecordsCount * 2,
     dynRecordsCount,
     _getTupleValues,
     _getTupleData)
    RECORD_DEFAULT_VALUES[recordName] = (0,) * dynRecordsCount


def unpackDossierCompDescr(recordsLayout, record_packing, compDescr, fmt = None, staticRecordPositions = None):
    data = {}
    if fmt is None:
        fmt = buildStaticRecordsFmt(recordsLayout, record_packing)
    if staticRecordPositions is None:
        staticRecordPositions = buildStaticRecordPositions(recordsLayout, record_packing)
    offset = staticRecordPositions['_staticRecordsSize']
    values = unpack(fmt, compDescr[:offset])
    index = 0
    for record in recordsLayout[0]:
        packing = record_packing[record]
        if packing[0] == 'p':
            data[record] = values[index]
            index += 1
        elif packing[0] == 'b':
            continue
        else:
            data[record] = packing[5](values[index:index + packing[3]])
            index += packing[3]

    for record in recordsLayout[1]:
        packing = record_packing[record]
        data[record], offset = packing[2](compDescr, offset)

    return data
