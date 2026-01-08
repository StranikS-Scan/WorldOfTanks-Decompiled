# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/rocket_accelerator_updater.py
from __future__ import absolute_import, division
import typing
import BigWorld
from constants import ROCKET_ACCELERATION_STATE
from events_handler import eventHandler
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.shared.utils.TimeInterval import TimeInterval
from gui.veh_mechanics.battle.updaters.mechanics.mechanics_common import VehicleMechanicUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
if typing.TYPE_CHECKING:
    from RocketAccelerationController import RocketAccelerationController
UI_ROCKET_STATE_MAP = {ROCKET_ACCELERATION_STATE.NOT_RUNNING: MECHANICS_WIDGET_CONST.IDLE,
 ROCKET_ACCELERATION_STATE.DEPLOYING: MECHANICS_WIDGET_CONST.PREPARING,
 ROCKET_ACCELERATION_STATE.PREPARING: MECHANICS_WIDGET_CONST.PREPARING,
 ROCKET_ACCELERATION_STATE.READY: MECHANICS_WIDGET_CONST.READY,
 ROCKET_ACCELERATION_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
 ROCKET_ACCELERATION_STATE.DISABLED: MECHANICS_WIDGET_CONST.DISABLE,
 ROCKET_ACCELERATION_STATE.EMPTY: MECHANICS_WIDGET_CONST.PREPARING}

class IRocketAcceleratorView(object):

    def setCount(self, count):
        raise NotImplementedError

    def setProgress(self, progress):
        raise NotImplementedError

    def setState(self, state, isInstantly=False):
        raise NotImplementedError

    def setTime(self, time):
        raise NotImplementedError


class RocketAcceleratorUpdater(VehicleMechanicUpdater):

    def __init__(self, view):
        super(RocketAcceleratorUpdater, self).__init__(VehicleMechanic.ROCKET_ACCELERATION, view)
        self.__timeInterval = TimeInterval(0.1, self, '_updateProgress')
        self.__rocketComponent = None
        return

    @eventHandler
    def onMechanicComponentCatching(self, component):
        self.__rocketComponent = component
        component.subscribe(self.__onRocketAcceleratorStateChanged)
        self.__timeInterval.start()

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        self.__timeInterval.stop()
        component.unsubscribe(self.__onRocketAcceleratorStateChanged)
        self.__rocketComponent = None
        return

    def finalize(self):
        self.__timeInterval.stop()
        super(RocketAcceleratorUpdater, self).finalize()

    def destroy(self):
        self.__timeInterval = self.__rocketComponent = None
        super(RocketAcceleratorUpdater, self).destroy()
        return

    def _updateProgress(self):
        stateStatus = self.__rocketComponent.stateStatus
        status = stateStatus.status
        progress = 1.0 if status == ROCKET_ACCELERATION_STATE.READY else 0.0
        duration = stateStatus.timeLeft
        if duration:
            leftTime = max(0.0, stateStatus.endTime - BigWorld.serverTime())
            if status == ROCKET_ACCELERATION_STATE.ACTIVE:
                progress = leftTime / duration
                self.view.setTime(leftTime)
            else:
                progress = 1.0 - leftTime / duration
        self.view.setProgress(progress)

    def __onRocketAcceleratorStateChanged(self, stateStatus, isInitial=False):
        self.view.setState(UI_ROCKET_STATE_MAP[stateStatus.status], isInitial)
        self.view.setCount(stateStatus.reuseCount)
        self._updateProgress()
