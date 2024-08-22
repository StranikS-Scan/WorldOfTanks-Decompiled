# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/compare_skill_model.py
from frameworks.wulf import ViewModel

class CompareSkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CompareSkillModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getLevel(self):
        return self._getReal(1)

    def setLevel(self, value):
        self._setReal(1, value)

    def _initialize(self):
        super(CompareSkillModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addRealProperty('level', 0.0)
