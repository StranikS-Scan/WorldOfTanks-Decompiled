# Embedded file name: scripts/client/gui/battle_control/BattleContext.py
import BigWorld
import Settings
from gui import game_control
from gui.battle_control.battle_constants import PLAYER_ENTITY_NAME
defNormalizePNameFunction = lambda pName: pName

class BattleContext(object):

    class FORMAT_MASK:
        NONE = 0
        VEHICLE = 1
        CLAN = 16
        REGION = 256
        VEH_CLAN = VEHICLE | CLAN
        VEH_REGION = VEHICLE | REGION
        REG_CLAN = CLAN | REGION
        ALL = VEHICLE | CLAN | REGION

    __playerFullNameFormats = {FORMAT_MASK.VEHICLE: '{0:>s} ({2:>s})',
     FORMAT_MASK.CLAN: '{0:>s}[{1:>s}]',
     FORMAT_MASK.VEH_CLAN: '{0:>s}[{1:>s}] ({2:>s})',
     FORMAT_MASK.REGION: '{0:>s} {3:>s}',
     FORMAT_MASK.VEH_REGION: '{0:>s} {3:>s} ({2:>s})',
     FORMAT_MASK.REG_CLAN: '{0:>s}[{1:>s}] {3:>s}',
     FORMAT_MASK.ALL: '{0:>s}[{1:>s}] {3:>s} ({2:>s})'}
    __normalizePName = staticmethod(defNormalizePNameFunction)

    def setNormalizePlayerName(self, function):
        BattleContext.__normalizePName = staticmethod(function)

    def resetNormalizePlayerName(self):
        BattleContext.__normalizePName = staticmethod(defNormalizePNameFunction)

    def __init__(self):
        super(BattleContext, self).__init__()
        self.__arenaDP = None
        self.__isShowVehShortName = True
        self.lastArenaUniqueID = None
        self.isInBattle = False
        self.wasInBattle = False
        return

    def start(self, arenaDP):
        prefs = Settings.g_instance.userPrefs
        if prefs is not None:
            self.__isShowVehShortName = prefs.readBool('showVehShortName', True)
        self.__arenaDP = arenaDP
        self.isInBattle = self.wasInBattle = True
        return

    def stop(self):
        self.isInBattle = False
        self.__arenaDP = None
        return

    def getArenaDP(self):
        return self.__arenaDP

    def getVehIDByAccDBID(self, accDBID):
        return self.__arenaDP.getVehIDByAccDBID(accDBID)

    def getFullPlayerNameWithParts(self, vID = None, accID = None, pName = None, showVehShortName = True, showClan = True, showRegion = True):
        FM = self.FORMAT_MASK
        key = FM.NONE
        vehShortName = ''
        vehName = ''
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        vInfo = self.__arenaDP.getVehicleInfo(vID)
        if accID is None:
            accID = vInfo.player.accountDBID
        vehType = vInfo.vehicleType
        if vehType is not None:
            if showVehShortName and self.__isShowVehShortName:
                vehName = vehShortName = vehType.shortName
                key |= FM.VEHICLE
            else:
                vehName = vehType.name
        if pName is None:
            pName = vInfo.player.name
        pName = self.__normalizePName(pName)
        clanAbbrev = ''
        if showClan:
            clanAbbrev = vInfo.player.clanAbbrev
            if clanAbbrev is not None and len(clanAbbrev) > 0:
                key |= FM.CLAN
        regionCode = ''
        if showRegion:
            regionCode = self.getRegionCode(accID)
            if regionCode:
                key |= FM.REGION
        if key == FM.NONE:
            fullName = pName
        else:
            fullName = self.__playerFullNameFormats.get(key, '{0:>s}').format(pName, clanAbbrev, vehShortName, regionCode)
        return (fullName,
         pName,
         clanAbbrev,
         regionCode,
         vehName)

    def getFullPlayerName(self, vID = None, accID = None, pName = None, showVehShortName = True, showClan = True, showRegion = True):
        return self.getFullPlayerNameWithParts(vID, accID, pName, showVehShortName, showClan, showRegion)[0]

    def getRegionCode(self, dbID):
        regionCode = None
        if dbID and not game_control.g_instance.roaming.isSameRealm(dbID):
            _, regionCode = game_control.g_instance.roaming.getPlayerHome(dbID)
        return regionCode

    def isSquadMan(self, vID = None, accID = None, prebattleID = None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return vID and self.__arenaDP.isSquadMan(vID, prebattleID)

    def isTeamKiller(self, vID = None, accID = None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return vID and self.__arenaDP.isTeamKiller(vID)

    def isObserver(self, vID):
        return self.__arenaDP.isObserver(vID)

    def isPlayerObserver(self):
        return self.isObserver(getattr(BigWorld.player(), 'playerVehicleID', -1))

    def isInTeam(self, vID = None, accID = None, enemy = False):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return self.__arenaDP.getVehicleInfo(vID).team == self.__arenaDP.getNumberOfTeam(enemy)

    def getPlayerEntityName(self, vID, team):
        if BigWorld.player().team == team:
            if self.isSquadMan(vID=vID):
                return PLAYER_ENTITY_NAME.squadman
            if self.isTeamKiller(vID=vID):
                return PLAYER_ENTITY_NAME.teamKiller
            return PLAYER_ENTITY_NAME.ally
        return PLAYER_ENTITY_NAME.enemy

    def getTeamName(self, myTeam, isAlliedTeam):
        teamName = '#menu:loading/team%s' % ('1' if isAlliedTeam else '2')
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena:
            extraData = arena.extraData or {}
            if isAlliedTeam:
                teamName = extraData.get('opponents', {}).get('%s' % myTeam, {}).get('name', teamName)
            else:
                teamName = extraData.get('opponents', {}).get('2' if myTeam == 1 else '1', {}).get('name', teamName)
        return teamName
