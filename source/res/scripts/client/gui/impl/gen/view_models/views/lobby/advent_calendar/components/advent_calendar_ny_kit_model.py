# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/components/advent_calendar_ny_kit_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class AdventCalendarNyKitModel(ViewModel):
    __slots__ = ('onSwitchResource',)

    def __init__(self, properties=4, commands=1):
        super(AdventCalendarNyKitModel, self).__init__(properties=properties, commands=commands)

    def getResources(self):
        return self._getArray(0)

    def setResources(self, value):
        self._setArray(0, value)

    @staticmethod
    def getResourcesType():
        return unicode

    def getCurrentResource(self):
        return self._getString(1)

    def setCurrentResource(self, value):
        self._setString(1, value)

    def getPrice(self):
        return self._getNumber(2)

    def setPrice(self, value):
        self._setNumber(2, value)

    def getNotEnoughResource(self):
        return self._getBool(3)

    def setNotEnoughResource(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(AdventCalendarNyKitModel, self)._initialize()
        self._addArrayProperty('resources', Array())
        self._addStringProperty('currentResource', '')
        self._addNumberProperty('price', 0)
        self._addBoolProperty('notEnoughResource', False)
        self.onSwitchResource = self._addCommand('onSwitchResource')
