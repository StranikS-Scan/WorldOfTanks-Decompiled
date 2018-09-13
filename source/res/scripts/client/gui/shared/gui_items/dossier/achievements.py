# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements.py
import uuid
import imghdr
from collections import namedtuple
import BigWorld
from helpers import i18n
from items import vehicles
from nations import NAMES as NATION_NAMES
from debug_utils import LOG_DEBUG
from gui import nationCompareByIndex, makeHtmlString
from gui.shared.gui_items import GUIItem
from gui.shared.utils import CONST_CONTAINER
from gui.shared.utils.RareAchievementsCache import g_rareAchievesCache, IMAGE_TYPE
from gui.shared.fortifications import isFortificationEnabled
from dossiers2.ui import achievements
from dossiers2.custom.records import RECORD_MAX_VALUES
from dossiers2.custom.config import RECORD_CONFIGS
from dossiers2.custom.cache import getCache as getDossiersCache
from dossiers2.custom.helpers import getTankExpertRequirements, getMechanicEngineerRequirements
_AB = achievements.ACHIEVEMENT_BLOCK

class MARK_OF_MASTERY(CONST_CONTAINER):
    MASTER = 4
    STEP_1 = 3
    STEP_2 = 2
    STEP_3 = 1


class _HasVehiclesList(object):
    VehicleData = namedtuple('VehicleData', 'name nation level type icon')

    def getVehiclesData(self):
        result = []
        for vCD in self._getVehiclesDescrsList():
            from gui.shared import g_itemsCache
            vehicle = g_itemsCache.items.getItemByCD(vCD)
            result.append(self.VehicleData(vehicle.userName, vehicle.nationID, vehicle.level, vehicle.type, vehicle.iconSmall))

        return map(lambda i: i._asdict(), sorted(result, self.__sortFunc))

    def getVehiclesListTitle(self):
        return 'vehicles'

    def _getVehiclesDescrsList(self):
        raise NotImplemented

    @classmethod
    def __sortFunc(cls, i1, i2):
        res = i1.level - i2.level
        if res:
            return res
        return nationCompareByIndex(i1.nation, i2.nation)


