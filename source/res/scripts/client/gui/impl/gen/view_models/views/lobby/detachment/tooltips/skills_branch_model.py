# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/skills_branch_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.perk_model import PerkModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.ultimate_perk_model import UltimatePerkModel

class SkillsBranchModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SkillsBranchModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def getPerksList(self):
        return self._getArray(3)

    def setPerksList(self, value):
        self._setArray(3, value)

    def getUltimateList(self):
        return self._getArray(4)

    def setUltimateList(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(SkillsBranchModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addArrayProperty('perksList', Array())
        self._addArrayProperty('ultimateList', Array())
