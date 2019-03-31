# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers/utils.py
# Compiled at: 2011-08-23 16:44:54
from struct import unpack
from debug_utils import *
from itertools import chain
RECORD_DEFAULT_VALUES = {'vehTypeFrags': {},
 'vehDossiersCut': {}}

def buildStaticRecordPositions(recordsLayout, recordPackings):
    positions = {}
    sum = 0
    for record in recordsLayout[0]:
        positions[record] = sum
        recordPacking = recordPackings[record]
        assert recordPacking[0] == 'p' or recordPacking[0] == 's'
        sum += recordPacking[2]

    positions['_staticRecordsSize'] = sum
    return positions


def buildStaticRecordsFmt(recordsLayout, recordPackings):
    fmt = '<'
    for record in recordsLayout[0]:
        fmt += recordPackings[record][1]

    return fmt


def _getTupleValues(data):
    return data


def _getTupleData(values):
    return values


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


def getVehDossiersCutFmtValues(vehDossiersCut):
    count = len(vehDossiersCut)
    fmt = 'H%dI' % (3 * count,)
    values = [count]
    for vehTypeCompDescr, (battlesCount, wins) in vehDossiersCut.iteritems():
        values += (vehTypeCompDescr, battlesCount, wins)

    return (fmt, values, 2 + 12 * count)


def unpackVehDossiersCut(compDescr, offset):
    count = unpack('<H', compDescr[offset:offset + 2])[0]
    next_offset = offset + 2 + 12 * count
    values = unpack('<%dI' % (3 * count,), compDescr[offset + 2:next_offset])
    data = {}
    for i in xrange(count):
        data[values[3 * i]] = (values[3 * i + 1], values[3 * i + 2])

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


def checkIntegrity():
    for record in RECORD_NAMES[1:]:
        if record not in _RECORD_PACKING:
            LOG_WARNING('Packing for the record is not specified', record)

    for record in chain(*_ACCOUNT_RECORDS_LAYOUT):
        if record not in RECORD_NAMES and record[0] != '_':
            LOG_WARNING('Layout containg record that is not in the list', record)

    for record in chain(*_VEHICLE_RECORDS_LAYOUT):
        if record not in RECORD_NAMES and record[0] != '_':
            LOG_WARNING('Layout containg record that is not in the list', record)

    for record in chain(*_TANKMAN_RECORDS_LAYOUT):
        if record not in RECORD_NAMES and record[0] != '_':
            LOG_WARNING('Layout containg record that is not in the list', record)

    for record, packing in _RECORD_PACKING.iteritems():
        if packing[0] != 'p' and record not in RECORD_DEFAULT_VALUES:
            LOG_WARNING('Default value is not specified for the record', record)


def unpackDossierCompDescr(version, recordsLayout, record_packing, compDescr):
    data = {}
    fmt = buildStaticRecordsFmt(recordsLayout, record_packing)
    staticRecordPositions = buildStaticRecordPositions(recordsLayout, record_packing)
    offset = staticRecordPositions['_staticRecordsSize']
    values = unpack(fmt, compDescr[:offset])
    index = 0
    for record in recordsLayout[0]:
        packing = record_packing[record]
        if packing[0] == 'p':
            data[record] = values[index]
            index += 1
        else:
            data[record] = packing[5](values[index:index + packing[3]])
            index += packing[3]

    for record in recordsLayout[1]:
        packing = record_packing[record]
        data[record], offset = packing[2](compDescr, offset)

    return data