class RegularAchievement(GUIItem):

    class ICON_TYPE:
        IT_180X180 = '180x180'
        IT_67X71 = '67x71'
        IT_32X32 = '32x32'

    ICON_PATH_180X180 = '../maps/icons/achievement/big'
    ICON_PATH_67X71 = '../maps/icons/achievement'
    ICON_PATH_32X32 = '../maps/icons/achievement/32x32'
    ICON_PATH_95X85 = '../maps/icons/achievement/95x85'
    ICON_DEFAULT = '../maps/icons/achievement/noImage.png'

    def __init__(self, name, block, dossier, value = None):
        super(RegularAchievement, self).__init__()
        self._name = str(name)
        self._block = str(block)
        self._value = value or 0
        self._lvlUpValue = 0
        self._lvlUpTotalValue = 0
        self._isDone = False
        self._isInDossier = self.checkIsInDossier(block, name, dossier)
        self._isValid = self.checkIsValid(block, name, dossier)
        if dossier is not None:
            if value is None:
                self._value = int(self._readValue(dossier))
            self._lvlUpTotalValue = self._readLevelUpTotalValue(dossier)
            self._lvlUpValue = self._readLevelUpValue(dossier)
            self._isDone = self._getDoneStatus(dossier)
        return

    def getName(self):
        return self._name

    def getBlock(self):
        return self._block

    def getValue(self):
        return self._value

    def getI18nValue(self):
        maxValue = RECORD_MAX_VALUES.get(self.getRecordName())
        if maxValue is not None and self._value >= maxValue:
            return i18n.makeString('#achievements:achievement/maxMedalValue') % BigWorld.wg_getIntegralFormat(maxValue - 1)
        else:
            return BigWorld.wg_getIntegralFormat(self._value)

    def getLevelUpValue(self):
        return self._lvlUpValue

    def getLevelUpTotalValue(self):
        return self._lvlUpTotalValue

    def getRecordName(self):
        return (self._block, self._name)

    def isInDossier(self):
        return self._isInDossier

    def isValid(self):
        return self._isValid

    def getNextLevelInfo(self):
        return ('', self._lvlUpValue)

    def getType(self):
        return self.__getPredefinedValue(achievements.getType)

    def getSection(self):
        return self.__getPredefinedValue(achievements.getSection)

    def getWeight(self):
        return self.__getPredefinedValue(achievements.getWeight)

    def isActive(self):
        return True

    def isDone(self):
        return self._isDone

    def getProgressValue(self):
        return 0.0

    def hasProgress(self):
        return False

    def hasCounter(self):
        return bool(self._value)

    def getIcons(self):
        iconName = self._getIconName()
        return {self.ICON_TYPE.IT_180X180: '%s/%s.png' % (self.ICON_PATH_180X180, iconName),
         self.ICON_TYPE.IT_67X71: '%s/%s.png' % (self.ICON_PATH_67X71, iconName),
         self.ICON_TYPE.IT_32X32: '%s/%s.png' % (self.ICON_PATH_32X32, iconName)}

    def getBigIcon(self):
        return self.getIcons()[self.ICON_TYPE.IT_180X180]

    def getSmallIcon(self):
        return self.getIcons()[self.ICON_TYPE.IT_67X71]

    def getUserName(self):
        return i18n.makeString('#achievements:%s' % self._getActualName())

    def getUserDescription(self):
        return i18n.makeString('#achievements:%s_descr' % self._getActualName())

    def getUserHeroInfo(self):
        heroInfoKey = '#achievements:%s_heroInfo' % self._getActualName()
        if i18n.doesTextExist(heroInfoKey):
            return i18n.makeString(heroInfoKey)
        return ''

    def getUserCondition(self):
        condKey = '#achievements:%s_condition' % self._getActualName()
        if i18n.doesTextExist(condKey):
            return i18n.makeString(condKey)
        return ''

    @classmethod
    def checkIsInDossier(cls, block, name, dossier):
        if dossier is not None:
            return bool(dossier.getRecordValue(block, name))
        else:
            return False

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return True

    def _readValue(self, dossier):
        return dossier.getRecordValue(*self.getRecordName())

    def _readLevelUpValue(self, dossier):
        return None

    def _readLevelUpTotalValue(self, dossier):
        return None

    def _getIconName(self):
        return self._getActualName()

    def _getActualName(self):
        return self._name

    def _getDoneStatus(self, dossier):
        return self.getProgressValue() == 1.0

    def __getPredefinedValue(self, getter):
        value = getter(self.getRecordName())
        if value is None:
            value = getter(achievements.makeAchievesStorageName(self._block))
        return value

    def __repr__(self):
        return '%s<name=%s; value=%s; levelUpValue=%s levelUpTotalValue=%s isDone=%s>' % (self.__class__.__name__,
         self._name,
         str(self._value),
         str(self._lvlUpValue),
         str(self._lvlUpTotalValue),
         str(self._isDone))

    def __cmp__(self, other):
        if isinstance(other, RegularAchievement):
            aSection, bSection = self.getSection(), other.getSection()
            if aSection is not None and bSection is not None:
                res = achievements.ACHIEVEMENT_SECTIONS_INDICES[aSection] - achievements.ACHIEVEMENT_SECTIONS_INDICES[bSection]
                if res:
                    return res
            return cmp(self.getWeight(), other.getWeight())
        else:
            return 1


class SeriesAchievement(RegularAchievement):

    def getMaxSeriesInfo(self):
        return (self._getCounterRecordNames()[1], self.getValue())

    def getI18nValue(self):
        return BigWorld.wg_getIntegralFormat(self._value)

    def _getCounterRecordNames(self):
        return (None, None)

    def _readValue(self, dossier):
        record = self._getCounterRecordNames()[1]
        if record is not None:
            return dossier.getRecordValue(*record)
        else:
            return 0

    def _readLevelUpTotalValue(self, dossier):
        return self._value + 1

    def _readLevelUpValue(self, dossier):
        record = self._getCounterRecordNames()[0]
        if record is not None:
            return self._lvlUpTotalValue - dossier.getRecordValue(*record)
        else:
            return 0


