# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/comp7_style_bonus_model.py
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel

class Comp7StyleBonusModel(Comp7BonusModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(Comp7StyleBonusModel, self).__init__(properties=properties, commands=commands)

    def getStyleID(self):
        return self._getNumber(14)

    def setStyleID(self, value):
        self._setNumber(14, value)

    def getBranchID(self):
        return self._getNumber(15)

    def setBranchID(self, value):
        self._setNumber(15, value)

    def getProgressLevel(self):
        return self._getNumber(16)

    def setProgressLevel(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(Comp7StyleBonusModel, self)._initialize()
        self._addNumberProperty('styleID', 0)
        self._addNumberProperty('branchID', 0)
        self._addNumberProperty('progressLevel', 0)
