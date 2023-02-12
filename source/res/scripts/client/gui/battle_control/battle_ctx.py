# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_ctx.py
import logging
import Settings
from gui.battle_control.arena_info import player_format
from gui.impl import backport
from gui.impl.gen import R
from unit_roster_config import SquadRoster, EpicRoster
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider, IBattleContext
_logger = logging.getLogger(__name__)

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

    def getVehIDBySessionID(self, avatarSessionID):
        return self.__arenaDP.getVehIDBySessionID(avatarSessionID)

    def getSessionIDByVehID(self, vehID):
        return self.__arenaDP.getSessionIDByVehID(vehID)

    def setPlayerFullNameFormatter(self, formatter):
        self.__playerFormatter = formatter

    def getVehicleInfo(self, vID=None, avatarSessionID=None):
        if vID is None:
            vID = self.getVehIDBySessionID(avatarSessionID)
        return self.__arenaDP.getVehicleInfo(vID)

    def getPlayerName(self, vID=None, avatarSessionID=None):
        return self.getVehicleInfo(vID, avatarSessionID).player.name

    def resetPlayerFullNameFormatter(self):
        self.__playerFormatter = player_format.PlayerFullNameFormatter()

    def createPlayerFullNameFormatter(self, showVehShortName=True, showClan=True, showRegion=True):
        return self.__playerFormatter.create(showVehShortName and self.__isShowVehShortName, showClan, showRegion)

    def getPlayerFullNameParts(self, vID=None, avatarSessionID=None, pName=None, showVehShortName=True, showClan=True, showRegion=True):
        if vID is None:
            vID = self.__arenaDP.getVehIDBySessionID(avatarSessionID)
        vInfo = self.__arenaDP.getVehicleInfo(vID)
        self.__playerFormatter.setVehicleShortNameShown(showVehShortName and self.__isShowVehShortName)
        self.__playerFormatter.setClanShown(showClan)
        self.__playerFormatter.setRegionShown(showRegion)
        return self.__playerFormatter.format(vInfo, playerName=pName)

    def getPlayerFullName(self, vID=None, avatarSessionID=None, pName=None, showVehShortName=True, showClan=True, showRegion=True):
        return self.getPlayerFullNameParts(vID, avatarSessionID, pName, showVehShortName, showClan, showRegion).playerFullName

    def isSquadMan(self, vID=None, avatarSessionID=None, prebattleID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDBySessionID(avatarSessionID)
        return vID and self.__arenaDP.isSquadMan(vID, prebattleID)

    def isGeneral(self, vID=None, avatarSessionID=None, prebattleID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDBySessionID(avatarSessionID)
        return self.__arenaDP.isGeneral(vID)

    def isTeamKiller(self, vID=None, avatarSessionID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDBySessionID(avatarSessionID)
        return vID and self.__arenaDP.isTeamKiller(vID)

    def isObserver(self, vID):
        if self.__arenaDP is not None:
            return self.__arenaDP.isObserver(vID)
        else:
            _logger.debug('BattleContext.isObserver: ArenaDP is None, vID = %s', vID)
            return

    def isPlayerObserver(self):
        if self.__arenaDP is not None:
            return self.__arenaDP.isPlayerObserver()
        else:
            _logger.debug('BattleContext.isPlayerObserver: ArenaDP is None')
            return

    def isInTeam(self, teamIdx, vID=None, avatarSessionID=None):
        return self._isInTeams([teamIdx], vID, avatarSessionID)

    def isAlly(self, vID=None, avatarSessionID=None):
        return self._isInTeams(self.__arenaDP.getAllyTeams(), vID, avatarSessionID)

    def isEnemy(self, vID=None, avatarSessionID=None):
        return self._isInTeams(self.__arenaDP.getEnemyTeams(), vID, avatarSessionID)

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
        iconRes = R.images.gui.maps.icons.battleTypes.c_136x136.dyn(self.__arenaDP.getPersonalDescription().getFrameLabel())
        return backport.image(iconRes()) if iconRes.exists() else ''

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

    def _isInTeams(self, teams, vID=None, sessionID=None):
        if vID is None:
            vID = self.__arenaDP.getVehIDBySessionID(sessionID)
        return self.__arenaDP.getVehicleInfo(vID).team in teams
