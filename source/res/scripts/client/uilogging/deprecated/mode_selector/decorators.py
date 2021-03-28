# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/deprecated/mode_selector/decorators.py
import logging
from functools import wraps
from uilogging.deprecated.base.loggers import isUILoggingEnabled
from uilogging.deprecated.mode_selector.constants import MS_LOG_ACTIONS
from uilogging.deprecated.mode_selector.loggers import ModeSelectorUILogger
import BigWorld
_logger = logging.getLogger(__name__)

def _loggingEnabled(self):
    return isinstance(self, ModeSelectorUILogger) and isUILoggingEnabled(self.feature)


def logCloseView(method):

    @wraps(method)
    def _impl(self, *methodArgs, **methodKwargs):
        try:
            if _loggingEnabled(self):
                self.logStatistic(action=MS_LOG_ACTIONS.CLOSE, timeSpent=int(BigWorld.time()) - self._populateTime)
        except Exception:
            _logger.exception('Close view')

        return method(self, *methodArgs, **methodKwargs)

    return _impl


def markTooltipOpened(method):

    @wraps(method)
    def _impl(self, *methodArgs, **methodKwargs):
        try:
            from gui.Scaleform.daapi.view.lobby.header.BattleTypeSelectPopover import BattleTypeSelectPopover
            validArgs = len(methodArgs) > 1 and isinstance(methodArgs[0], str) and isinstance(methodArgs[1], bool)
            if _loggingEnabled(self) and isinstance(self, BattleTypeSelectPopover) and validArgs:
                tooltip, advanced = methodArgs[0], methodArgs[1]
                if self._tooltip and self._tooltip == tooltip:
                    self._uiTooltipOpened = (int(BigWorld.time()), tooltip, advanced)
        except Exception:
            _logger.exception('Tooltip opened')

        return method(self, *methodArgs, **methodKwargs)

    return _impl


def logTooltipClosed(timeLimit=0):

    def wrapper(method):

        @wraps(method)
        def _impl(self, *methodArgs, **methodKwargs):
            try:
                if _loggingEnabled(self):
                    if self._uiTooltipOpened is not None:
                        openTime, tooltip, advanced = self._uiTooltipOpened
                        self._uiTooltipOpened = None
                        timeSpent = int(BigWorld.time()) - openTime
                        if timeSpent >= timeLimit:
                            self.logStatistic(action=MS_LOG_ACTIONS.TOOLTIP_WATCHED, timeSpent=timeSpent, tooltip=tooltip, isTooltipAdvanced=advanced)
            except Exception:
                _logger.exception('Tooltip closed')

            return method(self, *methodArgs, **methodKwargs)

        return _impl

    return wrapper


def logSelectMode(method):

    @wraps(method)
    def _impl(self, *methodArgs, **methodKwargs):
        try:
            available = _loggingEnabled(self) and methodArgs and isinstance(methodArgs[0], str)
            if available:
                self.logStatistic(action=MS_LOG_ACTIONS.SELECT_MODE, currentMode=methodArgs[0])
        except Exception:
            _logger.exception('Select mode')

        return method(self, *methodArgs, **methodKwargs)

    return _impl


def logChangeMode(method):

    @wraps(method)
    def _impl(self, *methodArgs, **methodKwargs):
        previous = None
        try:
            from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _BattleSelectorItems
            available = isinstance(self, _BattleSelectorItems)
            if available:
                previous = next((item.getData() for item in self.allItems if item.isSelected()), None)
        except Exception:
            available = False
            _logger.exception('Change mode')

        selected = method(self, *methodArgs, **methodKwargs)
        try:
            if available:
                selectedItem = next((item for item in self.allItems if item.isSelected()), None)
                if selectedItem and previous and previous != selectedItem.getData() and _loggingEnabled(self):
                    vo = selectedItem.getVO()
                    self.logStatistic(action=MS_LOG_ACTIONS.CHANGE_MODE, previousMode=previous, currentMode=selectedItem.getData(), isNewMode=selectedItem.isShowNewIndicator(), isFeaturedMode=bool(vo.get('specialBgIcon')))
        except Exception:
            _logger.exception('Change mode')

        return selected

    return _impl
