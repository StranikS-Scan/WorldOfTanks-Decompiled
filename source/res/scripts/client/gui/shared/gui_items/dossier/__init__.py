# Embedded file name: scripts/client/gui/shared/gui_items/dossier/__init__.py
import math
import cPickle
import BigWorld
import dossiers2
from constants import DOSSIER_TYPE
from gui.Scaleform.locale.MENU import MENU
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
            from gui.LobbyContext import g_lobbyContext
            serverSettings = g_lobbyContext.getServerSettings()
            if serverSettings is not None:
                roaming = serverSettings.roaming
                return roaming.isInRoaming() or roaming.isPlayerInRoaming(self._playerDBID)
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

    def __init__(self, dossier, playerDBID = None, rated7x7Seasons = None):
        super(AccountDossier, self).__init__(dossier, DOSSIER_TYPE.ACCOUNT, playerDBID)
        self._rated7x7Seasons = rated7x7Seasons or {}

    def getGlobalRating(self):
        from gui.shared import g_itemsCache
        return g_itemsCache.items.stats.globalRating

    def pack(self):
        return (AccountDossier,
         self._dossier.makeCompDescr(),
         self._playerDBID,
         self._rated7x7Seasons)

    @staticmethod
    def unpack(dossierCD, playerDBID, seasons):
        return AccountDossier(dossiers2.getAccountDossierDescr(dossierCD), playerDBID, seasons)

    def getRated7x7SeasonDossier(self, seasonID):
        return self._makeSeasonDossier(self._rated7x7Seasons.get(seasonID) or dossiers2.getRated7x7DossierDescr())

    def getRated7x7Seasons(self):
        result = {}
        for sID, d in self._rated7x7Seasons.iteritems():
            result[sID] = self._makeSeasonDossier(d)

        return result

    def _makeSeasonDossier(self, dossierDescr):
        return ClubMemberDossier(dossierDescr, -1, self._playerDBID)

    def _getDossierItem(self):
        return self

    def __repr__(self):
        return 'AccountDossier<playerDBID=%r; roaming=%r>' % (self._playerDBID, self.isInRoaming())


