# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_ctx.py
import Settings
from gui.battle_control.arena_info import player_format
from unit_roster_config import SquadRoster, EpicRoster
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider, IBattleContext

class BattleContext(IBattleContext):

    def __init__(self):
        super(BattleContext, self).__init__()
        self.__arenaDP = None
        self.__isShowVehShortName = True
        self.__lastArenaWinStatus = None
        self.__playerFormatter = player_format.PlayerFullNameFormatter()
        self.lastArenaUniqueID = None
        self.lastArenaBonusType = None
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
        if vID is None:
            vID = self.getVehIDByAccDBID(accID)
        return self.__arenaDP.getVehicleInfo(vID)

    def getPlayerName(self, vID=None, accID=None):
        return self.getVehicleInfo(vID, accID).player.name

    def resetPlayerFullNameFormatter(self):
        self.__playerFormatter = player_format.PlayerFullNameFormatter()

    def createPlayerFullNameFormatter(self, showVehShortName=True, showClan=True, showRegion=True):
        return self.__playerFormatter.create(showVehShortName and self.__isShowVehShortName, showClan, showRegion)

    def getPlayerFullNameParts(self, vID=None, accID=None, pName=None, showVehShortName=True, showClan=True, showRegion=True):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        vInfo = self.__arenaDP.getVehicleInfo(vID)
        self.__playerFormatter.setVehicleShortNameShown(showVehShortName and self.__isShowVehShortName)
        self.__playerFormatter.setClanShown(showClan)
        self.__playerFormatter.setRegionShown(showRegion)
        return self.__playerFormatter.format(vInfo, playerName=pName)

    def getPlayerFullName(self, vID=None, accID=None, pName=None, showVehShortName=True, showClan=True, showRegion=True):
        return self.getPlayerFullNameParts(vID, accID, pName, showVehShortName, showClan, showRegion).playerFullName

    def isSquadMan(self, vID=None, accID=None, prebattleID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return vID and self.__arenaDP.isSquadMan(vID, prebattleID)

    def isGeneral(self, vID=None, accID=None, prebattleID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return self.__arenaDP.isGeneral(vID)

    def isTeamKiller(self, vID=None, accID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return vID and self.__arenaDP.isTeamKiller(vID)

    def isObserver(self, vID):
        return self.__arenaDP.isObserver(vID) if self.__arenaDP is not None else False

    def isPlayerObserver(self):
        return self.__arenaDP.isPlayerObserver()

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

    def getArenaFrameLabel(self):
        return '../maps/icons/battleTypes/136x136/%s.png' % self.__arenaDP.getPersonalDescription().getFrameLabel()

    def getFrameLabel(self):
        return self.__arenaDP.getPersonalDescription().getFrameLabel()

    def getGuiEventType(self):
        return self.__arenaDP.getPersonalDescription().getGuiEventType()

    def areQuestsEnabledForArena(self):
        return self.__arenaDP.getPersonalDescription().isQuestEnabled()

    def isInvitationEnabled(self):
        return self.__arenaDP.getPersonalDescription().isInvitationEnabled()

    def hasSquadRestrictions(self):
        limit = False
        sessionProvider = dependency.instance(IBattleSessionProvider)
        arenaVisitor = sessionProvider.arenaVisitor
        isEpicBattle = arenaVisitor.gui.isEpicBattle()
        vInfo = self.__arenaDP.getVehicleInfo()
        maxSlots = SquadRoster.MAX_SLOTS if not isEpicBattle else EpicRoster.MAX_SLOTS
        if vInfo.isSquadMan():
            if vInfo.isSquadCreator():
                limit = self.__arenaDP.getVehiclesCountInPrebattle(vInfo.team, vInfo.prebattleID) >= maxSlots
            else:
                limit = True
        return limit

    def getSelectedQuestIDs(self):
        return self.__arenaDP.getPersonalDescription().getSelectedQuestIDs()

    def getSelectedQuestInfo(self):
        return self.__arenaDP.getPersonalDescription().getSelectedQuestInfo()

    def getTeamName(self, enemy=False):
        return self.__arenaDP.getPersonalDescription().getTeamName(self.__arenaDP.getNumberOfTeam(enemy=enemy))

    def getArenaSmallIcon(self):
        return self.__arenaDP.getPersonalDescription().getSmallIcon()

    def getArenaScreenIcon(self):
        return self.__arenaDP.getPersonalDescription().getScreenIcon()

    def getArenaRespawnIcon(self):
        return self.__arenaDP.getPersonalDescription().getRespawnIcon()

    def setLastArenaWinStatus(self, winStatus):
        self.__lastArenaWinStatus = winStatus

    def getLastArenaWinStatus(self):
        return self.__lastArenaWinStatus

    def extractLastArenaWinStatus(self):
        value = self.__lastArenaWinStatus
        self.__lastArenaWinStatus = None
        return value

    def _isInTeams(self, teams, vID=None, accID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDByAccDBID(accID)
        return self.__arenaDP.getVehicleInfo(vID).team in teams
