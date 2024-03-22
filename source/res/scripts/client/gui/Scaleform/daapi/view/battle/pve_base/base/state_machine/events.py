# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/base/state_machine/events.py
import typing
from frameworks.state_machine import StateEvent, StringEvent

class ToStateEvent(StringEvent):

    def __init__(self, widgetStateName, **kwargs):
        super(ToStateEvent, self).__init__(token=widgetStateName, **kwargs)


class OneSecondEvent(StateEvent):

    @property
    def lastTime(self):
        return self.getArgument('lastTime', 0.0)

    @property
    def currentTime(self):
        return self.getArgument('currentTime', 0.0)
