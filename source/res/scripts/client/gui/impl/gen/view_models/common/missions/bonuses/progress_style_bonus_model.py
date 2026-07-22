# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/progress_style_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ProgressStyleBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(ProgressStyleBonusModel, self).__init__(properties=properties, commands=commands)

    def getStyleID(self):
        return self._getNumber(8)

    def setStyleID(self, value):
        self._setNumber(8, value)

    def getBranchID(self):
        return self._getNumber(9)

    def setBranchID(self, value):
        self._setNumber(9, value)

    def getProgressLevel(self):
        return self._getNumber(10)

    def setProgressLevel(self, value):
        self._setNumber(10, value)

    def getProgressLevelsCount(self):
        return self._getNumber(11)

    def setProgressLevelsCount(self, value):
        self._setNumber(11, value)

    def getIsGranted(self):
        return self._getBool(12)

    def setIsGranted(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(ProgressStyleBonusModel, self)._initialize()
        self._addNumberProperty('styleID', 0)
        self._addNumberProperty('branchID', 0)
        self._addNumberProperty('progressLevel', 0)
        self._addNumberProperty('progressLevelsCount', 0)
        self._addBoolProperty('isGranted', False)
