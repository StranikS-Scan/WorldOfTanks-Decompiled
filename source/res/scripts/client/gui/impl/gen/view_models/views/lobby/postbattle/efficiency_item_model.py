# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/efficiency_item_model.py
from frameworks.wulf import ViewModel

class EfficiencyItemModel(ViewModel):
    __slots__ = ()
    DAMAGE_ASSISTED_STUN = 'damageAssistedStun'
    SPOTTED = 'spotted'
    DAMAGE_ASSISTED = 'damageAssisted'
    DAMAGE_BLOCKED_BY_ARMOR = 'damageBlockedByArmor'
    CRITS_COUNT = 'critsCount'
    DAMAGE_DEALT = 'damageDealt'
    KILLS = 'kills'

    def __init__(self, properties=4, commands=0):
        super(EfficiencyItemModel, self).__init__(properties=properties, commands=commands)

    def getParamName(self):
        return self._getString(0)

    def setParamName(self, value):
        self._setString(0, value)

    def getSimpleValue(self):
        return self._getNumber(1)

    def setSimpleValue(self, value):
        self._setNumber(1, value)

    def getDetailedValue(self):
        return self._getNumber(2)

    def setDetailedValue(self, value):
        self._setNumber(2, value)

    def getIsVisible(self):
        return self._getBool(3)

    def setIsVisible(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(EfficiencyItemModel, self)._initialize()
        self._addStringProperty('paramName', '')
        self._addNumberProperty('simpleValue', 0)
        self._addNumberProperty('detailedValue', 0)
        self._addBoolProperty('isVisible', True)
