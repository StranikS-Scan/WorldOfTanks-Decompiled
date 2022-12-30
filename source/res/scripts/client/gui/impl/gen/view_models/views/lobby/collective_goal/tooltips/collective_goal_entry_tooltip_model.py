# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collective_goal/tooltips/collective_goal_entry_tooltip_model.py
from frameworks.wulf import ViewModel

class CollectiveGoalEntryTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(CollectiveGoalEntryTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getStage(self):
        return self._getNumber(1)

    def setStage(self, value):
        self._setNumber(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getCurrentPoints(self):
        return self._getNumber(4)

    def setCurrentPoints(self, value):
        self._setNumber(4, value)

    def getTotalPoints(self):
        return self._getNumber(5)

    def setTotalPoints(self, value):
        self._setNumber(5, value)

    def getCaption(self):
        return self._getString(6)

    def setCaption(self, value):
        self._setString(6, value)

    def getEndDate(self):
        return self._getNumber(7)

    def setEndDate(self, value):
        self._setNumber(7, value)

    def getIsFinished(self):
        return self._getBool(8)

    def setIsFinished(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(CollectiveGoalEntryTooltipModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addNumberProperty('stage', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('totalPoints', 0)
        self._addStringProperty('caption', '')
        self._addNumberProperty('endDate', 0)
        self._addBoolProperty('isFinished', False)
