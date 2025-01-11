# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/indicator_items/thermal_vision.py
import BigWorld
from constants import THERMAL_VISION_STATE
from gui.Scaleform.daapi.view.battle.shared.indicator_items.base import BaseIndicator
from gui.Scaleform.genConsts.COMMON_INDICATOR_CONSTS import COMMON_INDICATOR_CONSTS
from helpers.CallbackDelayer import CallbackDelayer
_STATES_MAPPING = {THERMAL_VISION_STATE.IDLE: COMMON_INDICATOR_CONSTS.READY,
 THERMAL_VISION_STATE.ACTIVE: COMMON_INDICATOR_CONSTS.ACTIVE,
 THERMAL_VISION_STATE.RELOADING: COMMON_INDICATOR_CONSTS.PREPARING,
 THERMAL_VISION_STATE.DISABLED: COMMON_INDICATOR_CONSTS.DISABLE}
_PROGRESS_FORWARD = 0
_PROGRESS_BACKWARD = 1

class ThermalVisionIndicator(BaseIndicator, CallbackDelayer):

    def __init__(self):
        super(ThermalVisionIndicator, self).__init__('thermalVisionController')

    def setState(self, state):
        if state in _STATES_MAPPING:
            self.as_setStateS(_STATES_MAPPING[state])

    def isValidVehicle(self, vehicle):
        player = BigWorld.player()
        isAvatarVehicle = player and player.vehicle and player.playerVehicleID == player.vehicle.id
        return vehicle.isAlive() and vehicle.typeDescriptor.hasThermalVision and isAvatarVehicle

    def startReloadAnimation(self, startTime, duration):
        self.delayCallback(0, self.__indicatorTimerCallback, startTime, duration, _PROGRESS_FORWARD)

    def startActiveAnimation(self, startTime, duration):
        self.delayCallback(0, self.__indicatorTimerCallback, startTime, duration, _PROGRESS_BACKWARD)

    def hide(self):
        self._setVisible(False)
        self.clearCallbacks()

    def _dispose(self):
        self.clearCallbacks()
        super(ThermalVisionIndicator, self)._dispose()

    def __indicatorTimerCallback(self, startTime, duration, progressOffset=0):
        elapsedTime = BigWorld.serverTime() - startTime
        if elapsedTime > duration:
            self.as_setProgressS(1 - progressOffset)
            self.as_setActiveTimeS(0)
            return
        progress = abs(progressOffset - elapsedTime / duration)
        self.as_setProgressS(progress)
        self.as_setActiveTimeS(duration - elapsedTime)
