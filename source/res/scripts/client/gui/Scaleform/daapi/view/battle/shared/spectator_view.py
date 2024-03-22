# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/spectator_view.py
import logging
from enum import Enum
from collections import namedtuple
import BigWorld
import CommandMapping
from AvatarInputHandler.control_modes import DeathFreeCamMode
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.spectator_ctrl import ISpectatorViewListener
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.SpectatorViewMeta import SpectatorViewMeta
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_MovementKeyBindings = namedtuple('MovementKeyBindings', ('forward', 'left', 'backward', 'right'))

class SPECTATOR_VIEW_SOUND(object):
    SPEED_CHANGE = 'dc_fc_speed_change'
    FOLLOW_HINT = 'dc_fc_follow_hint'
    START_TO_FOLLOW_TANK = 'dc_fc_start_to_follow_tank'
    STOP_TO_FOLLOW_TANK = 'dc_fc_stop_to_follow_tank'


class SpectatorView(SpectatorViewMeta, ISpectatorViewListener, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    DELAY_HINT_MOVEMENT = 3
    DELAY_HINT_SPEED = 4
    __RETURN_TO_PREVIOUS_VEHICLE_HINT_DURATION = 10

    class HintModes(Enum):
        init = 0
        speed_idle = 1
        speed_loading = 2
        finished = 3

    def __init__(self):
        super(SpectatorView, self).__init__()
        self.__followHintSound = True
        self.__isInRespawn = False
        self.__hintMode = self.HintModes.init
        self.__timestamp = 0
        self.__timeCB = None
        self.__mode = -1
        self.__movementKeyBindings = _MovementKeyBindings('', '', '', '')
        return

    def updateSpeedLevel(self, newSpeedLevel):
        if self.__mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            if self.__hintMode == self.HintModes.speed_idle:
                self.__startSpeedHintTimeout()
            self.as_setSpeedS(newSpeedLevel)
            self.__playSound(SPECTATOR_VIEW_SOUND.SPEED_CHANGE)

    def hideReturnHintWrapper(self):
        self.as_showReturnHintS(False)

    def toggleFollowHint(self, toggle):
        self.__playFollowHintSound(toggle)
        self.as_focusOnVehicleS(toggle)

    def _populate(self):
        super(SpectatorView, self)._populate()
        self.__movementKeyBindings = self.__getMovementKeyBindings()
        self._addGameListeners()
        self.as_setFollowInfoTextS(backport.text(R.strings.death_cam.hints.follow_pt1()) + ' ' + backport.text(R.strings.death_cam.hints.follow_pt2()))
        self.__setHintStrings()
        self.toggleFollowHint(False)
        self.__updateKeyBindingSettings()
        if self.sessionProvider.isReplayPlaying:
            self.as_handleAsReplayS()

    def _dispose(self):
        self._removeGameListeners()
        self.__removeMovementListener()
        if self.__timeCB:
            BigWorld.cancelCallback(self.__timeCB)
            self.__timeCB = None
        super(SpectatorView, self)._dispose()
        return

    def _handleMovement(self):
        if self.__mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            self.delayCallback(self.DELAY_HINT_MOVEMENT, self.as_showMovementHintS, False)
            self.delayCallback(self.DELAY_HINT_SPEED, self.__showSpeedHeightHintWrapper, True)
            self.__removeMovementListener()

    def _handleVerticalMovement(self):
        if self.__mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            self.__startSpeedHintTimeout()
            self.__removeMovementListener()

    def _addGameListeners(self):
        specCtrl = self.sessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged += self.__onSpectatorModeChanged
            self.__onSpectatorModeChanged(specCtrl.spectatorViewMode)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibility
            self.__onRespawnVisibility(ctrl.isRespawnVisible())
        playerComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerComp is not None and hasattr(playerComp, 'onReinforcementTimerUpdated'):
            playerComp.onReinforcementTimerUpdated += self.__onReinforcementTimerUpdated
            self.__onReinforcementTimerUpdated(playerComp.reinforcementTimer)
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        return

    def _removeGameListeners(self):
        playerComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if hasattr(playerComp, 'onReinforcementTimerUpdated'):
            playerComp.onReinforcementTimerUpdated -= self.__onReinforcementTimerUpdated
        ctrl = self.sessionProvider.shared.spectator
        if ctrl is not None:
            ctrl.onSpectatorViewModeChanged -= self.__onSpectatorModeChanged
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibility
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        return

    def _updateVehicleInfo(self):
        if self.__isInRespawn:
            return
        self._deathAlreadySet = False

    def __startSpeedHintTimeout(self):
        self.__hintMode = self.HintModes.speed_loading
        self.delayCallback(self.DELAY_HINT_SPEED, self.__showSpeedHeightHintWrapper, False)

    def __showSpeedHeightHintWrapper(self, toShow):
        if self.__mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            self.as_showSpeedHeightHintS(toShow)
        if self.__hintMode == self.HintModes.init:
            self.__hintMode = self.HintModes.speed_idle
            specCtrl = self.sessionProvider.shared.spectator
            specCtrl.onFreeCameraVerticalMoved += self._handleVerticalMovement
        if self.__hintMode == self.HintModes.speed_loading:
            self.as_toggleHintS(self.__hintMode.value)
            self.__hintMode = self.HintModes.finished
            self.delayCallback(SpectatorView.__RETURN_TO_PREVIOUS_VEHICLE_HINT_DURATION, self.hideReturnHintWrapper)

    def __onSpectatorModeChanged(self, mode):
        if self.__mode == mode:
            return
        prevMode = self.__mode
        self.__mode = mode
        self.as_changeModeS(mode)
        self.toggleFollowHint(False)
        self.clearCallbacks()
        if mode == EPIC_CONSTS.SPECTATOR_MODE_FOLLOW:
            self.__removeMovementListener()
            if prevMode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
                self.__playSound(SPECTATOR_VIEW_SOUND.START_TO_FOLLOW_TANK)
            self.delayCallback(0.0, self.hideReturnHintWrapper)
            self.as_showMovementHintS(False)
            self.as_showSpeedHeightHintS(False)
            self.as_showSpeedHintS(False)
        elif mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            if not self.__showFreeCamHints():
                self.__hintMode = self.HintModes.finished
            specCtrl = self.sessionProvider.shared.spectator
            if self.__hintMode == self.HintModes.init:
                specCtrl.onFreeCameraMoved += self._handleMovement
                self.as_toggleHintS(self.__hintMode.value)
            elif self.__hintMode == self.HintModes.speed_idle:
                specCtrl.onFreeCameraVerticalMoved += self._handleVerticalMovement
            elif self.__hintMode == self.HintModes.speed_loading:
                self.as_toggleHintS(self.__hintMode.value)
                self.__hintMode = self.HintModes.finished
            else:
                self.as_toggleHintS(self.__hintMode.value)
                self.delayCallback(SpectatorView.__RETURN_TO_PREVIOUS_VEHICLE_HINT_DURATION, self.hideReturnHintWrapper)
            self.__playSound(SPECTATOR_VIEW_SOUND.STOP_TO_FOLLOW_TANK)

    @staticmethod
    def __showFreeCamHints():
        avatar = BigWorld.player()
        if not avatar:
            return False
        controlMode = avatar.inputHandler.ctrl
        return controlMode.showFreeCamHints() if isinstance(controlMode, DeathFreeCamMode) else False

    def __playFollowHintSound(self, toggle):
        if not toggle:
            self.__followHintSound = True
            return
        if toggle and self.__followHintSound:
            self.__followHintSound = False
            self.__playSound(SPECTATOR_VIEW_SOUND.FOLLOW_HINT)

    def __playSound(self, eventName):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __onRespawnVisibility(self, isVisible):
        self.__isInRespawn = isVisible
        if isVisible:
            self._deathAlreadySet = False

    def __onReinforcementTimerUpdated(self, time):
        self.__timestamp = time
        if time is None:
            if self.__timeCB:
                BigWorld.cancelCallback(self.__timeCB)
                self.__timeCB = None
        elif not self.__timeCB:
            self.__timeCB = BigWorld.callback(1, self.__tick)
        return

    def __tick(self):
        diffTime = self.__timestamp - BigWorld.serverTime()
        if diffTime <= 0:
            self.__timeCB = None
            self.as_setTimerS('0:00')
        else:
            timeStr = time_utils.getTimeLeftFormat(diffTime)
            self.as_setTimerS(timeStr)
            if self.__timeCB is not None:
                self.__timeCB = BigWorld.callback(1, self.__tick)
        return

    def __removeMovementListener(self):
        specCtrl = self.sessionProvider.shared.spectator
        if specCtrl:
            specCtrl.onFreeCameraMoved -= self._handleMovement
            specCtrl.onFreeCameraVerticalMoved -= self._handleVerticalMovement

    @staticmethod
    def __getMovementKeyBindings():
        forwardKey, _ = CommandMapping.g_instance.getCommandKeys(CommandMapping.CMD_MOVE_FORWARD)
        backwardKey, _ = CommandMapping.g_instance.getCommandKeys(CommandMapping.CMD_MOVE_BACKWARD)
        leftKey, _ = CommandMapping.g_instance.getCommandKeys(CommandMapping.CMD_ROTATE_LEFT)
        rightKey, _ = CommandMapping.g_instance.getCommandKeys(CommandMapping.CMD_ROTATE_RIGHT)
        left = BigWorld.keyToString(leftKey)
        right = BigWorld.keyToString(rightKey)
        forward = BigWorld.keyToString(forwardKey)
        backward = BigWorld.keyToString(backwardKey)
        return _MovementKeyBindings(forward, left, backward, right)

    def __updateKeyBindingSettings(self):
        self.as_updateMovementHintControlsS(self.__movementKeyBindings.forward, self.__movementKeyBindings.left, self.__movementKeyBindings.backward, self.__movementKeyBindings.right)

    def __setHintStrings(self):
        self.as_setHintStringsS(movementHeadline=backport.text(R.strings.death_cam.hints.movement.label()), movementDescription=backport.text(R.strings.death_cam.hints.movement.text(), forward=self.__movementKeyBindings.forward, left=self.__movementKeyBindings.left, backward=self.__movementKeyBindings.backward, right=self.__movementKeyBindings.right), speedHeadline=backport.text(R.strings.death_cam.hints.speed.label()), speedDescription=backport.text(R.strings.death_cam.hints.speed.text()), heightHeadline=backport.text(R.strings.death_cam.hints.height.label()), heightDescription=backport.text(R.strings.death_cam.hints.height.text()), spectatorUpBtnText=backport.text(R.strings.death_cam.hints.spectatorUp()), spectatorDownBtnText=backport.text(R.strings.death_cam.hints.spectatorDown()))

    def __onMappingChanged(self, *args):
        self.__movementKeyBindings = self.__getMovementKeyBindings()
        self.__updateKeyBindingSettings()
        self.__setHintStrings()
