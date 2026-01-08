# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/stronghold/tooltips/stronghold_main_widget_tooltip_model.py
from frameworks.wulf import ViewModel

class StrongholdMainWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(StrongholdMainWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    def getSprintType(self):
        return self._getString(0)

    def setSprintType(self, value):
        self._setString(0, value)

    def getSprintNumber(self):
        return self._getNumber(1)

    def setSprintNumber(self, value):
        self._setNumber(1, value)

    def getSprintStartDate(self):
        return self._getString(2)

    def setSprintStartDate(self, value):
        self._setString(2, value)

    def getSprintEndDate(self):
        return self._getString(3)

    def setSprintEndDate(self, value):
        self._setString(3, value)

    def getIsEventActive(self):
        return self._getBool(4)

    def setIsEventActive(self, value):
        self._setBool(4, value)

    def getIsDataAvailable(self):
        return self._getBool(5)

    def setIsDataAvailable(self, value):
        self._setBool(5, value)

    def getProgressionLevel(self):
        return self._getNumber(6)

    def setProgressionLevel(self, value):
        self._setNumber(6, value)

    def getIsInClan(self):
        return self._getBool(7)

    def setIsInClan(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(StrongholdMainWidgetTooltipModel, self)._initialize()
        self._addStringProperty('sprintType', '')
        self._addNumberProperty('sprintNumber', 0)
        self._addStringProperty('sprintStartDate', '')
        self._addStringProperty('sprintEndDate', '')
        self._addBoolProperty('isEventActive', False)
        self._addBoolProperty('isDataAvailable', False)
        self._addNumberProperty('progressionLevel', 0)
        self._addBoolProperty('isInClan', False)
