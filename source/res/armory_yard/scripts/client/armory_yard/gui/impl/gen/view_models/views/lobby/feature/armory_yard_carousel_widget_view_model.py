# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_carousel_widget_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    BEFOREPROGRESSION = 'beforeProgression'
    ACTIVE = 'active'
    ACTIVELASTHOURS = 'activeLastHours'
    POSTPROGRESSION = 'postProgression'
    COMPLETED = 'completed'
    DISABLED = 'disabled'


class ArmoryYardCarouselWidgetViewModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=4, commands=1):
        super(ArmoryYardCarouselWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getStartTime(self):
        return self._getNumber(1)

    def setStartTime(self, value):
        self._setNumber(1, value)

    def getEndTime(self):
        return self._getNumber(2)

    def setEndTime(self, value):
        self._setNumber(2, value)

    def getCurrentTime(self):
        return self._getNumber(3)

    def setCurrentTime(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ArmoryYardCarouselWidgetViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('startTime', 0)
        self._addNumberProperty('endTime', 0)
        self._addNumberProperty('currentTime', 0)
        self.onAction = self._addCommand('onAction')
