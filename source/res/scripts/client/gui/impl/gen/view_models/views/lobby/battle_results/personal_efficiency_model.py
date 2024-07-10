# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/personal_efficiency_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EfficiencyParameter(Enum):
    KILLS = 'kills'
    SPOTTED = 'spotted'
    DAMAGEDEALT = 'damageDealt'
    STUN = 'damageAssistedStun'
    DAMAGEASSISTED = 'damageAssisted'
    DAMAGEBLOCKEDBYARMOR = 'damageBlockedByArmor'
    CAPTUREPOINTS = 'capturePoints'
    DROPPEDCAPTUREPOINTS = 'droppedCapturePoints'


class PersonalEfficiencyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PersonalEfficiencyModel, self).__init__(properties=properties, commands=commands)

    def getParamType(self):
        return EfficiencyParameter(self._getString(0))

    def setParamType(self, value):
        self._setString(0, value.value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(PersonalEfficiencyModel, self)._initialize()
        self._addStringProperty('paramType')
        self._addNumberProperty('value', 0)
