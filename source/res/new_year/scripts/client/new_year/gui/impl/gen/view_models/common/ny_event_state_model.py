# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/common/ny_event_state_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EventState(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'


class NyEventStateModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyEventStateModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return EventState(self._getString(0))

    def setValue(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(NyEventStateModel, self)._initialize()
        self._addStringProperty('value', EventState.PAUSED.value)
