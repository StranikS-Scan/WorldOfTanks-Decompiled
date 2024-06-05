# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/live_ops_web_events/entry_point_base.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    PRE_EVENT = 'preEvent'
    EVENT_ACTIVE = 'eventActive'
    POST_EVENT = 'postEvent'


class EntryPointBase(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EntryPointBase, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getPreviousState(self):
        return State(self._getString(1))

    def setPreviousState(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(EntryPointBase, self)._initialize()
        self._addStringProperty('state')
        self._addStringProperty('previousState')