class DeprecatedAchievement(RegularAchievement):

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return cls.checkIsInDossier(block, name, dossier)


class SimpleProgressAchievement(RegularAchievement):

    def __init__(self, name, block, dossier, value = None):
        if dossier is not None:
            self._progressValue = self._readProgressValue(dossier)
        else:
            self._progressValue = 0
        super(SimpleProgressAchievement, self).__init__(name, block, dossier, value)
        return

    def getProgressValue(self):
        if not self._lvlUpTotalValue:
            return 1.0
        return 1 - float(self._lvlUpValue) / float(self._lvlUpTotalValue)

    def isInNear(self):
        return self.getProgressValue() > 0

    def hasProgress(self):
        return not self._isDone

    def _readLevelUpValue(self, dossier):
        minValue = RECORD_CONFIGS[self._name]
        medals, series = divmod(self._progressValue, minValue)
        return minValue - series

    def _readLevelUpTotalValue(self, dossier):
        return RECORD_CONFIGS[self._name]

    def _readProgressValue(self, dossier):
        return 0


class NationSpecificAchievement(SimpleProgressAchievement):

    def __init__(self, namePrefix, nationID, block, dossier, value = None):
        self._nationID = nationID
        super(NationSpecificAchievement, self).__init__(self.makeFullName(namePrefix, nationID), block, dossier, value)

    @classmethod
    def makeFullName(cls, name, nationID):
        if nationID != -1:
            name += str(nationID)
        return name

    def getNationID(self):
        return self._nationID

    def _readValue(self, dossier):
        return 0

    def _readLevelUpTotalValue(self, dossier):
        cache = getDossiersCache()
        if self._nationID != -1:
            return len(cache['vehiclesInTreesByNation'][self._nationID])
        else:
            return len(cache['vehiclesInTrees'])

    def _getDoneStatus(self, dossier):
        return bool(dossier.getRecordValue(*self.getRecordName()))

    def __cmp__(self, other):
        res = super(NationSpecificAchievement, self).__cmp__(other)
        if res:
            return res
        if isinstance(other, NationSpecificAchievement):
            if self._nationID != -1 and other._nationID != -1:
                return nationCompareByIndex(self._nationID, other._nationID)
        return 0


class ClassProgressAchievement(SimpleProgressAchievement):
    MIN_LVL = 4
    NO_LVL = 5

    def __init__(self, name, block, dossier, value = None):
        if dossier is not None:
            self._currentProgressValue = self._readCurrentProgressValue(dossier)
        else:
            self._currentProgressValue = 0
        super(ClassProgressAchievement, self).__init__(name, block, dossier, value)
        return

    def getUserName(self):
        i18nRank = i18n.makeString('#achievements:achievement/rank%d' % (self._value or self.MIN_LVL))
        return super(ClassProgressAchievement, self).getUserName() % {'rank': i18nRank}

    def getValue(self):
        return self._value or self.NO_LVL

    def getI18nValue(self):
        return BigWorld.wg_getIntegralFormat(self._value)

    def getProgressValue(self):
        if self._progressValue == 1:
            return 1.0
        elif self._lvlUpTotalValue == 0:
            return 1.0
        else:
            return 1 - float(self._lvlUpValue) / float(self._lvlUpTotalValue)

    def isInNear(self):
        return self.getProgressValue() >= 0.95 or self._lvlUpValue == 1

    def _readLevelUpTotalValue(self, dossier):
        if self._name not in RECORD_CONFIGS:
            return 0
        progressValue = self._progressValue or self.NO_LVL
        medalCfg = RECORD_CONFIGS[self._name]
        maxMedalClass = len(medalCfg)
        nextMedalClass = progressValue - 1
        nextMedalClassIndex = maxMedalClass - nextMedalClass
        if nextMedalClass <= 0:
            return 0.0
        elif nextMedalClass <= maxMedalClass:
            return medalCfg[nextMedalClassIndex]
        else:
            return 1.0

    def _readLevelUpValue(self, dossier):
        if self._progressValue == 1:
            return 0.0
        else:
            return max(float(self._lvlUpTotalValue) - float(self._currentProgressValue), 0.0)

    def _readCurrentProgressValue(self, dossier):
        return 0

    def _getIconName(self):
        return '%s%d' % (self._name, self._value or self.MIN_LVL)


