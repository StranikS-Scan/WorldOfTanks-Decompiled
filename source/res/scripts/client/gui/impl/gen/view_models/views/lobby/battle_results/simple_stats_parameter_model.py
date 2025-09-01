# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/simple_stats_parameter_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen import R

class ValueType(IntEnum):
    INTEGER = 0
    FLOAT = 1
    TIME = 2


class RegularParamType(Enum):
    SHOTS = 'shots'
    HITS = 'hits'
    EXPLOSIONHITS = 'explosionHits'
    DAMAGEDEALT = 'damageDealt'
    SNIPERDAMAGEDEALT = 'sniperDamageDealt'
    DIRECTHITSRECEIVED = 'directHitsReceived'
    PIERCINGSRECEIVED = 'piercingsReceived'
    NODAMAGEDIRECTHITSRECEIVED = 'noDamageDirectHitsReceived'
    EXPLOSIONHITSRECEIVED = 'explosionHitsReceived'
    DAMAGEBLOCKEDBYARMOR = 'damageBlockedByArmor'
    TEAMHITSDAMAGE = 'teamHitsDamage'
    SPOTTED = 'spotted'
    DAMAGEDKILLED = 'damagedKilled'
    DAMAGEASSISTED = 'damageAssisted'
    DAMAGEASSISTEDSELF = 'damageAssistedSelf'
    STUNDURATION = 'stunDuration'
    DAMAGEASSISTEDSTUN = 'damageAssistedStun'
    DAMAGEASSISTEDSTUNSELF = 'damageAssistedStunSelf'
    STUNNUM = 'stunNum'
    CAPTUREPOINTSVAL = 'capturePointsVal'
    MILEAGE = 'mileage'


class SimpleStatsParameterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SimpleStatsParameterModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getLabelKey(self):
        return self._getString(1)

    def setLabelKey(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getArray(2)

    def setValue(self, value):
        self._setArray(2, value)

    @staticmethod
    def getValueType():
        return float

    def getParamValueType(self):
        return ValueType(self._getNumber(3))

    def setParamValueType(self, value):
        self._setNumber(3, value.value)

    def _initialize(self):
        super(SimpleStatsParameterModel, self)._initialize()
        self._addResourceProperty('label', R.invalid())
        self._addStringProperty('labelKey', '')
        self._addArrayProperty('value', Array())
        self._addNumberProperty('paramValueType')
