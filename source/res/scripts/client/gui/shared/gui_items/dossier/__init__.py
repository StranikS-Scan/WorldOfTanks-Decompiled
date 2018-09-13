# Embedded file name: scripts/client/gui/shared/gui_items/dossier/__init__.py
import math
import cPickle
import BigWorld
import dossiers2
from constants import DOSSIER_TYPE
from items import tankmen
from helpers import i18n
from gui.shared.gui_items import GUIItem
from gui.shared.gui_items.dossier import stats
from gui.shared.gui_items.dossier.factories import getAchievementFactory

def loadDossier(dumpData):
    args = cPickle.loads(dumpData)
    return args[0].unpack(*args[1:])


def dumpDossier(dossierItem):
    return cPickle.dumps(dossierItem.pack())


class _Dossier(GUIItem):

    def __init__(self, dossier, dossierType, playerDBID = None):
        super(GUIItem, self).__init__()
        self._dossier = dossier
        self._dossierType = dossierType
        self._playerDBID = playerDBID

    def getBlock(self, blockName):
        return self._dossier[blockName]

    def getRecordValue(self, blockName, keyName):
        return self._dossier[blockName][keyName]

    def getDossierDescr(self):
        return self._dossier

    def getDossierType(self):
        return self._dossierType

    def getPlayerDBID(self):
        return self._playerDBID

    def isInRoaming(self):
        if not self.isCurrentUser():
            from gui import game_control
            return game_control.g_instance.roaming.isInRoaming() or game_control.g_instance.roaming.isPlayerInRoaming(self._playerDBID)
        return False

    def isCurrentUser(self):
        return self._playerDBID is None


class VehicleDossier(_Dossier, stats.VehicleDossierStats):

    def __init__(self, dossier, vehTypeCompDescr, playerDBID = None):
        super(VehicleDossier, self).__init__(dossier, DOSSIER_TYPE.VEHICLE, playerDBID)
        self.__vehTypeCompDescr = vehTypeCompDescr

    def getCompactDescriptor(self):
        return self.__vehTypeCompDescr

    def pack(self):
        return (VehicleDossier,
         self._dossier.makeCompDescr(),
         self.__vehTypeCompDescr,
         self._playerDBID)

    @staticmethod
    def unpack(dossierCD, vehTypeCD, isCurrentUser):
        return VehicleDossier(dossiers2.getVehicleDossierDescr(dossierCD), vehTypeCD, isCurrentUser)

    def _getDossierItem(self):
        return self

    def __repr__(self):
        return 'VehicleDossier<vehTypeCD=%d; playerDBID=%r; roaming=%r>' % (self.__vehTypeCompDescr, self._playerDBID, self.isInRoaming())


class AccountDossier(_Dossier, stats.AccountDossierStats):

    def __init__(self, dossier, playerDBID = None):
        super(AccountDossier, self).__init__(dossier, DOSSIER_TYPE.ACCOUNT, playerDBID)

    def getGlobalRating(self):
        from gui.shared import g_itemsCache
        return g_itemsCache.items.stats.getGlobalRating()

    def pack(self):
        return (AccountDossier, self._dossier.makeCompDescr(), self._playerDBID)

    @staticmethod
    def unpack(dossierCD, playerDBID):
        return AccountDossier(dossiers2.getAccountDossierDescr(dossierCD), playerDBID)

    def _getDossierItem(self):
        return self

    def __repr__(self):
        return 'AccountDossier<playerDBID=%r; roaming=%r>' % (self._playerDBID, self.isInRoaming())


