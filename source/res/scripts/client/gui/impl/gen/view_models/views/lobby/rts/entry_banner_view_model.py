# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/entry_banner_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    ANNOUNCE = 'announce'
    AVAILABLE = 'available'
    SUSPENDED = 'suspended'
    PAUSED = 'paused'
    FINISHED = 'finished'


class EntryBannerViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(EntryBannerViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getState(self):
        return State(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(EntryBannerViewModel, self)._initialize()
        self._addNumberProperty('startDate', -1)
        self._addNumberProperty('endDate', -1)
        self._addStringProperty('state')
        self.onClick = self._addCommand('onClick')
