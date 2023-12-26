# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/markers/advent_calendar_marker_view_model.py
from frameworks.wulf import ViewModel

class AdventCalendarMarkerViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(AdventCalendarMarkerViewModel, self).__init__(properties=properties, commands=commands)

    def getAvailableDoorsAmount(self):
        return self._getNumber(0)

    def setAvailableDoorsAmount(self, value):
        self._setNumber(0, value)

    def getIsVisible(self):
        return self._getBool(1)

    def setIsVisible(self, value):
        self._setBool(1, value)

    def getDogSacksAvailable(self):
        return self._getBool(2)

    def setDogSacksAvailable(self, value):
        self._setBool(2, value)

    def getIsPostEvent(self):
        return self._getBool(3)

    def setIsPostEvent(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(AdventCalendarMarkerViewModel, self)._initialize()
        self._addNumberProperty('availableDoorsAmount', 0)
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('dogSacksAvailable', False)
        self._addBoolProperty('isPostEvent', False)
