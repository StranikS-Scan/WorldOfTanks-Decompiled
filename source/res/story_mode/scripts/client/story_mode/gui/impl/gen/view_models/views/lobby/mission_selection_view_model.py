# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/mission_selection_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class MissionSelectionViewModel(ViewModel):
    __slots__ = ('onQuit', 'onMissionSelect', 'onLoaded')

    def __init__(self, properties=3, commands=3):
        super(MissionSelectionViewModel, self).__init__(properties=properties, commands=commands)

    def getMissionId(self):
        return self._getNumber(0)

    def setMissionId(self, value):
        self._setNumber(0, value)

    def getIsTaskCompleted(self):
        return self._getBool(1)

    def setIsTaskCompleted(self, value):
        self._setBool(1, value)

    def getMissions(self):
        return self._getArray(2)

    def setMissions(self, value):
        self._setArray(2, value)

    @staticmethod
    def getMissionsType():
        return bool

    def _initialize(self):
        super(MissionSelectionViewModel, self)._initialize()
        self._addNumberProperty('missionId', 0)
        self._addBoolProperty('isTaskCompleted', False)
        self._addArrayProperty('missions', Array())
        self.onQuit = self._addCommand('onQuit')
        self.onMissionSelect = self._addCommand('onMissionSelect')
        self.onLoaded = self._addCommand('onLoaded')
