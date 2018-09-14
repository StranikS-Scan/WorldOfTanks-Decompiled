# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_ctx.py
import BigWorld
import Settings
from gui.battle_control.arena_info import player_format
from unit_roster_config import SquadRoster

class BattleContext(object):

    def __init__(self):
        super(BattleContext, self).__init__()
        self.__arenaDP = None
        self.__isShowVehShortName = True
        self.__lastArenaWinStatus = None
        self.__playerFormatter = player_format.PlayerFullNameFormatter()
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

    def setPlayerFullNameFormatter(self, formatter):
        self.__playerFormatter = formatter

    def getVehicleInfo(self, vID=None, accID=None):
        """
        Gets vehicle info.
        
        :param vID: long containing vehicle's entity ID.
        :param accID: long containing account's database ID
        :return: an instance of VehicleArenaInfoVO.
        """
        if vID is None:
            vID = self.getVehIDByAccDBID(accID)
        return self.__arenaDP.getVehicleInfo(vID)

    def getPlayerName(self, vID=None, accID=None):
        """
        Gets player name by vehicle id or account id. If both are None, returns name of
        the current player.
        
        :param vID: long containing vehicle's entity ID.
        :param accID: long containing account's database ID
        :return: string.
        """
        return self.getVehicleInfo(vID, accID).player.name

    def resetPlayerFullNameFormatter(self):
        self.__playerFormatter = player_format.PlayerFullNameFormatter()

    def createPlayerFullNameFormatter(self, showVehShortName=True, showClan=True, showRegion=True):
        """
        Creates configured player's name formatter.
        :param showVehShortName: is vehicle's short name shown.
        :param showClan: is player's clan shown.
        :param showRegion: is player's region code shown.
        :return: instance of PlayerFullNameFormatter.
        """
        return self.__playerFormatter.create(showVehShortName and self.__isShowVehShortName, showClan, showRegion)

    def getPlayerFullNameParts(self, vID=None, accID=None, pName=None, showVehShortName=True, showClan=True, showRegion=True):
        """
        Gets player display name and all parts of this name. The full name of the player consists of:
            <player name>[<clanAbbrev>]* (<vehicle short name>)*
                clanAbbrev if vData['clanAbbrev'] isn't empty
                vehicle short name if given setting is enabled.
        :param vID: long containing vehicle's entity ID.
        :param accID: long containing account's database ID.
        :param pName: string containing player's name.
        :param showVehShortName: is vehicle's short name shown.
        :param showClan: is player's region code shown.
        :param showRegion: is player's region code shown.
        :return: namedtuple with formatted full name and all parts, composing it.
        """
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        vInfo = self.__arenaDP.getVehicleInfo(vID)
        self.__playerFormatter.setVehicleShortNameShown(showVehShortName and self.__isShowVehShortName)
        self.__playerFormatter.setClanShown(showClan)
        self.__playerFormatter.setRegionShown(showRegion)
        return self.__playerFormatter.format(vInfo, playerName=pName)

    def getPlayerFullName(self, vID=None, accID=None, pName=None, showVehShortName=True, showClan=True, showRegion=True):
        """
        Gets player display name. The full name of the player consists of:
            <player name>[<clanAbbrev>]* (<vehicle short name>)*
                clanAbbrev if vData['clanAbbrev'] isn't empty
                vehicle short name if given setting is enabled.
        :param vID: long containing vehicle's entity ID.
        :param accID: long containing account's database ID
        :param pName: string containing player's name.
        :param showVehShortName: is vehicle's short name shown.
        :param showClan: is player's region code shown.
        :param showRegion: is player's region code shown.
        :return: string containing player's full name.
        """
        return self.getPlayerFullNameParts(vID, accID, pName, showVehShortName, showClan, showRegion).playerFullName

    def isSquadMan(self, vID=None, accID=None, prebattleID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return vID and self.__arenaDP.isSquadMan(vID, prebattleID)

    def isTeamKiller(self, vID=None, accID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return vID and self.__arenaDP.isTeamKiller(vID)

    def isObserver(self, vID):
        return self.__arenaDP.isObserver(vID)

    def isPlayerObserver(self):
        return self.isObserver(getattr(BigWorld.player(), 'playerVehicleID', -1))

    def isInTeam(self, teamIdx, vID=None, accID=None):
        return self._isInTeams([teamIdx], vID, accID)

    def isAlly(self, vID=None, accID=None):
        return self._isInTeams(self.__arenaDP.getAllyTeams(), vID, accID)

    def isEnemy(self, vID=None, accID=None):
        return self._isInTeams(self.__arenaDP.getEnemyTeams(), vID, accID)

    def isCurrentPlayer(self, vID):
        return self.__arenaDP.getPlayerVehicleID() == vID

    def getPlayerGuiProps(self, vID, team):
        return self.__arenaDP.getPlayerGuiProps(vID, team)

    def getArenaTypeName(self, isInBattle=True):
        return self.__arenaDP.getPersonalDescription().getTypeName(isInBattle)

    def getArenaDescriptionString(self, isInBattle=True):
        return self.__arenaDP.getPersonalDescription().getDescriptionString(isInBattle)

    def getArenaWinString(self, isInBattle=True):
        return self.__arenaDP.getPersonalDescription().getWinString(isInBattle)

    def getArenaFrameLabel(self, isLegacy=False):
        if isLegacy:
            return self.__arenaDP.getPersonalDescription().getLegacyFrameLabel()
        else:
            return self.__arenaDP.getPersonalDescription().getFrameLabel()

    def getGuiEventType(self):
        return self.__arenaDP.getPersonalDescription().getGuiEventType()

    def isInvitationEnabled(self):
        return self.__arenaDP.getPersonalDescription().isInvitationEnabled()

    def hasSquadRestrictions(self):
        limit = False
        vInfo = self.__arenaDP.getVehicleInfo()
        if vInfo.isSquadMan():
            if vInfo.isSquadCreator():
                limit = self.__arenaDP.getVehiclesCountInPrebattle(vInfo.team, vInfo.prebattleID) >= SquadRoster.MAX_SLOTS
            else:
                limit = True
        return limit

    def getQuestInfo(self):
        return self.__arenaDP.getPersonalDescription().getQuestInfo()

    def getTeamName(self, enemy=False):
        return self.__arenaDP.getPersonalDescription().getTeamName(self.__arenaDP.getNumberOfTeam(enemy=enemy))

    def getArenaSmallIcon(self):
        return self.__arenaDP.getPersonalDescription().getSmallIcon()

    def getArenaScreenIcon(self):
        return self.__arenaDP.getPersonalDescription().getScreenIcon()

    def setLastArenaWinStatus(self, winStatus):
        self.__lastArenaWinStatus = winStatus

    def extractLastArenaWinStatus(self):
        value = self.__lastArenaWinStatus
        self.__lastArenaWinStatus = None
        return value

    def _isInTeams(self, teams, vID=None, accID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return self.__arenaDP.getVehicleInfo(vID).team in teams
