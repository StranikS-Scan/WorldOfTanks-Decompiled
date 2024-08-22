# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/skill_model.py
from frameworks.wulf import ViewModel

class SkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SkillModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getIsZero(self):
        return self._getBool(3)

    def setIsZero(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SkillModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isZero', False)
