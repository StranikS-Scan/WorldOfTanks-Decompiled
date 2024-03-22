# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/base/state_machine/states.py
import typing
from frameworks.state_machine import State
if typing.TYPE_CHECKING:
    from enum import IntEnum

class BaseState(State):
    __slots__ = ('_view', '_widgetType', '_widgetId')

    def __init__(self, stateID, flags):
        super(BaseState, self).__init__(stateID.name, flags)
        self._view = None
        self._widgetType = None
        self._widgetId = None
        return

    def configure(self, view, widgetType, widgetId):
        super(BaseState, self).configure()
        self._view = view
        self._widgetType = widgetType
        self._widgetId = widgetId

    def getSettings(self):
        return self._view.getSettings((self._widgetType, self._widgetId))

    def update(self):
        self._updateView()

    def _onEntered(self):
        self._showView()

    def _showView(self):
        pass

    def _updateView(self):
        pass


class BaseTimerState(BaseState):
    __slots__ = ('_doShow', '_doUpdate')

    def __init__(self, stateID, flags):
        super(BaseTimerState, self).__init__(stateID, flags)
        self._doUpdate = False
        self._doShow = False

    def update(self):
        self._doUpdate = True

    def _onEntered(self):
        self._doShow = True

    def _onExited(self):
        super(BaseTimerState, self)._onExited()
        self._doUpdate = False
        self._doShow = False

    def tick(self, currentTime):
        if self._doShow:
            self._showView()
            self._doShow = False
            self._doUpdate = False
        elif self._doUpdate:
            self._updateView()
            self._doUpdate = False
