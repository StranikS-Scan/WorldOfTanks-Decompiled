# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/dialog_skill_model.py
from frameworks.wulf import ViewModel

class DialogSkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DialogSkillModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIconName(self):
        return self._getString(1)

    def setIconName(self, value):
        self._setString(1, value)

    def getLevel(self):
        return self._getReal(2)

    def setLevel(self, value):
        self._setReal(2, value)

    def getIsIrrelevant(self):
        return self._getBool(3)

    def setIsIrrelevant(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(DialogSkillModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('iconName', '')
        self._addRealProperty('level', 100)
        self._addBoolProperty('isIrrelevant', False)
