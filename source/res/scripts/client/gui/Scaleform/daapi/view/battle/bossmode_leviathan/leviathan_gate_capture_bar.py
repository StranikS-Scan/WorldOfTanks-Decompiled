# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/leviathan_gate_capture_bar.py
import BigWorld
import SoundGroups
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG_DEV
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from gui.Scaleform.daapi.view.meta.LeviathanGateCaptureBarMeta import LeviathanGateCaptureBarMeta
from PlayerEvents import g_playerEvents
_LEVIATHAN_CAPTURED_SOUND = 'ev_halloween_leviathan_enters_portal'
_LEVIATHAN_CAP_WARNING = 'ev_halloween_ui_leviathan_enters_gate'

class LeviathanGateCaptureBar(LeviathanGateCaptureBarMeta):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LeviathanGateCaptureBar, self).__init__()
        self.__captureWarningPlayed = 0
        self.__leviathanMaxHealth = 0
        self.__leviathanCurrHealth = 0
        self.__leviathanID = None
        self.__vehicle = None
        self.__isShowing = False
        return

    def _dispose(self):
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        BigWorld.player().onLeviathanProgressUpdate -= self.__arena_onLeviathanHealthAndProgressUpdated
        BigWorld.player().arena.onTeamBasePointsUpdate -= self.__arena_onTeamBasePointsUpdated
        self.__settingsCore.onSettingsChanged -= self.__arena_onSettingsStatusChanged
        super(LeviathanGateCaptureBar, self)._dispose()

    def _populate(self):
        super(LeviathanGateCaptureBar, self)._populate()
        self.__invalidateVehiclesInfo(self.__sessionProvider.getArenaDP())
        self.__arena_initializeLeviathanCaptureBar()
        self.__settingsCore.onSettingsChanged += self.__arena_onSettingsStatusChanged
        BigWorld.player().arena.onTeamBasePointsUpdate += self.__arena_onTeamBasePointsUpdated
        BigWorld.player().onLeviathanProgressUpdate += self.__arena_onLeviathanHealthAndProgressUpdated
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def __arena_initializeLeviathanCaptureBar(self):
        isColorBlind = self.__settingsCore.getSetting(GRAPHICS.COLOR_BLIND)
        self.as_isColorBlindS(isColorBlind)
        self.as_setCommentS(INGAME_GUI.HALLOWEEN_PVE_GATE_CAPTURE_LEVIATHANCAPTUREMSG)

    def __invalidateVehiclesInfo(self, arenaDP):
        for vInfo in arenaDP.getVehiclesInfoIterator():
            vTypeInfoVO = vInfo.vehicleType
            if vTypeInfoVO.isLeviathan:
                self.__leviathanMaxHealth = vTypeInfoVO.maxHealth
                self.__leviathanID = vInfo.vehicleID
                self.__vehicle = BigWorld.entities.get(self.__leviathanID)
                if self.__vehicle is not None:
                    self.__leviathanCurrHealth = self.__vehicle.health
                    self.__initLeviathanInitialHealthValues(self.__leviathanMaxHealth, self.__vehicle.health)
                else:
                    self.__leviathanCurrHealth = self.__leviathanMaxHealth
                    self.__initLeviathanInitialHealthValues(self.__leviathanMaxHealth, self.__leviathanMaxHealth)
                break

        return

    def __initLeviathanInitialHealthValues(self, maxHealth, currHealth):
        if currHealth < 0:
            currHealth = 0
        self.as_setLeviathanHealthS(maxHealth, currHealth)

    def __arena_onLeviathanHealthAndProgressUpdated(self, health, progress):
        if self.__leviathanID is not None:
            self.__leviathanCurrHealth = health
            if self.__leviathanCurrHealth < 0:
                self.__leviathanCurrHealth = 0
            self.as_updateHealthS(self.__leviathanCurrHealth)
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
        if not self.__isShowing and timeLeft > 0:
            self.__isShowing = True
            self.as_showS()
        if points > 0:
            if self.__captureWarningPlayed <= 0:
                SoundGroups.g_instance.playSound2D(_LEVIATHAN_CAP_WARNING)
                self.__captureWarningPlayed = 1
            if self.__captureWarningPlayed == 1 and points >= 100:
                SoundGroups.g_instance.playSound2D(_LEVIATHAN_CAPTURED_SOUND)
                self.__captureWarningPlayed = 2
        if timeLeft < 10:
            msg = '00:0' + str(timeLeft)
        else:
            msg = '00:' + str(timeLeft)
        self.as_updateTimeDisplayS(msg)

    def __onRoundFinished(self, winningTeam, reason):
        self.as_hideS()
