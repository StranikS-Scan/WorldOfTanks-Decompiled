# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/leviathan_progress_panel.py
import BigWorld
import SoundGroups
from skeletons.gui.battle_session import IBattleSessionProvider
from account_helpers.settings_core.settings_constants import GRAPHICS
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency
from gui.Scaleform.daapi.view.meta.LeviathanProgressPanelMeta import LeviathanProgressPanelMeta
_UPDATE_INTERVAL = 3

class LeviathanProgressPanel(LeviathanProgressPanelMeta):
    """
    Initialize the PvE Leviathan Progress bar with the inital current Health and the max Health of Leviathan.
    Then update the progress bar as Leviathan's health goes down from being attacked by players.
    Also keep updating the Leviathan's progress, as it heads towards its goal
    """
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(LeviathanProgressPanel, self).__init__()
        self.__isInitialized = False
        self.__leviathanMaxHealth = 0
        self.__leviathanCurrHealth = 0
        self.__leviathanID = None
        self.__vehicle = None
        self.__timerCallbackID = None
        self.__goneAway = False
        return

    def _dispose(self):
        self.settingsCore.onSettingsChanged -= self.__arena_onSettingsStatusChanged
        BigWorld.player().arena.onTeamBasePointsUpdate -= self.__arena_onTeamBasePointsUpdated
        BigWorld.player().onLeviathanProgressUpdate -= self.__arena_onLeviathanHealthAndProgressUpdated
        super(LeviathanProgressPanel, self)._dispose()

    def _populate(self):
        super(LeviathanProgressPanel, self)._populate()
        self.invalidateArenaInfo()
        BigWorld.player().onLeviathanProgressUpdate += self.__arena_onLeviathanHealthAndProgressUpdated
        BigWorld.player().arena.onTeamBasePointsUpdate += self.__arena_onTeamBasePointsUpdated
        self.__arena_initializeLeviathanProgressPanel()
        self.settingsCore.onSettingsChanged += self.__arena_onSettingsStatusChanged

    def __arena_initializeLeviathanProgressPanel(self):
        isColorBlind = self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND)
        self.as_isColorBlindS(isColorBlind)

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        if not self.__isInitialized:
            for vInfo in arenaDP.getVehiclesInfoIterator():
                vTypeInfoVO = vInfo.vehicleType
                if vTypeInfoVO.isLeviathan:
                    self.__isInitialized = True
                    self.__leviathanMaxHealth = vTypeInfoVO.maxHealth
                    self.__leviathanID = vInfo.vehicleID
                    self.__vehicle = BigWorld.entities.get(self.__leviathanID)
                    if self.__vehicle is not None:
                        self.__leviathanCurrHealth = self.__vehicle.health
                        self.initLeviathanInitialHealthValues(self.__leviathanMaxHealth, self.__vehicle.health)
                    else:
                        self.__leviathanCurrHealth = self.__leviathanMaxHealth
                        self.initLeviathanInitialHealthValues(self.__leviathanMaxHealth, self.__leviathanMaxHealth)
                    break

        return

    def initLeviathanInitialHealthValues(self, maxHealth, currHealth):
        if currHealth < 0:
            currHealth = 0
        self.as_setLeviathanHealthS(currHealth, maxHealth)

    def __arena_onLeviathanHealthAndProgressUpdated(self, health, progress):
        self.as_updateLeviathanProgressS(progress)
        if self.__leviathanID is not None:
            self.__leviathanCurrHealth = health
            if self.__leviathanCurrHealth < 0:
                self.__leviathanCurrHealth = 0
            self.as_updateLeviathanHealthS(self.__leviathanCurrHealth)
        return

    def __arena_onSettingsStatusChanged(self, diff):
        """
        Callback to handle change of user preferences.
        :param diff: dict of changed settings
        """
        if GRAPHICS.COLOR_BLIND in diff:
            val = bool(diff[GRAPHICS.COLOR_BLIND])
            self.as_isColorBlindS(val)

    def __arena_onTeamBasePointsUpdated(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        if not self.__goneAway and timeLeft > 0:
            self.__goneAway = True
            self.as_hideS()
