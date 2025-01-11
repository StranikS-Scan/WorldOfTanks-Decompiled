# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/indicator_items/thermal_indicator_proxy.py
import typing
from WeakMethod import WeakMethodProxy
from cache import cached_property
from constants import THERMAL_VISION_STATE
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.battle.shared.indicator_items.thermal_vision import ThermalVisionIndicator
    from items.components.shared_components import ThermalVisionParams

class ThermalVisionIndicatorProxy(object):

    def __init__(self):
        super(ThermalVisionIndicatorProxy, self).__init__()
        self.__indicator = None
        return

    @cached_property
    def stateHandlers(self):
        return {THERMAL_VISION_STATE.IDLE: WeakMethodProxy(self.__onIdleReceived),
         THERMAL_VISION_STATE.ACTIVE: WeakMethodProxy(self.__onActiveReceived),
         THERMAL_VISION_STATE.RELOADING: WeakMethodProxy(self.__onReloadingReceived),
         THERMAL_VISION_STATE.DISABLED: WeakMethodProxy(self.__onDisabledReceived)}

    def setIndicator(self, indicator):
        self.__indicator = indicator

    def __onIdleReceived(self, stateStatus):
        self.__indicator.clearCallbacks()
        self.__indicator.as_setProgressS(1)
        self.__indicator.as_setActiveTimeS(0)
        self.__indicator.as_setCountS(stateStatus.useCount)

    def __onActiveReceived(self, stateStatus):
        self.__indicator.clearCallbacks()
        self.__indicator.startActiveAnimation(stateStatus.startTime, stateStatus.duration)

    def __onReloadingReceived(self, stateStatus):
        self.__indicator.clearCallbacks()
        self.__indicator.startReloadAnimation(stateStatus.startTime, stateStatus.reloadTime)

    def __onDisabledReceived(self, _):
        self.__indicator.clearCallbacks()
        self.__indicator.as_setProgressS(0)
        self.__indicator.as_setActiveTimeS(0)

    @noexcept
    def setState(self, stateStatus):
        if stateStatus is None or self.__indicator is None:
            return
        else:
            state = stateStatus.status
            handler = self.stateHandlers[state]
            self.__indicator.setState(state)
            self.__indicator.as_setCountS(stateStatus.useCount)
            handler(stateStatus)
            return

    def hide(self):
        if self.__indicator is None:
            return
        else:
            self.__indicator.hide()
            return

    def setBeforeBattleState(self, params):
        if self.__indicator is None:
            return
        else:
            self.__indicator.setState(THERMAL_VISION_STATE.RELOADING)
            self.__indicator.as_setProgressS(0)
            self.__indicator.as_setCountS(params.useCount)
            self.__indicator.as_setActiveTimeS(params.initialReloadTime)
            return
