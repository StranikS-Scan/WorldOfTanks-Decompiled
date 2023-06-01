# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_ability_level_param_model.py
from frameworks.wulf import ViewModel

class BattleAbilityLevelParamModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(BattleAbilityLevelParamModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getValueTemplate(self):
        return self._getString(1)

    def setValueTemplate(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getString(2)

    def setValue(self, value):
        self._setString(2, value)

    def getName(self):
        return self._getString(3)

    def setName(self, value):
        self._setString(3, value)

    def getSign(self):
        return self._getString(4)

    def setSign(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(BattleAbilityLevelParamModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('valueTemplate', '')
        self._addStringProperty('value', '')
        self._addStringProperty('name', '')
        self._addStringProperty('sign', '')
