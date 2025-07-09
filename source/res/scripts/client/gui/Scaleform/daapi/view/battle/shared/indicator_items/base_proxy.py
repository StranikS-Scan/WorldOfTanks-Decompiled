# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/indicator_items/base_proxy.py
import typing
from gui.Scaleform.daapi.view.battle.shared.indicator_items.indicators_storage import g_indicatorsStorage
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.battle.shared.indicator_items.base import BaseIndicator

class BaseIndicatorProxy(object):
    __slots__ = ('_indicator', '__delayedStateStatus', '__stateHandlers')

    def __init__(self):
        super(BaseIndicatorProxy, self).__init__()
        self._indicator = g_indicatorsStorage.get(self.componentName)
        self.__delayedStateStatus = None
        self.__stateHandlers = self._stateHandlers
        return

    @property
    def componentName(self):
        raise NotImplementedError

    def onIndicatorLoaded(self, metaObject):
        self._indicator = metaObject
        if self.__delayedStateStatus is not None:
            self.setState(self.__delayedStateStatus)
            self.__delayedStateStatus = None
            return
        else:
            self._setBeforeBattleState()
            return

    def init(self):
        g_indicatorsStorage.onNewItem += self.__onNewItem

    def fini(self):
        g_indicatorsStorage.onNewItem -= self.__onNewItem
        self.hide()

    @noexcept
    def setState(self, stateStatus):
        if stateStatus is None:
            self._setBeforeBattleState()
            return
        elif self._indicator is None:
            self.__delayedStateStatus = stateStatus
            return
        else:
            state = stateStatus.status
            self._indicator.setState(state)
            self.__stateHandlers[state](stateStatus)
            return

    def hide(self):
        if self._indicator is None:
            return
        else:
            self._indicator.hide()
            return

    @property
    def _stateHandlers(self):
        raise NotImplementedError

    def _setBeforeBattleState(self):
        raise NotImplementedError

    def __onNewItem(self, name, metaObject):
        if name != self.componentName:
            return
        g_indicatorsStorage.onNewItem -= self.__onNewItem
        self.onIndicatorLoaded(metaObject)
