# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/characteristics_skill_model.py
from frameworks.wulf import ViewModel

class CharacteristicsSkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CharacteristicsSkillModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(CharacteristicsSkillModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('icon', '')
