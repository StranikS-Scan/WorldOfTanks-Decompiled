# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/cosmic_lobby_view/scoring_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ScoringTypeEnum(Enum):
    SCAN = 'scan'
    KILL = 'kill'
    PICKUP = 'pickup'
    RAM = 'ram'
    SHOT = 'shot'
    ABILITYHIT = 'abilityHit'


class ScoringModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ScoringModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return ScoringTypeEnum(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getMarsPoints(self):
        return self._getNumber(1)

    def setMarsPoints(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(ScoringModel, self)._initialize()
        self._addStringProperty('type', ScoringTypeEnum.SCAN.value)
        self._addNumberProperty('marsPoints', 0)