class TankmanDossier(_Dossier, stats.TankmanDossierStats):

    def __init__(self, tmanDescr, dossier, extDossier, playerDBID = None):
        raise extDossier is not None or AssertionError
        super(TankmanDossier, self).__init__(dossier, DOSSIER_TYPE.TANKMAN, playerDBID)
        self.tmanDescr = tmanDescr
        self.extStats = extDossier.getRandomStats()
        self.addStats = extDossier.getTeam7x7Stats()
        self.__extDossierDump = dumpDossier(extDossier)
        return

    def pack(self):
        return (TankmanDossier,
         self.tmanDescr.makeCompactDescr(),
         self._dossier.makeCompDescr(),
         self.__extDossierDump)

    @staticmethod
    def unpack(tmanCompDescr, dossierCD, extDossierDump):
        return TankmanDossier(tankmen.TankmanDescr(tmanCompDescr), dossiers2.getTankmanDossierDescr(dossierCD), loadDossier(extDossierDump))

    def getNextSkillXPLeft(self):
        if self.tmanDescr.roleLevel != tankmen.MAX_SKILL_LEVEL or not self.__isNewSkillReady():
            return self.__getSkillNextLevelCost()
        return 0

    def getAvgXP(self):
        totalXP = self.extStats.getXP() + self.addStats.getXP()
        totalBattles = self.extStats.getBattlesCount() + self.addStats.getBattlesCount()
        if totalBattles == 0:
            return 0
        return totalXP / totalBattles

    def getBattlesCount(self):
        return self.getTotalStats().getBattlesCount()

    def getNextSkillBattlesLeft(self):
        if not self.getBattlesCount() or not self.extStats.getBattlesCount() or not self.extStats.getXP():
            return None
        avgExp = self.getAvgXP()
        newSkillReady = self.tmanDescr.roleLevel == tankmen.MAX_SKILL_LEVEL and (len(self.tmanDescr.skills) == 0 or self.tmanDescr.lastSkillLevel == tankmen.MAX_SKILL_LEVEL)
        if avgExp and not newSkillReady:
            return max(1, math.ceil(self.__getSkillNextLevelCost() / avgExp))
        else:
            return 0

    def getStats(self):
        nextSkillsBattlesLeft = self.getNextSkillBattlesLeft()
        nextSkillBattlesLeftExtra = ''
        if nextSkillsBattlesLeft is not None:
            nextSkillsBattlesLeft = BigWorld.wg_getIntegralFormat(nextSkillsBattlesLeft)
        else:
            nextSkillBattlesLeftExtra = '(%s)' % i18n.makeString('#menu:profile/stats/items/unknown')
        skillImgType, skillImg = self.__getCurrentSkillIcon()
        return ({'label': 'common',
          'stats': (self.__packStat('battlesCount', BigWorld.wg_getNiceNumberFormat(self.getBattlesCount())),)}, {'label': 'studying',
          'stats': (self.__packStat('nextSkillXPLeft', BigWorld.wg_getIntegralFormat(self.getNextSkillXPLeft()), imageType=skillImgType, image=skillImg), self.__packStat('avgExperience', BigWorld.wg_getIntegralFormat(self.getAvgXP())), self.__packStat('nextSkillBattlesLeft', nextSkillsBattlesLeft, nextSkillBattlesLeftExtra))})

    def _getDossierItem(self):
        return self

    def __isNewSkillReady(self):
        return self.tmanDescr.roleLevel == tankmen.MAX_SKILL_LEVEL and (not len(self.tmanDescr.skills) or self.tmanDescr.lastSkillLevel == tankmen.MAX_SKILL_LEVEL)

    def __getSkillNextLevelCost(self):
        skillsCount = len(self.tmanDescr.skills)
        lastSkillLevel = self.tmanDescr.lastSkillLevel
        if not skillsCount or self.tmanDescr.roleLevel != tankmen.MAX_SKILL_LEVEL:
            lastSkillLevel = self.tmanDescr.roleLevel
        return self.tmanDescr.levelUpXpCost(lastSkillLevel, skillsCount if self.tmanDescr.roleLevel == tankmen.MAX_SKILL_LEVEL else 0) - self.tmanDescr.freeXP

    def __getCurrentSkillIcon(self):
        if self.__isNewSkillReady():
            return ('new_skill', 'new_skill.png')
        if self.tmanDescr.roleLevel != tankmen.MAX_SKILL_LEVEL or not len(self.tmanDescr.skills):
            return ('role', '%s.png' % self.tmanDescr.role)
        return ('skill', tankmen.getSkillsConfig()[self.tmanDescr.skills[-1]]['icon'])

    @classmethod
    def __packStat(cls, name, value, extra = '', imageType = None, image = None):
        return {'name': name,
         'value': value,
         'extra': extra,
         'imageType': imageType,
         'image': image}

    def __repr__(self):
        return ('TankmanDossier<extStats=%r; addStats=%r>' % self.extStats, self.addStats)


class FortDossier(_Dossier, stats.FortDossierStats):

    def __init__(self, dossier, playerDBID = False):
        super(FortDossier, self).__init__(dossier, DOSSIER_TYPE.FORTIFIED_REGIONS, playerDBID)

    def pack(self):
        return (FortDossier, self._dossier.makeCompactDescr(), self._playerDBID)

    @staticmethod
    def unpack(dossierCD, playerDBID):
        return FortDossier(dossiers2.getFortifiedRegionsDossierDescr(dossierCD), playerDBID)

    def _getDossierItem(self):
        return self

    def __repr__(self):
        return 'FortDossier<playerDBID=%r; roaming=%r>' % (self._playerDBID, self.isInRoaming())
