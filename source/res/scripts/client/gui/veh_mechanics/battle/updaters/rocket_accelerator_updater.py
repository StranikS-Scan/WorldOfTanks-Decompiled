# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/rocket_accelerator_updater.py
import BigWorld
from constants import ROCKET_ACCELERATION_STATE
from events_handler import eventHandler
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.shared.utils.TimeInterval import TimeInterval
from gui.veh_mechanics.battle.updaters.updaters_common import VehicleMechanicUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
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

    def setState(self, state):
        raise NotImplementedError


class RocketAcceleratorUpdater(VehicleMechanicUpdater):

    def __init__(self, view):
        super(RocketAcceleratorUpdater, self).__init__(VehicleMechanic.ROCKET_ACCELERATION, view)
        self.__timeInterval = TimeInterval(0.1, self, '_updateProgress')

    @eventHandler
    def onComponentDestroyed(self):
        self.__timeInterval.stop()
        super(RocketAcceleratorUpdater, self).onComponentDestroyed()

    def finalize(self):
        super(RocketAcceleratorUpdater, self).finalize()
        self.__timeInterval.stop()
        self.__timeInterval = None
        return

    def _subscribeToMechanicComponent(self, mechanicComponent):
        super(RocketAcceleratorUpdater, self)._subscribeToMechanicComponent(mechanicComponent)
        mechanicComponent.subscribe(self.__onRocketAcceleratorStateChanged)
        self.__timeInterval.start()

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        self.__timeInterval.stop()
        mechanicComponent.unsubscribe(self.__onRocketAcceleratorStateChanged)
        super(RocketAcceleratorUpdater, self)._unsubscribeFromMechanicComponent(mechanicComponent)

    def _updateProgress(self):
        stateStatus = self.mechanicComponent.stateStatus
        status = stateStatus.status
        leftTime = max(0, stateStatus.endTime - BigWorld.serverTime())
        progress = 1.0 if status == ROCKET_ACCELERATION_STATE.READY else 0.0
        duration = stateStatus.timeLeft
        if duration:
            if status == ROCKET_ACCELERATION_STATE.ACTIVE:
                progress = leftTime / duration
                self.view.as_setTimeS(leftTime)
            else:
                progress = 1.0 - leftTime / duration
        self.view.as_setProgressS(progress)

    def __onRocketAcceleratorStateChanged(self, stateStatus, isInitial=False):
        self.view.as_setStateS(UI_ROCKET_STATE_MAP[stateStatus.status], isInitial)
        self.view.as_setCountS(stateStatus.reuseCount)
        self._updateProgress()