class TacticalBreakthroughAchievement(SeriesAchievement):

    def __init__(self, dossier, value = None):
        super(TacticalBreakthroughAchievement, self).__init__('tacticalBreakthrough', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TEAM_7X7, 'tacticalBreakthroughSeries'), (_AB.TEAM_7X7, 'maxTacticalBreakthroughSeries'))


class DiehardAchievement(SeriesAchievement):

    def __init__(self, dossier, value = None):
        super(DiehardAchievement, self).__init__('diehard', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'diehardSeries'), (_AB.TOTAL, 'maxDiehardSeries'))


class InvincibleAchievement(SeriesAchievement):

    def __init__(self, dossier, value = None):
        super(InvincibleAchievement, self).__init__('invincible', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'invincibleSeries'), (_AB.TOTAL, 'maxInvincibleSeries'))


class HandOfDeathAchievement(SeriesAchievement):

    def __init__(self, dossier, value = None):
        super(HandOfDeathAchievement, self).__init__('handOfDeath', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'killingSeries'), (_AB.TOTAL, 'maxKillingSeries'))


class ArmorPiercerAchievement(SeriesAchievement):

    def __init__(self, dossier, value = None):
        super(ArmorPiercerAchievement, self).__init__('armorPiercer', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'piercingSeries'), (_AB.TOTAL, 'maxPiercingSeries'))


class TitleSniperAchievement(SeriesAchievement):

    def __init__(self, dossier, value = None):
        super(TitleSniperAchievement, self).__init__('titleSniper', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'sniperSeries'), (_AB.TOTAL, 'maxSniperSeries'))


class TankExpertAchievement(NationSpecificAchievement, _HasVehiclesList):

    def __init__(self, nationID, block, dossier, value = None):
        self.__vehTypeCompDescrs = self._parseVehiclesDescrsList(NationSpecificAchievement.makeFullName('tankExpert', nationID), dossier)
        NationSpecificAchievement.__init__(self, 'tankExpert', nationID, block, dossier, value)
        _HasVehiclesList.__init__(self)
        self.__achieved = dossier is not None and bool(dossier.getRecordValue(*self.getRecordName()))
        return

    def isActive(self):
        return self.__achieved

    def getVehiclesListTitle(self):
        return 'vehiclesToKill'

    def _readLevelUpValue(self, dossier):
        return len(self.getVehiclesData())

    def _getVehiclesDescrsList(self):
        return self.__vehTypeCompDescrs

    @classmethod
    def _parseVehiclesDescrsList(cls, name, dossier):
        if dossier is not None:
            return getTankExpertRequirements(dossier.getBlock('vehTypeFrags')).get(name, [])
        else:
            return []


class MechEngineerAchievement(NationSpecificAchievement, _HasVehiclesList):

    def __init__(self, nationID, block, dossier, value = None):
        self.__vehTypeCompDescrs = self._parseVehiclesDescrsList(NationSpecificAchievement.makeFullName('mechanicEngineer', nationID), nationID, dossier)
        NationSpecificAchievement.__init__(self, 'mechanicEngineer', nationID, block, dossier, value)
        _HasVehiclesList.__init__(self)

    def getVehiclesListTitle(self):
        return 'vehiclesToResearch'

    def isActive(self):
        return not len(self.getVehiclesData())

    def _readLevelUpValue(self, dossier):
        return len(self.getVehiclesData())

    def _getVehiclesDescrsList(self):
        return self.__vehTypeCompDescrs

    @classmethod
    def _parseVehiclesDescrsList(cls, name, nationID, dossier):
        if dossier is not None and dossier.isCurrentUser():
            from gui.shared import g_itemsCache
            return getMechanicEngineerRequirements(set(), g_itemsCache.items.stats.unlocks, nationID).get(name, [])
        else:
            return []


