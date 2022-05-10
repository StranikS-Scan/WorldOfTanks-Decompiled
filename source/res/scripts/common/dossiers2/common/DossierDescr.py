# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/common/DossierDescr.py
import struct
from array import array
from dossiers2.custom.records import PLATFORM_ACHIEVEMENTS

class DossierDescr(object):

    def __init__(self, compDescr, blockBuilders, headerFormat):
        self.__compDescr = compDescr
        self.__headerFormat = headerFormat
        self.__blocksOffset = struct.calcsize(headerFormat)
        self.__blocksLayout = [ builder.name for builder in blockBuilders ]
        self.__blocksIndexes = dict([ (name, idx) for idx, name in enumerate(self.__blocksLayout) ])
        self.__blocksBuilders = dict([ (builder.name, builder) for builder in blockBuilders ])
        self.__blocks = {}
        self._dependentUpdates = 0
        self.__popUps = {}
        self.__logRecords = {}
        self.__blockRemoved = False
        values = struct.unpack_from(headerFormat, compDescr)
        self.__version = values[0]
        self.__sizes = list(values[1:])

    def __getitem__(self, name):
        block = self.__blocks.get(name, None)
        if block is not None:
            return block
        else:
            blockIdx = self.__blocksIndexes[name]
            size = self.__sizes[blockIdx]
            if size == 0:
                block = self.__blocksBuilders[name].build(self)
            else:
                offset = sum(self.__sizes[:blockIdx], self.__blocksOffset)
                block = self.__blocksBuilders[name].build(self, self.__compDescr[offset:offset + size])
            self.__blocks[name] = block
            return block

    def __contains__(self, block):
        return block in self.__blocks or self.__blocksIndexes.get(block, None) is not None and bool(self.__sizes[self.__blocksIndexes[block]])

    def removeBlock(self, name):
        self.__blocks.pop(name, None)
        blockIdx = self.__blocksIndexes[name]
        size = self.__sizes[blockIdx]
        if size != 0:
            self.__blockRemoved = True
            offset = sum(self.__sizes[:blockIdx], self.__blocksOffset)
            compDescr = self.__compDescr
            self.__compDescr = compDescr[:offset] + compDescr[offset + size:]
            self.__sizes[blockIdx] = 0
        return

    def isBlockInLayout(self, block):
        return block in self.__blocksBuilders

    def expand(self, name):
        return self[name].expand()

    def addPopUp(self, block, record, value, addLogRecord=True):
        self.__popUps[block, record] = value
        if addLogRecord:
            self.addLogRecord(block, record, value)

    def addLogRecord(self, block, record, value):
        self.__logRecords[block, record] = value

    def popPopUps(self):
        popUps = self.__popUps
        self.__popUps = {}
        return popUps

    def popLogRecords(self):
        logRecords = self.__logRecords
        self.__logRecords = {}
        return logRecords

    def getChanges(self):
        changes = dict()
        for key, block in self.__blocks.iteritems():
            blockChanges = block.getChanges()
            if blockChanges:
                changes[key] = blockChanges

        return changes

    def checkPlatformAchievements(self, disabledAchievements, oldDossierDescr, revertAchievements):
        platformAchievements = []
        changes = self.getChanges()
        for name, (medal, stat) in PLATFORM_ACHIEVEMENTS.iteritems():
            medalBlock, medalName = medal
            isMedalAchived = medalBlock in changes and medalName in changes[medalBlock]
            isStatsChanges = stat and stat[0] in changes and stat[1] in changes[stat[0]]
            if isMedalAchived or isStatsChanges:
                if name in disabledAchievements or revertAchievements:
                    self[medalBlock][medalName] = oldDossierDescr[medalBlock][medalName]
                    if stat:
                        self[stat[0]][stat[1]] = oldDossierDescr[stat[0]][stat[1]]
                else:
                    operation = {'code': name}
                    if isMedalAchived:
                        operation['unlocked'] = True
                    if stat and (isMedalAchived or not self[medalBlock][medalName]):
                        statValue = int(self[stat[0]].get(stat[1], 0))
                        if statValue:
                            operation['progress_amount'] = statValue
                    if len(operation) > 1:
                        platformAchievements.append(operation)

        return platformAchievements

    def makeCompDescr(self):
        if self.__blocks or self.__blockRemoved:
            compDescrArray = array('c', self.__compDescr)
            sizes = self.__sizes[:]
            offset = self.__blocksOffset
            for i, name in enumerate(self.__blocksLayout):
                block = self.__blocks.get(name, None)
                if block is not None:
                    compDescrArray, sizes[i] = block.updateDossierCompDescr(compDescrArray, offset, sizes[i])
                offset += sizes[i]

            if sizes != self.__sizes or self.__blockRemoved:
                self.__sizes = sizes
                struct.pack_into(self.__headerFormat, compDescrArray, 0, self.__version, *sizes)
            self.__compDescr = compDescrArray.tostring()
            self.__blockRemoved = False
        return self.__compDescr

    def isEmpty(self):
        hasSmth = any(self.__sizes)
        return not hasSmth
