# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/mission_difficulty_tooltip_model.py
from frameworks.wulf import ViewModel

class MissionDifficultyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MissionDifficultyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getDifficulty(self):
        return self._getString(0)

    def setDifficulty(self, value):
        self._setString(0, value)

    def getIsAutoCompleteCondition(self):
        return self._getBool(1)

    def setIsAutoCompleteCondition(self, value):
        self._setBool(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getIsLocked(self):
        return self._getBool(3)

    def setIsLocked(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(MissionDifficultyTooltipModel, self)._initialize()
        self._addStringProperty('difficulty', '')
        self._addBoolProperty('isAutoCompleteCondition', False)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isLocked', False)
