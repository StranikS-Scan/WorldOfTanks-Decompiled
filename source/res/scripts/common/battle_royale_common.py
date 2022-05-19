# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_royale_common.py


class BattleRoyaleVehicleStats(object):
    __DAMAGE_DEALT = 0
    __XP = 1
    __SHOTS = 2
    __DIRECT_HITS = 3
    __DAMAGE_RECEIVED = 4
    __SURVIVED_BATTLES = 5
    __FRAGS = 6
    __MAX_XP = 7
    __MAX_DAMAGE_DEALT = 8
    __MAX_FRAGS = 9
    __END_INDEX = 10

    def __init__(self, rawData):
        self.__rawData = rawData
        self.__checkAndInitData()

    def addShots(self, value):
        self.__rawData['brstats'][self.__SHOTS] += value

    def addDirectHits(self, value):
        self.__rawData['brstats'][self.__DIRECT_HITS] += value

    def addDamageReceived(self, value):
        self.__rawData['brstats'][self.__DAMAGE_RECEIVED] += value

    def addSurvivedBattles(self, value):
        self.__rawData['brstats'][self.__SURVIVED_BATTLES] += value

    def addXP(self, value):
        self.__rawData['brstats'][self.__XP] += value
        if value > self.__rawData['brstats'][self.__MAX_XP]:
            self.__rawData['brstats'][self.__MAX_XP] = value

    def addDamageDealt(self, value):
        self.__rawData['brstats'][self.__DAMAGE_DEALT] += value
        if value > self.__rawData['brstats'][self.__MAX_DAMAGE_DEALT]:
            self.__rawData['brstats'][self.__MAX_DAMAGE_DEALT] = value

    def addFrags(self, value):
        self.__rawData['brstats'][self.__FRAGS] += value
        if value > self.__rawData['brstats'][self.__MAX_FRAGS]:
            self.__rawData['brstats'][self.__MAX_FRAGS] = value

    def getXP(self):
        return self.__rawData['brstats'][self.__XP]

    def getShotsCount(self):
        return self.__rawData['brstats'][self.__SHOTS]

    def getHitsCount(self):
        return self.__rawData['brstats'][self.__DIRECT_HITS]

    def getDamageReceived(self):
        return self.__rawData['brstats'][self.__DAMAGE_RECEIVED]

    def getDamageDealt(self):
        return self.__rawData['brstats'][self.__DAMAGE_DEALT]

    def getSurvivedBattlesCount(self):
        return self.__rawData['brstats'][self.__SURVIVED_BATTLES]

    def getFragsCount(self):
        return self.__rawData['brstats'][self.__FRAGS]

    def getMaxXp(self):
        return self.__rawData['brstats'][self.__MAX_XP]

    def getMaxFrags(self):
        return self.__rawData['brstats'][self.__MAX_FRAGS]

    def getMaxDamage(self):
        return self.__rawData['brstats'][self.__MAX_DAMAGE_DEALT]

    def _getAvgValue(self, allOccurs, effectiveOccurs):
        return float(effectiveOccurs) / allOccurs if allOccurs else 0.0

    def getAvgDamageReceived(self):
        return self._getAvgValue(self.getBattlesCount(), self.getDamageReceived())

    def getAvgFrags(self):
        return self._getAvgValue(self.getBattlesCount(), self.getFragsCount())

    def getHitsEfficiency(self):
        return self._getAvgValue(self.getShotsCount(), self.getHitsCount())

    def getFragsEfficiency(self):
        return self._getAvgValue(self.getDeathsCount(), self.getFragsCount())

    def getDamageEfficiency(self):
        return self._getAvgValue(self.getDamageReceived(), self.getDamageDealt())

    def getBattlesCount(self):
        return self.getWinsCount() + self.getLossesCount()

    def getDeathsCount(self):
        return self.getBattlesCount() - self.getSurvivedBattlesCount()

    def getWinsCount(self):
        return self.__rawData['brplaces'].get(1, 0)

    def getLossesCount(self):
        return sum([ count for place, count in self.__rawData['brplaces'].iteritems() if place != 1 ])

    def getAvgXP(self):
        return self._getAvgValue(self.getBattlesCount(), self.getXP())

    def getAvgDamage(self):
        return self._getAvgValue(self.getBattlesCount(), self.getDamageDealt())

    def getAveragePosition(self):
        return round(self._getAvgValue(self.getBattlesCount(), self.getPositionSum()), 1)

    def getAverageLevel(self):
        return round(self._getAvgValue(self.getBattlesCount(), self.getAchivedLevelSum()), 1)

    def getPositionSum(self):
        return sum([ k * v for k, v in self.__rawData['brplaces'].iteritems() ])

    def getAchivedLevelSum(self):
        return sum([ k * v for k, v in self.__rawData['brlevels'].iteritems() ])

    def incrementPlace(self, place):
        self.__rawData['brplaces'][place] = self.__rawData['brplaces'].get(place, 0) + 1

    def incrementLevel(self, level):
        self.__rawData['brlevels'][level] = self.__rawData['brlevels'].get(level, 0) + 1

    @property
    def places(self):
        return self.__rawData['brplaces']

    @property
    def levels(self):
        return self.__rawData['brlevels']

    @property
    def rawData(self):
        return self.__rawData

    def __checkAndInitData(self):
        if not self.__rawData:
            self.__rawData['brstats'] = []
            self.__rawData['brplaces'] = {}
            self.__rawData['brlevels'] = {}
        lengthStats = len(self.__rawData['brstats'])
        if lengthStats < self.__END_INDEX:
            self.__rawData['brstats'] += [0] * (self.__END_INDEX - lengthStats)
