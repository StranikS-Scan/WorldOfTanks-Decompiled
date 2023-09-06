# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/comp7_helpers.py
import collections
import operator
from dossiers2.common.updater_utils import getStaticSizeBlockRecordValues, getDictBlockRecordValues, updateDictRecords, addRecords, removeRecords, updateStaticSizeBlockRecords
SEASON_KEY = 'comp7Season'
MAX_SEASON_KEY = 'maxComp7Season'
CUT_SEASON_KEY = 'comp7CutSeason'

def getSeasonsRecords(seasonKey, seasonsNumber, ctx, packing):
    seasonsRecords = []
    for seasonNumber in range(seasonsNumber):
        key = '{}{}'.format(seasonKey, seasonNumber + 1)
        seasonsRecords.append(getStaticSizeBlockRecordValues(ctx, key, packing))

    return seasonsRecords


def getCutSeasonsRecords(seasonKey, seasonsNumber, ctx):
    cutRecords = []
    for seasonNumber in range(seasonsNumber):
        key = '{}{}'.format(seasonKey, seasonNumber + 1)
        cutRecords.append(getDictBlockRecordValues(ctx, key, 'I', 'IIII'))

    return cutRecords


def getSumSeasonsValues(seasonsValues):
    return dict(reduce(operator.add, map(collections.Counter, seasonsValues)))


def getMaxSeasonsValues(seasonsValues):
    maxValues = seasonsValues[0]
    for seasonValues in seasonsValues[1:]:
        for key, value in seasonValues.iteritems():
            if key.endswith('Vehicle'):
                continue
            if value >= maxValues.get(key):
                maxValues[key] = value
                vehicleKey = '{}Vehicle'.format(key)
                if vehicleKey in seasonValues:
                    maxValues[vehicleKey] = seasonValues[vehicleKey]

    return maxValues


def prepareArchiveSeasonsRecords(values, packing):
    archiveRecords = []
    for key, packingFormat in packing.iteritems():
        archiveRecords.append((packingFormat[0], packingFormat[1], values.get(key, 0)))

    return archiveRecords


def prepareArchiveCutSeasonsRecords(cutSeasonsValues):
    cutArchiveRecords = cutSeasonsValues[0]
    for seasonValue in cutSeasonsValues[1:]:
        for key, value in seasonValue.iteritems():
            archiveValue = cutArchiveRecords.setdefault(key, (0, 0, 0, 0))
            cutArchiveRecords[key] = tuple(map(sum, tuple(zip(archiveValue, value))))

    return cutArchiveRecords


def clearSeasonsRecords(seasonsNumber, seasonsKey, ctx, packing):
    for seasonNumber in range(seasonsNumber):
        removeRecords(ctx, '{}{}'.format(seasonsKey, seasonNumber + 1), packing)


def clearCutSeasonsRecords(seasonsNumber, ctx):
    for seasonNumber in range(seasonsNumber):
        updateDictRecords(ctx, '{}{}'.format(CUT_SEASON_KEY, seasonNumber + 1), 'I', 'IIII', {})


def addSeasonRecord(updateCtx, seasonKey, fields, values):
    addRecords(updateCtx, seasonKey, fields, values)


def archiveSeasonsGriffin(seasonsNumber, ctx, seasonsPacking, seasonsNewPacking):
    archiveName = 'comp7ArchiveGriffin'
    seasonsValues = getSeasonsRecords(SEASON_KEY, seasonsNumber, ctx, seasonsPacking)
    sumSeasonsValues = getSumSeasonsValues(seasonsValues)
    valuesToArchive = prepareArchiveSeasonsRecords(sumSeasonsValues, seasonsNewPacking)
    updateStaticSizeBlockRecords(ctx, archiveName, valuesToArchive)
    clearSeasonsRecords(seasonsNumber, SEASON_KEY, ctx, seasonsPacking)


def archiveMaxSeasonsGriffin(seasonsNumber, ctx, maxSeasonsPacking):
    archiveName = 'maxComp7ArchiveGriffin'
    maxSeasonsValues = getSeasonsRecords(MAX_SEASON_KEY, seasonsNumber, ctx, maxSeasonsPacking)
    maxValues = getMaxSeasonsValues(maxSeasonsValues)
    valuesToArchive = prepareArchiveSeasonsRecords(maxValues, maxSeasonsPacking)
    updateStaticSizeBlockRecords(ctx, archiveName, valuesToArchive)
    clearSeasonsRecords(seasonsNumber, MAX_SEASON_KEY, ctx, maxSeasonsPacking)


def archiveCutSeasonsGriffin(seasonsNumber, ctx):
    archiveName = 'comp7CutArchiveGriffin'
    cutSeasonsValues = getCutSeasonsRecords(CUT_SEASON_KEY, seasonsNumber, ctx)
    valuesToArchive = prepareArchiveCutSeasonsRecords(cutSeasonsValues)
    updateDictRecords(ctx, archiveName, 'I', 'IIII', valuesToArchive)
    clearCutSeasonsRecords(seasonsNumber, ctx)
