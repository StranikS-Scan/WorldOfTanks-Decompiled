# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/progress_style_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ProgressStyleBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
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

    def _initialize(self):
        super(ProgressStyleBonusModel, self)._initialize()
        self._addNumberProperty('styleID', 0)
        self._addNumberProperty('branchID', 0)
        self._addNumberProperty('progressLevel', 0)
