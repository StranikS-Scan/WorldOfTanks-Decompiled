# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/rewards_header_tooltip_model.py
from frameworks.wulf import ViewModel

class RewardsHeaderTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RewardsHeaderTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsLevelAchieved(self):
        return self._getBool(0)

    def setIsLevelAchieved(self, value):
        self._setBool(0, value)

    def getIsCurrentLevel(self):
        return self._getBool(1)

    def setIsCurrentLevel(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(RewardsHeaderTooltipModel, self)._initialize()
        self._addBoolProperty('isLevelAchieved', False)
        self._addBoolProperty('isCurrentLevel', False)
