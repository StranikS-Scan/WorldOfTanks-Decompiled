# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/recovery_panel.py
from functools import partial
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.Scaleform.daapi.view.meta.RecoveryPanelMeta import RecoveryPanelMeta
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
import BigWorld
import CommandMapping
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.shared.utils.key_mapping import getReadableKey
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import time_utils, i18n
from constants import RM_STATE
from gui.sounds.epic_sound_constants import EPIC_SOUND
from gui.battle_control import avatar_getter
from PlayerEvents import g_playerEvents
_SHOW_HINT_TIME = 5
_SHOW_COOLDOWN_TIME = 5

class _CALLBACK_HIDE(object):
    ALL = 0
    HINT = 1
    COOLDOWN = 2


class RecoveryPanel(RecoveryPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RecoveryPanel, self).__init__()
        self.__hideHintCB = None
        self.__hideCooldownCB = None
        self.__cooldownTimerCallback = None
        self.__nextActionTime = -1
        self.__recoveryActivated = False
        self.__state = -1
        return

    def _populate(self):
        super(RecoveryPanel, self)._populate()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        self.as_setupTextsS(i18n.makeString(INGAME_GUI.RECOVERY_HINT1), i18n.makeString(INGAME_GUI.RECOVERY_HINT2), getReadableKey(CommandMapping.CMD_REQUEST_RECOVERY))
        if avatar_getter.getLastRecoveryArgs() is not None:
            activated, state, timerDuration, endOfTimer = avatar_getter.getLastRecoveryArgs()
            if state > RM_STATE.NOT_RECOVERING:
                self.__onVehicleFeedbackReceived(_EVENT_ID.VEHICLE_RECOVERY_STATE_UPDATE, avatar_getter.getPlayerVehicleID(), (activated,
                 state,
                 timerDuration,
                 endOfTimer))
        return

    def _dispose(self):
        super(RecoveryPanel, self)._dispose()
        self.__nextActionTime = -1
        self.__cancelHideCallback(_CALLBACK_HIDE.ALL)
        if self.__cooldownTimerCallback:
            BigWorld.cancelCallback(self.__cooldownTimerCallback)
            self.__cooldownTimerCallback = None
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        return

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == _EVENT_ID.VEHICLE_RECOVERY_CANCELED:
            self.as_displayCooldownS(False, True)
            self.__cancelHideCallback(_CALLBACK_HIDE.COOLDOWN)
            self.as_displayHintS(True, True)
            self.__cancelHideCallback(_CALLBACK_HIDE.HINT)
            self.__hideHintCB = BigWorld.callback(_SHOW_HINT_TIME, self.__hideHint)
            if avatar_getter.isVehicleAlive:
                self.__playSound(EPIC_SOUND.BF_EB_RECOVERY_CANCELED)
        elif eventID == _EVENT_ID.VEHICLE_RECOVERY_STATE_UPDATE:
            activated, state, _, endOfTimer = value
            self.__nextActionTime = endOfTimer
            self.__recoveryActivated = activated
            if not activated:
                return
            if state == RM_STATE.RECOVERING:
                self.__playSound(EPIC_SOUND.BF_EB_RECOVERY_REQUESTED)
                self.as_displayCooldownS(False, False)
                self.as_displayHintS(False, False)
            elif state in {RM_STATE.TEMPORARILY_BLOCKED_FROM_RECOVERING, RM_STATE.TEMPORARILY_BLOCKED_RECOVER_TRY}:
                if state == RM_STATE.TEMPORARILY_BLOCKED_FROM_RECOVERING and self.__state in (RM_STATE.TEMPORARILY_BLOCKED_RECOVER_TRY, RM_STATE.TEMPORARILY_BLOCKED_FROM_RECOVERING, RM_STATE.NOT_RECOVERING):
                    pass
                else:
                    self.as_displayCooldownS(True, True)
                    self.as_displayHintS(False, True)
                    self.__cancelHideCallback(_CALLBACK_HIDE.ALL)
                    self.__hideCooldownCB = BigWorld.callback(_SHOW_COOLDOWN_TIME, partial(self.__hideCooldown, True))
                    if not self.__cooldownTimerCallback:
                        self.__tick()
            self.__state = state

    def __hideHint(self):
        self.as_displayHintS(False, True)
        self.__hideHintCB = None
        return

    def __hideCooldown(self, animate):
        self.as_displayCooldownS(False, animate)
        self.__hideCooldownCB = None
        if self.__cooldownTimerCallback:
            BigWorld.cancelCallback(self.__cooldownTimerCallback)
            self.__cooldownTimerCallback = None
        return

    def __onMappingChanged(self, *args):
        self.as_updateTextsS(getReadableKey(CommandMapping.CMD_REQUEST_RECOVERY))

    def __tick(self):
        if self.__nextActionTime > 0 and self.__recoveryActivated:
            diffTime = self.__nextActionTime - BigWorld.serverTime()
            timerText = time_utils.getTimeLeftFormat(diffTime)
            if diffTime > 0:
                self.__cooldownTimerCallback = BigWorld.callback(1, self.__tick)
                self.as_updateTimerS(i18n.makeString(INGAME_GUI.RECOVERY_COOLDOWN, cooldown=timerText))
            else:
                self.__nextActionTime = -1
                self.as_updateTimerS(i18n.makeString(INGAME_GUI.RECOVERY_COOLDOWN, cooldown=timerText))
                self.__cooldownTimerCallback = None
                self.__cancelHideCallback(_CALLBACK_HIDE.COOLDOWN)
                self.as_displayCooldownS(False, False)
        elif self.__cooldownTimerCallback:
            BigWorld.cancelCallback(self.__cooldownTimerCallback)
            self.__cooldownTimerCallback = None
        return

    def __cancelHideCallback(self, mode):
        if mode in {_CALLBACK_HIDE.ALL, _CALLBACK_HIDE.HINT}:
            if self.__hideHintCB:
                BigWorld.cancelCallback(self.__hideHintCB)
                self.__hideHintCB = None
        if mode in {_CALLBACK_HIDE.ALL, _CALLBACK_HIDE.COOLDOWN}:
            if self.__hideCooldownCB:
                BigWorld.cancelCallback(self.__hideCooldownCB)
                self.__hideCooldownCB = None
        return

    def __playSound(self, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __onRoundFinished(self, winnerTeam, reason):
        self.__hideCooldown(False)
        self.__hideHint()
