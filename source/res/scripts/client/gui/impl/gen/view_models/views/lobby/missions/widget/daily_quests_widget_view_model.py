# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/widget/daily_quests_widget_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class DailyQuestsWidgetViewModel(ViewModel):
    __slots__ = ('onMissionClick', 'onNothingToDisplay')

    def __init__(self, properties=4, commands=2):
        super(DailyQuestsWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getMissions(self):
        return self._getArray(0)

    def setMissions(self, value):
        self._setArray(0, value)

    def getCountDown(self):
        return self._getNumber(1)

    def setCountDown(self, value):
        self._setNumber(1, value)

    def getIsVisible(self):
        return self._getBool(2)

    def setIsVisible(self, value):
        self._setBool(2, value)

    def getMissionsCompletedVisited(self):
        return self._getArray(3)

    def setMissionsCompletedVisited(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(DailyQuestsWidgetViewModel, self)._initialize()
        self._addArrayProperty('missions', Array())
        self._addNumberProperty('countDown', 0)
        self._addBoolProperty('isVisible', False)
        self._addArrayProperty('missionsCompletedVisited', Array())
        self.onMissionClick = self._addCommand('onMissionClick')
        self.onNothingToDisplay = self._addCommand('onNothingToDisplay')
