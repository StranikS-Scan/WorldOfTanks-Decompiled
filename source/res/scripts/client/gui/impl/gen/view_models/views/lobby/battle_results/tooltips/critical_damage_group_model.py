# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/tooltips/critical_damage_group_model.py
from frameworks.wulf import ViewModel

class CriticalDamageGroupModel(ViewModel):
    __slots__ = ()
    CRITICAL_DEVICES = 'criticalDevices'
    DESTROYED_DEVICES = 'destroyedDevices'
    DESTROYED_TANKMENS = 'destroyedTankmen'

    def __init__(self, properties=2, commands=0):
        super(CriticalDamageGroupModel, self).__init__(properties=properties, commands=commands)

    def getDamageGroup(self):
        return self._getString(0)

    def setDamageGroup(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(CriticalDamageGroupModel, self)._initialize()
        self._addStringProperty('damageGroup', '')
        self._addStringProperty('value', '')