class TankmanDossier(_Dossier, stats.TankmanDossierStats):
    PREMIUM_TANK_DEFAULT_CREW_XP_FACTOR = 1.5

    def __init__(self, tmanDescr, tankmanDossierDescr, extDossier, playerDBID = None, currentVehicleItem = None):
        raise extDossier is not None or AssertionError
        super(TankmanDossier, self).__init__(tankmanDossierDescr, DOSSIER_TYPE.TANKMAN, playerDBID)
        currentVehicleType = currentVehicleItem.descriptor.type if currentVehicleItem else None
        self.tmanDescr = tmanDescr
        self.__totalStats = extDossier.getTotalStats()
        self.__globalMapStats = extDossier.getGlobalMapStats()
        self.__clanStats = extDossier.getClanStats()
        self.__extDossierDump = dumpDossier(extDossier)
        self.__currentVehicleIsPremium = currentVehicleItem and currentVehicleItem.isPremium
        self.__currentVehicleCrewXpFactor = currentVehicleType.crewXpFactor if currentVehicleType else 1.0
        return

    def pack(self):
        return (TankmanDossier,
         self.tmanDescr.makeCompactDescr(),
         self._dossier.makeCompDescr(),
         self.__extDossierDump)

    @staticmethod
    def unpack(tmanCompDescr, dossierCD, extDossierDump):
        return TankmanDossier(tankmen.TankmanDescr(tmanCompDescr), dossiers2.getTankmanDossierDescr(dossierCD), loadDossier(extDossierDump))

    def getAvgXP(self):
        totalXP = self.__totalStats.getXP() - self.__clanStats.getXP() + self.__globalMapStats.getXP()
        totalBattles = self.__totalStats.getBattlesCount() - self.__clanStats.getBattlesCount() + self.__globalMapStats.getBattlesCount()
        if totalBattles == 0:
            return 0
        return totalXP / totalBattles

    def getBattlesCount(self):
        return self.getTotalStats().getBattlesCount()

    def getStats(self, tankman):
        imageType, image = self.__getCurrentSkillIcon()
        return ({'label': 'common',
          'stats': (self.__packStat('battlesCount', self.getBattlesCount()), self.__packStat('avgExperience', self.getAvgXP()))}, {'label': 'studying',
          'secondLabel': i18n.makeString(MENU.CONTEXTMENU_PERSONALCASE_STATSBLOCKTITLE),
          'isPremium': self.__currentVehicleIsPremium,
          'stats': (self.__packStat('nextSkillXPLeft', tankman.getNextLevelXpCost(), imageType=imageType, image=image), self.__packStat('nextSkillBattlesLeft', self.__getNextSkillBattlesLeft(tankman), usePremiumXpFactor=True))})

    def _getDossierItem(self):
        return self

    def __isNewSkillReady(self):
        return self.tmanDescr.roleLevel == tankmen.MAX_SKILL_LEVEL and (not len(self.tmanDescr.skills) or self.tmanDescr.lastSkillLevel == tankmen.MAX_SKILL_LEVEL)

    def __getCurrentSkillIcon(self):
        if self.__isNewSkillReady():
            return ('new_skill', 'new_skill.png')
        if self.tmanDescr.roleLevel != tankmen.MAX_SKILL_LEVEL or not len(self.tmanDescr.skills):
            return ('role', '%s.png' % self.tmanDescr.role)
        return ('skill', tankmen.getSkillsConfig()[self.tmanDescr.skills[-1]]['icon'])

    def __getNextSkillBattlesLeft(self, tankman):
        if not self.getBattlesCount():
            result = None
        else:
            avgExp = self.getAvgXP()
            newSkillReady = self.tmanDescr.roleLevel == tankmen.MAX_SKILL_LEVEL and (len(self.tmanDescr.skills) == 0 or self.tmanDescr.lastSkillLevel == tankmen.MAX_SKILL_LEVEL)
            if avgExp and not newSkillReady:
                result = max(1, math.ceil(tankman.getNextLevelXpCost() / avgExp))
            else:
                result = 0
        return result

    def __formatValueForUI(self, value):
        if value is None:
            return '%s' % i18n.makeString('#menu:profile/stats/items/empty')
        else:
            return BigWorld.wg_getIntegralFormat(value)
            return

    def __getBattlesLeftOnPremiumVehicle(self, value):
        xpFactorToUse = self.PREMIUM_TANK_DEFAULT_CREW_XP_FACTOR
        if self.__currentVehicleIsPremium:
            xpFactorToUse = self.__currentVehicleCrewXpFactor
        if value is not None:
            if value != 0:
                return max(1, value / xpFactorToUse)
            return 0
        else:
            return

    def __packStat(self, name, value, imageType = None, image = None, usePremiumXpFactor = False):
        if usePremiumXpFactor:
            premiumValue = self.__getBattlesLeftOnPremiumVehicle(value)
        else:
            premiumValue = value
        value = self.__formatValueForUI(value)
        premiumValue = self.__formatValueForUI(premiumValue)
        return {'name': name,
         'value': value,
         'premiumValue': premiumValue,
         'imageType': imageType,
         'image': image}

    def __repr__(self):
        return 'TankmanDossier<stats.__totalStats=%r>' % self.__totalStats


class FortDossier(_Dossier, stats.FortDossierStats):

    def __init__(self, dossier, playerDBID = False):
        super(FortDossier, self).__init__(dossier, DOSSIER_TYPE.FORTIFIED_REGIONS, playerDBID)

    def pack(self):
        return (FortDossier, self._dossier.makeCompDescr(), self._playerDBID)

    @staticmethod
    def unpack(dossierCD, playerDBID):
        return FortDossier(dossiers2.getFortifiedRegionsDossierDescr(dossierCD), playerDBID)

    def _getDossierItem(self):
        return self

    def __repr__(self):
        return 'FortDossier<playerDBID=%r; roaming=%r>' % (self._playerDBID, self.isInRoaming())


class ClubDossier(_Dossier, stats.ClubDossierStats):

    def __init__(self, dossier, clubDbID):
        super(ClubDossier, self).__init__(dossier, DOSSIER_TYPE.CLUB)
        self._clubDbID = clubDbID

    def pack(self):
        return (ClubDossier, self._dossier.makeCompDescr(), self._clubDbID)

    @staticmethod
    def unpack(dossierCD, clubDbID):
        return ClubDossier(dossiers2.getClubDossierDescr(dossierCD), clubDbID)

    def getClubDbID(self):
        return self._clubDbID

    def _getDossierItem(self):
        return self


class ClubMemberDossier(_Dossier, stats.ClubMemberDossierStats):

    def __init__(self, dossier, clubDbID, memberDbID):
        super(ClubMemberDossier, self).__init__(dossier, DOSSIER_TYPE.RATED7X7, memberDbID)
        self._clubDbID = clubDbID

    def pack(self):
        return (ClubMemberDossier,
         self._dossier.makeCompactDescr(),
         self._clubDbID,
         self._playerDBID)

    @staticmethod
    def unpack(dossierCD, clubDbID, memberDbID):
        return ClubMemberDossier(dossiers2.getRated7x7DossierDescr(dossierCD), clubDbID, memberDbID)

    def getClubDbID(self):
        return self._clubDbID

    def _getDossierItem(self):
        return self
