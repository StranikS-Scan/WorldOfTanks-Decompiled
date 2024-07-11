# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_banner_view/races_banner_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    ACTIVE = 'active'
    DISABLED = 'disabled'


class RacesBannerViewModel(ViewModel):
    __slots__ = ('onOpenRacesLobby',)

    def __init__(self, properties=3, commands=1):
        super(RacesBannerViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getEndTime(self):
        return self._getNumber(1)

    def setEndTime(self, value):
        self._setNumber(1, value)

    def getTimeLeft(self):
        return self._getNumber(2)

    def setTimeLeft(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(RacesBannerViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('endTime', 0)
        self._addNumberProperty('timeLeft', 0)
        self.onOpenRacesLobby = self._addCommand('onOpenRacesLobby')