class WhiteTigerAchievement(RegularAchievement):
    WHITE_TIGER_COMP_DESCR = 56337

    def __init__(self, dossier, value = None):
        super(WhiteTigerAchievement, self).__init__('whiteTiger', _AB.CLIENT, dossier, value)

    @classmethod
    def checkIsInDossier(cls, block, name, dossier):
        if dossier is not None:
            return bool(cls.__getWhiteTigerKillings(dossier))
        else:
            return False

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        if dossier is not None:
            return cls.checkIsInDossier(block, name, dossier) and not dossier.isInRoaming()
        else:
            return False

    def _readValue(self, dossier):
        return self.__getWhiteTigerKillings(dossier)

    @classmethod
    def __getWhiteTigerKillings(cls, dossier):
        return dossier.getBlock('vehTypeFrags').get(cls.WHITE_TIGER_COMP_DESCR, 0)


class MousebaneAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MousebaneAchievement, self).__init__('mousebane', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getBlock('vehTypeFrags').get(getDossiersCache()['mausTypeCompDescr'], 0)


class BeasthunterAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(BeasthunterAchievement, self).__init__('beasthunter', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'fragsBeast')


class PattonValleyAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(PattonValleyAchievement, self).__init__('pattonValley', _AB.TOTAL, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'fragsPatton')


class SinaiAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(SinaiAchievement, self).__init__('sinai', _AB.TOTAL, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'fragsSinai')


class MarkOnGunAchievement(RegularAchievement):
    IT_95X85 = '95x85'

    def __init__(self, dossier, value = None):
        super(MarkOnGunAchievement, self).__init__('marksOnGun', _AB.TOTAL, dossier, value)
        self.__nationId = self._readVehicleNationID(dossier)
        self.__damageRating = self._readDamageRating(dossier)

    def setVehicleNationID(self, nationID):
        self.__nationId = nationID

    def getVehicleNationID(self):
        return self.__nationId

    def getUserCondition(self):
        return i18n.makeString('#achievements:marksOnGun_condition')

    def setDamageRating(self, val):
        self.__damageRating = val

    def getDamageRating(self):
        return self.__damageRating

    def getIcons(self):
        return {self.ICON_TYPE.IT_180X180: self.__getIconPath(self.ICON_TYPE.IT_180X180),
         self.ICON_TYPE.IT_67X71: self.__getIconPath(self.ICON_TYPE.IT_67X71),
         self.ICON_TYPE.IT_32X32: self.__getIconPath(self.ICON_TYPE.IT_32X32),
         self.IT_95X85: self.__getIconPath(self.IT_95X85)}

    def getI18nValue(self):
        if self.__damageRating > 0:
            return makeHtmlString('html_templates:lobby/tooltips/achievements', 'marksOnGun', {'count': BigWorld.wg_getNiceNumberFormat(self.__damageRating)})
        return ''

    def _getActualName(self):
        return '%s%d' % (self._name, self._value)

    @classmethod
    def _readDamageRating(cls, dossier):
        if dossier is not None:
            return dossier.getRecordValue(_AB.TOTAL, 'damageRating') / 100.0
        else:
            return 0.0

    @classmethod
    def _readVehicleNationID(cls, dossier):
        if dossier is not None:
            return vehicles.parseIntCompactDescr(dossier.getCompactDescriptor())[1]
        else:
            return 0

    def __getIconPath(self, dir_):
        currentValue = 3 if self._value == 0 else self._value
        markCtx = 'mark' if currentValue < 2 else 'marks'
        return '../maps/icons/marksOnGun/%s/%s_%s_%s.png' % (dir_,
         NATION_NAMES[self.__nationId],
         currentValue,
         markCtx)

    def __repr__(self):
        return 'MarkOnGunAchievement<value=%s; damageRating=%.2f>' % (str(self._value), float(self.__damageRating))


class MarkOfMasteryAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MarkOfMasteryAchievement, self).__init__('markOfMastery', _AB.TOTAL, dossier, value)

    def getUserName(self):
        i18nRank = i18n.makeString('#achievements:achievement/master%d' % (self._value or self.MIN_LVL))
        return super(ClassProgressAchievement, self).getUserName() % {'name': i18nRank}


class MedalKnispelAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalKnispelAchievement, self).__init__('medalKnispel', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('damageLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalKnispel')

    def _readCurrentProgressValue(self, dossier):
        random, _7x7 = dossier.getRandomStats(), dossier.getTeam7x7Stats()
        return random.getDamageDealt() + random.getDamageReceived() + _7x7.getDamageDealt() + _7x7.getDamageReceived()


class MedalCariusAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalCariusAchievement, self).__init__('medalCarius', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalCarius')

    def _readCurrentProgressValue(self, dossier):
        random, _7x7 = dossier.getRandomStats(), dossier.getTeam7x7Stats()
        return random.getFragsCount() + _7x7.getFragsCount()


class MedalAbramsAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalAbramsAchievement, self).__init__('medalAbrams', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('battlesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalAbrams')

    def _readCurrentProgressValue(self, dossier):
        random, _7x7 = dossier.getRandomStats(), dossier.getTeam7x7Stats()
        return random.getWinAndSurvived() + _7x7.getWinAndSurvived()


class MedalPoppelAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalPoppelAchievement, self).__init__('medalPoppel', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalPoppel')

    def _readCurrentProgressValue(self, dossier):
        random, _7x7 = dossier.getRandomStats(), dossier.getTeam7x7Stats()
        return random.getSpottedEnemiesCount() + _7x7.getSpottedEnemiesCount()


class MedalKayAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalKayAchievement, self).__init__('medalKay', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('heroesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalKay')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'battleHeroes')


class MedalEkinsAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalEkinsAchievement, self).__init__('medalEkins', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalEkins')

    def _readCurrentProgressValue(self, dossier):
        random, _7x7 = dossier.getRandomStats(), dossier.getTeam7x7Stats()
        return random.getFrags8p() + _7x7.getFrags8p()


class MedalLeClercAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalLeClercAchievement, self).__init__('medalLeClerc', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('capturePointsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalLeClerc')

    def _readCurrentProgressValue(self, dossier):
        random, _7x7 = dossier.getRandomStats(), dossier.getTeam7x7Stats()
        return random.getCapturePoints() + _7x7.getCapturePoints()


class MedalLavrinenkoAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalLavrinenkoAchievement, self).__init__('medalLavrinenko', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('dropPointsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalLavrinenko')

    def _readCurrentProgressValue(self, dossier):
        random, _7x7 = dossier.getRandomStats(), dossier.getTeam7x7Stats()
        return random.getDroppedCapturePoints() + _7x7.getDroppedCapturePoints()


class MakerOfHistoryAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MakerOfHistoryAchievement, self).__init__('makerOfHistory', _AB.HISTORICAL, dossier, value)

    def getNextLevelInfo(self):
        return ('pairWinsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.HISTORICAL, 'makerOfHistory')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.HISTORICAL, 'bothSidesWins')


class GuardsmanAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(GuardsmanAchievement, self).__init__('guardsman', _AB.HISTORICAL, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.HISTORICAL, 'guardsman')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.HISTORICAL, 'weakVehiclesWins')


class MedalRotmistrovAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalRotmistrovAchievement, self).__init__('medalRotmistrov', _AB.CLAN, dossier, value)

    def getNextLevelInfo(self):
        return ('battlesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.CLAN, 'medalRotmistrov')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getClanStats().getBattlesCount()


class RareAchievement(RegularAchievement):
    SHOW_COUNTER = True

    def __init__(self, rareID, dossier, value = None):
        self._rareID = int(rareID)
        super(RareAchievement, self).__init__(rareID, _AB.RARE, dossier, value)

    def getRareID(self):
        return self._rareID

    def getRecordName(self):
        return (_AB.RARE, self._rareID)

    def getUserName(self):
        return g_rareAchievesCache.getTitle(self._rareID)

    def getUserDescription(self):
        return g_rareAchievesCache.getDescription(self._rareID)

    @classmethod
    def checkIsInDossier(cls, block, rareID, dossier):
        if dossier is not None:
            return rareID in dossier.getBlock(_AB.RARE)
        else:
            return False

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        if dossier is not None:
            return not dossier.isInRoaming()
        else:
            return True

    def getUserHeroInfo(self):
        return g_rareAchievesCache.getHeroInfo(self._rareID)

    def getUserCondition(self):
        return g_rareAchievesCache.getConditions(self._rareID)

    def hasCounter(self):
        return self.SHOW_COUNTER and self._value > 1

    def requestImageID(self):
        return self._requestImageID(IMAGE_TYPE.IT_67X71)

    def requestBigImageID(self):
        return self._requestImageID(IMAGE_TYPE.IT_180X180)

    def _readValue(self, dossier):
        return dossier.getBlock(_AB.RARE).count(self._rareID)

    def _requestImageID(self, imgType):
        g_rareAchievesCache.request([self._rareID])
        memImgID = None
        iconData = g_rareAchievesCache.getImageData(imgType, self._rareID)
        if iconData and imghdr.what(None, iconData) is not None:
            memImgID = str(uuid.uuid4())
            BigWorld.wg_addTempScaleformTexture(memImgID, iconData)
        return memImgID

    def getIcons(self):
        memImgID = self.requestImageID()
        icons = super(RareAchievement, self).getIcons()
        if memImgID is not None:
            icons[self.ICON_TYPE.IT_67X71] = 'img://%s' % str(memImgID)
        memBigImgID = self.requestBigImageID()
        if memBigImgID is not None:
            icons[self.ICON_TYPE.IT_180X180] = 'img://%s' % str(memBigImgID)
        return icons

    def _getIconName(self):
        return 'actionUnknown'

    def __repr__(self):
        return '%s<rareID=%s; value=%s>' % (self.__class__.__name__, str(self._rareID), str(self._value))


class GeniusForWarAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(GeniusForWarAchievement, self).__init__('geniusForWarMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'geniusForWar')


class WolfAmongSheepAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(WolfAmongSheepAchievement, self).__init__('wolfAmongSheepMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'wolfAmongSheep')


class FightingReconnaissanceAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(FightingReconnaissanceAchievement, self).__init__('fightingReconnaissanceMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'fightingReconnaissance')


class CrucialShotAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(CrucialShotAchievement, self).__init__('crucialShotMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'crucialShot')


class ForTacticalOperationsAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(ForTacticalOperationsAchievement, self).__init__('forTacticalOperations', _AB.TEAM_7X7, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'forTacticalOperations')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getTeam7x7Stats().getWinsCount()


class BattleTestedAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(BattleTestedAchievement, self).__init__('battleTested', _AB.TEAM_7X7, dossier, value)

    def getNextLevelInfo(self):
        return ('achievesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'battleTested')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'awardCount')


class GuerrillaAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(GuerrillaAchievement, self).__init__('guerrillaMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'guerrilla')


class InfiltratorAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(InfiltratorAchievement, self).__init__('infiltratorMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'infiltrator')


class SentinelAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(SentinelAchievement, self).__init__('sentinelMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'sentinel')


class PrematureDetonationAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(PrematureDetonationAchievement, self).__init__('prematureDetonationMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'prematureDetonation')


class BruteForceAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(BruteForceAchievement, self).__init__('bruteForceMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'bruteForce')


class FireAndSwordAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(FireAndSwordAchievement, self).__init__('fireAndSword', _AB.FORT, dossier, value)

    def getNextLevelInfo(self):
        return ('fortDefResLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FORT, 'fireAndSword')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getFortMiscStats().getLootInBattles()


class SoldierOfFortuneAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(SoldierOfFortuneAchievement, self).__init__('soldierOfFortune', _AB.FORT, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FORT, 'soldierOfFortune')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getFortBattlesStats().getBattlesCount()


class _FortClassAchievement(ClassProgressAchievement):

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        return isFortificationEnabled()


class KampferAchievement(_FortClassAchievement):

    def __init__(self, dossier, value = None):
        super(KampferAchievement, self).__init__('kampfer', _AB.FORT, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FORT, 'kampfer')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getFortSortiesStats().getWinsCount()


class ConquerorAchievement(_FortClassAchievement):

    def __init__(self, dossier, value = None):
        super(ConquerorAchievement, self).__init__('conqueror', _AB.FORT, dossier, value)

    def getNextLevelInfo(self):
        return ('fortDefResLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FORT, 'conqueror')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getFortMiscStats().getLootInSorties()


class PromisingFighterAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(PromisingFighterAchievement, self).__init__('promisingFighterMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'promisingFighter')


class HeavyFireAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(HeavyFireAchievement, self).__init__('heavyFireMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'heavyFire')


class RangerAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(RangerAchievement, self).__init__('rangerMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'ranger')


class FireAndSteelAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(FireAndSteelAchievement, self).__init__('fireAndSteelMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'fireAndSteel')


class PyromaniacAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(PyromaniacAchievement, self).__init__('pyromaniacMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'pyromaniac')


class QuestAchievement(RegularAchievement):

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        from gui.shared import g_eventsCache
        for records in g_eventsCache.getQuestsDossierBonuses().itervalues():
            if (block, name) in records:
                return True

        return cls.checkIsInDossier(block, name, dossier)


class QuestSeriesAchievement(SeriesAchievement):

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        from gui.shared import g_eventsCache
        for records in g_eventsCache.getQuestsDossierBonuses().itervalues():
            if (block, name) in records:
                return True

        return cls.checkIsInDossier(block, name, dossier)


class WFC2014Achievement(QuestSeriesAchievement):

    def __init__(self, dossier, value = None):
        super(WFC2014Achievement, self).__init__('WFC2014', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'WFC2014WinSeries'), (_AB.TOTAL, 'maxWFC2014WinSeries'))


class UniqueAchievement(RegularAchievement):
    pass


class HistoricalAchievement(UniqueAchievement, _HasVehiclesList):

    @classmethod
    def checkIsValid(cls, block, name, dossier):
        quest = cls.__getQuestByDossierRecord(name)
        if quest is not None:
            return True
        else:
            return cls.checkIsInDossier(block, name, dossier)

    def getVehiclesListTitle(self):
        return 'vehiclesTakePart'

    def _getVehiclesDescrsList(self):
        vehsList = []
        try:
            from gui.shared import g_eventsCache
            for qIDs in self.__getQuestByDossierRecord(self._name).getChildren().itervalues():
                for qID in qIDs:
                    counterQuest = g_eventsCache.getQuests().get(qID)
                    histBattleCond = counterQuest.preBattleCond.getConditions().find('historicalBattleIDs')
                    allVehsCompDescrs = set()
                    for hID in histBattleCond._battlesIDs:
                        hb = g_eventsCache.getHistoricalBattles().get(hID)
                        if hb is not None:
                            allVehsCompDescrs.update(hb.getVehiclesData().keys())

                    vehsList = filter(lambda intCD: not counterQuest.isCompletedByGroup(intCD), allVehsCompDescrs)
                    break

        except Exception:
            pass

        return vehsList

    @classmethod
    def __getQuestByDossierRecord(cls, name):
        from gui.shared import g_eventsCache
        for qID, records in g_eventsCache.getQuestsDossierBonuses().iteritems():
            if (_AB.UNIQUE, name) in records:
                return g_eventsCache.getQuests().get(qID)

        return None
