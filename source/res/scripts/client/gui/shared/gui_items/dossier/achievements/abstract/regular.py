# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/regular.py
from gui.impl.gen import R
from helpers import i18n
from gui.impl import backport
from gui.shared.gui_items.gui_item import GUIItem
from dossiers2.custom.records import RECORD_MAX_VALUES
from dossiers2.ui import achievements

class RegularAchievement(GUIItem):
    __slots__ = ('_name', '_block', '_value', '_lvlUpValue', '_lvlUpTotalValue', '_isDone', '_isInDossier', '_isValid')

    class ICON_TYPE:
        IT_180X180 = '180x180'
        IT_67X71 = '67x71'
        IT_32X32 = '32x32'
        IT_80X80 = '80x80'

    ICON_PATH_180X180 = '../maps/icons/achievement/big'
    ICON_PATH_67X71 = '../maps/icons/achievement'
    ICON_PATH_32X32 = '../maps/icons/achievement/32x32'
    ICON_PATH_95X85 = '../maps/icons/achievement/95x85'
    ICON_PATH_80X80 = '../maps/icons/achievement/80x80'
    ICON_DEFAULT = '../maps/icons/achievement/noImage.png'

    def __init__(self, name, block, dossier, value=None):
        super(RegularAchievement, self).__init__()
        self._name = str(name)
        self._block = str(block)
        self._value = int(value or 0)
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

    def isApproachable(self):
        return self._getIconName() in achievements.BATTLE_APPROACHABLE_ACHIEVES

    def hasRibbon(self):
        return self._getIconName() in achievements.BATTLE_ACHIEVES_WITH_RIBBON

    def getI18nValue(self):
        maxValue = RECORD_MAX_VALUES.get(self.getRecordName())
        return i18n.makeString('#achievements:achievement/maxMedalValue') % backport.getIntegralFormat(maxValue - 1) if maxValue is not None and self._value >= maxValue else backport.getIntegralFormat(self._value)

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
        pass

    def hasProgress(self):
        return False

    def hasCounter(self):
        return bool(self._value)

    def getIcons(self):
        iconName = self._getIconName()
        return {self.ICON_TYPE.IT_180X180: '%s/%s.png' % (self.ICON_PATH_180X180, iconName),
         self.ICON_TYPE.IT_67X71: '%s/%s.png' % (self.ICON_PATH_67X71, iconName),
         self.ICON_TYPE.IT_32X32: '%s/%s.png' % (self.ICON_PATH_32X32, iconName),
         self.ICON_TYPE.IT_80X80: '%s/%s.png' % (self.ICON_PATH_80X80, iconName)}

    def getHugeIcon(self):
        return self.getIcons()[self.ICON_TYPE.IT_180X180]

    def getBigIcon(self):
        iconName = self._getIconName()
        if len(iconName) > 0 and iconName[0].isdigit():
            iconName = 'c_' + iconName
        iconRes = R.images.gui.maps.icons.achievement.c_80x80.dyn(iconName)
        if iconRes.exists():
            return backport.image(iconRes())
        else:
            return self.getSmallIcon()

    def getBig80x80Icon(self):
        return self.getIcons()[self.ICON_TYPE.IT_80X80]

    def getSmallIcon(self):
        return self.getIcons()[self.ICON_TYPE.IT_67X71]

    def getIcon32x32(self):
        return self.getIcons()[self.ICON_TYPE.IT_32X32]

    def getUserName(self):
        return i18n.makeString('#achievements:%s' % self._getActualName())

    def getUserDescription(self):
        return i18n.makeString('#achievements:%s_descr' % self._getActualName())

    def getUserWebDescription(self):
        return self.getUserDescription()

    def getUserHeroInfo(self):
        heroInfoKey = '#achievements:%s_heroInfo' % self._getActualName()
        return i18n.makeString(heroInfoKey) if i18n.doesTextExist(heroInfoKey) else ''

    def getNotificationInfo(self):
        notificationKey = '#achievements:%s_notification' % self._getActualName()
        return i18n.makeString(notificationKey) if i18n.doesTextExist(notificationKey) else ''

    def getShowCondSeparator(self):
        return True

    def getUserCondition(self):
        condKey = '#achievements:%s_condition' % self._getActualName()
        return i18n.makeString(condKey) if i18n.doesTextExist(condKey) else ''

    def isAvailableInQuest(self):
        return True

    def isHidden(self):
        return self._name.startswith('epicBattle') and not self._isInDossier

    @classmethod
    def checkIsInDossier(cls, block, name, dossier):
        if dossier is not None:
            a = bool(dossier.getRecordValue(block, name))
            return a
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
