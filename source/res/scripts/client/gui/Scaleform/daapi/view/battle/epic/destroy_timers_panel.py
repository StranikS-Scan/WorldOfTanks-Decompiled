# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/destroy_timers_panel.py
from functools import partial
import BigWorld
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME
from constants import DEATH_ZONES
from gui.Scaleform.daapi.view.battle.shared import destroy_times_mapping as _mapping
from gui.Scaleform.daapi.view.meta.EpicDestroyTimersPanelMeta import EpicDestroyTimersPanelMeta
from gui.Scaleform.genConsts.BATTLE_DESTROY_TIMER_STATES import BATTLE_DESTROY_TIMER_STATES
from gui.battle_control import avatar_getter
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.controllers.progress_circle_ctrl import PROGRESS_CIRCLE_TYPE
from helpers import dependency, time_utils
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.sounds.epic_sound_constants import EPIC_SOUND
from PlayerEvents import g_playerEvents
_WARNING_TEXT_TIMER = 3
_LEAVE_ZONE_DEFENDER_DELAY = 10

class EpicDestroyTimersPanel(EpicDestroyTimersPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        deathZonesCodes = _mapping.getDefaultDeathZonesCodes()
        deathZonesCodes[DEATH_ZONES.SECTOR_AIRSTRIKE] = BATTLE_DESTROY_TIMER_STATES.SECTOR_AIRSTRIKE
        deathZonesSoundIDs = {}
        super(EpicDestroyTimersPanel, self).__init__(mapping=_mapping.FrontendMapping(deathZonesCodes=deathZonesCodes, deathZonesSoundIDs=deathZonesSoundIDs))
        self.__underFireCount = 0
        self.__delayedCB = None
        self.__inCircleIdx = -1
        self.__inCircleType = -1
        return

    def _populate(self):
        super(EpicDestroyTimersPanel, self)._populate()
        ctrl = self.sessionProvider.dynamic.progressTimer
        if not ctrl:
            return
        ctrl.onTimerUpdated += self.__onTimerUpdated
        ctrl.onVehicleEntered += self.__onVehicleEntered
        ctrl.onVehicleLeft += self.__onVehicleLeft
        ctrl.onCircleStatusChanged += self.__onCircleStatusChanged
        ctrl.onProgressUpdate += self.__onProgressUpdate
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def _dispose(self):
        ctrl = self.sessionProvider.dynamic.progressTimer
        if not ctrl:
            return
        ctrl.onTimerUpdated -= self.__onTimerUpdated
        ctrl.onVehicleEntered -= self.__onVehicleEntered
        ctrl.onVehicleLeft -= self.__onVehicleLeft
        ctrl.onCircleStatusChanged -= self.__onCircleStatusChanged
        ctrl.onProgressUpdate -= self.__onProgressUpdate
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        super(EpicDestroyTimersPanel, self)._dispose()

    def _showDeathZoneTimer(self, value):
        if BigWorld.player().team == EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER and not value[4] and avatar_getter.getInputHandler().ctrlModeName != CTRL_MODE_NAME.POSTMORTEM:
            if self.__delayedCB is not None:
                BigWorld.cancelCallback(self.__delayedCB)
            self.__delayedCB = BigWorld.callback(_LEAVE_ZONE_DEFENDER_DELAY, partial(self.__displayDeathZoneTimer, value[0:4]))
        else:
            self.__displayDeathZoneTimer(value[0:4])
        return

    def _hideDeathZoneTimer(self, value):
        if self.__delayedCB is not None:
            BigWorld.cancelCallback(self.__delayedCB)
            self.__delayedCB = None
        else:
            super(EpicDestroyTimersPanel, self)._hideDeathZoneTimer(value)
        return

    def _onVehicleStateUpdated(self, state, value):
        super(EpicDestroyTimersPanel, self)._onVehicleStateUpdated(state, value)
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            if self.__underFireCount > 0:
                self.__underFireCount = 0
                self._hideTimer(BATTLE_DESTROY_TIMER_STATES.UNDER_FIRE)
        if state == VEHICLE_VIEW_STATE.UNDER_FIRE:
            self.__setUnderFire(value)
        if state == VEHICLE_VIEW_STATE.RECOVERY:
            self.__setRecoveryActive(value)

    def __displayDeathZoneTimer(self, value):
        super(EpicDestroyTimersPanel, self)._showDeathZoneTimer(value)
        self.__playSound(EPIC_SOUND.BF_EB_ENTER_CLOSED_ZONE)
        self.__delayedCB = None
        return

    def __setUnderFire(self, isUnderFire):
        if isUnderFire:
            self.__underFireCount += 1
        elif self.__underFireCount > 0:
            self.__underFireCount -= 1
        if self.__underFireCount == 1:
            self._showTimer(BATTLE_DESTROY_TIMER_STATES.UNDER_FIRE, 0, 'warning', BigWorld.serverTime())
            self.__playSound(EPIC_SOUND.BF_EB_ENTER_PROTECTION_ZONE)
        elif self.__underFireCount == 0:
            self._hideTimer(BATTLE_DESTROY_TIMER_STATES.UNDER_FIRE)

    def __setRecoveryActive(self, values):
        isActivated, duration, endOfTimer = values
        if isActivated and avatar_getter.getInputHandler().ctrlModeName not in (CTRL_MODE_NAME.POSTMORTEM, CTRL_MODE_NAME.DEATH_FREE_CAM):
            self._showTimer(BATTLE_DESTROY_TIMER_STATES.RECOVERY, duration, 'critical', endOfTimer)
        else:
            self._hideTimer(BATTLE_DESTROY_TIMER_STATES.RECOVERY)

    def __playSound(self, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __isPresentCircle(self, circleType, idx):
        return circleType == self.__inCircleType and idx == self.__inCircleIdx and circleType != PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE

    def __onTimerUpdated(self, circleType, idx, timeLeft):
        if not self.__isPresentCircle(circleType, idx):
            return
        self.as_setAdditionalTimerTimeStringS(circleType, time_utils.getTimeLeftFormat(timeLeft))

    def __onVehicleEntered(self, circleType, idx, state):
        self.__inCircleIdx = idx
        self.__inCircleType = circleType
        self.as_showAdditionalTimerS(circleType, state)

    def __onVehicleLeft(self, circleType, idx):
        if not self.__isPresentCircle(circleType, idx):
            return
        self.as_hideAdditionalTimerS(circleType)
        self.__inCircleIdx = -1
        self.__inCircleType = -1

    def __onCircleStatusChanged(self, circleType, idx, state):
        if not self.__isPresentCircle(circleType, idx):
            return
        self.as_setAdditionalTimerStateS(circleType, state)

    def __onProgressUpdate(self, circleType, idx, value):
        if not self.__isPresentCircle(circleType, idx):
            return
        self.as_setAdditionalTimerProgressValueS(circleType, value)

    def __onRoundFinished(self, winnerTeam, reason):
        self._timers.removeTimers()
