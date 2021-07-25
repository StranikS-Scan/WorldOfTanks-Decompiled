# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/perks_matrix/branch_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.perk_model import PerkModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.ultimate_perk_model import UltimatePerkModel

class BranchModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(BranchModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getPerksList(self):
        return self._getArray(2)

    def setPerksList(self, value):
        self._setArray(2, value)

    def getUltimatePerksList(self):
        return self._getArray(3)

    def setUltimatePerksList(self, value):
        self._setArray(3, value)

    def getCurrentPoints(self):
        return self._getNumber(4)

    def setCurrentPoints(self, value):
        self._setNumber(4, value)

    def getMaxPoints(self):
        return self._getNumber(5)

    def setMaxPoints(self, value):
        self._setNumber(5, value)

    def getAreUltimatePerksUnlocked(self):
        return self._getBool(6)

    def setAreUltimatePerksUnlocked(self, value):
        self._setBool(6, value)

    def getHasUnsavedPoints(self):
        return self._getBool(7)

    def setHasUnsavedPoints(self, value):
        self._setBool(7, value)

    def getIsHighlighted(self):
        return self._getBool(8)

    def setIsHighlighted(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(BranchModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addStringProperty('icon', '')
        self._addArrayProperty('perksList', Array())
        self._addArrayProperty('ultimatePerksList', Array())
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addBoolProperty('areUltimatePerksUnlocked', False)
        self._addBoolProperty('hasUnsavedPoints', False)
        self._addBoolProperty('isHighlighted', False)
