# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/skill_select_row_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.skill_select_item_model import SkillSelectItemModel

class SkillSelectRowModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SkillSelectRowModel, self).__init__(properties=properties, commands=commands)

    def getSkills(self):
        return self._getArray(0)

    def setSkills(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSkillsType():
        return SkillSelectItemModel

    def getCommonSkills(self):
        return self._getArray(1)

    def setCommonSkills(self, value):
        self._setArray(1, value)

    @staticmethod
    def getCommonSkillsType():
        return SkillSelectItemModel

    def getRole(self):
        return self._getString(2)

    def setRole(self, value):
        self._setString(2, value)

    def getPossibleMaxSelected(self):
        return self._getNumber(3)

    def setPossibleMaxSelected(self, value):
        self._setNumber(3, value)

    def getSelectedAmount(self):
        return self._getNumber(4)

    def setSelectedAmount(self, value):
        self._setNumber(4, value)

    def getTankmanIdx(self):
        return self._getNumber(5)

    def setTankmanIdx(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(SkillSelectRowModel, self)._initialize()
        self._addArrayProperty('skills', Array())
        self._addArrayProperty('commonSkills', Array())
        self._addStringProperty('role', '')
        self._addNumberProperty('possibleMaxSelected', 0)
        self._addNumberProperty('selectedAmount', 0)
        self._addNumberProperty('tankmanIdx', -1)
