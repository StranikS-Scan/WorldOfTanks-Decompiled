# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/indicator_items/thermal_indicator_proxy.py
import typing
from WeakMethod import WeakMethodProxy
from constants import THERMAL_VISION_STATE
from gui.Scaleform.daapi.view.battle.shared.indicator_items.base_proxy import BaseIndicatorProxy
from gui.Scaleform.daapi.view.battle.shared.indicator_items.thermal_vision import ThermalVisionIndicator
if typing.TYPE_CHECKING:
    from items.components.shared_components import ThermalVisionParams

class ThermalVisionIndicatorProxy(BaseIndicatorProxy):

    def __init__(self):
        super(ThermalVisionIndicatorProxy, self).__init__()
        self.__params = None
        return

    def setParams(self, params):
        self.__params = params

    @property
    def _stateHandlers(self):
        return {THERMAL_VISION_STATE.IDLE: WeakMethodProxy(self.__onIdleReceived),
         THERMAL_VISION_STATE.ACTIVE: WeakMethodProxy(self.__onActiveReceived),
         THERMAL_VISION_STATE.RELOADING: WeakMethodProxy(self.__onReloadingReceived),
         THERMAL_VISION_STATE.DISABLED: WeakMethodProxy(self.__onDisabledReceived)}

    @property
    def componentName(self):
        return ThermalVisionIndicator.componentName()

    def setUseCount(self, count):
        self._indicator.as_setCountS(count)

    def setEntityInSector(self, state):
        if self._indicator is not None:
            self._indicator.as_setEnemyIndicatorS(state)
        return

    def _setBeforeBattleState(self):
        if self._indicator is None or self.__params is None:
            return
        else:
            self._indicator.setState(THERMAL_VISION_STATE.RELOADING)
            self._indicator.as_setProgressS(0)
            self._indicator.as_setCountS(self.__params.useCount)
            self._indicator.as_setActiveTimeS(self.__params.initialReloadTime)
            return

    def __onIdleReceived(self, stateStatus):
        self._indicator.clearCallbacks()
        self._indicator.as_setProgressS(1)
        self._indicator.as_setActiveTimeS(0)
        self._indicator.as_setCountS(stateStatus.useCount)
        self.setEntityInSector(False)

    def __onActiveReceived(self, stateStatus):
        self._indicator.clearCallbacks()
        self._indicator.startActiveAnimation(stateStatus.startTime, stateStatus.duration)
        self._indicator.as_setCountS(stateStatus.useCount)

    def __onReloadingReceived(self, stateStatus):
        self._indicator.clearCallbacks()
        self._indicator.startReloadAnimation(stateStatus.startTime, stateStatus.duration)
        self._indicator.as_setCountS(stateStatus.useCount)
        self.setEntityInSector(False)

    def __onDisabledReceived(self, _):
        self._indicator.clearCallbacks()
        self._indicator.as_setProgressS(0)
        self._indicator.as_setActiveTimeS(0)
        self._indicator.as_setCountS(0)
        self.setEntityInSector(False)
