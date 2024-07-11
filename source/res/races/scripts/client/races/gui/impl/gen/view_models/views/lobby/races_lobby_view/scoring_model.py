# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_lobby_view/scoring_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ScoringTypeEnum(Enum):
    SHOT = 'shot'
    RAM = 'ram'
    SHOCK = 'shock'
    BOOST = 'boost'
    SHIELD = 'shield'
    IMPULSE = 'impulse'


class ScoringModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ScoringModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getType(self):
        return ScoringTypeEnum(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getRacesPoints(self):
        return self._getNumber(2)

    def setRacesPoints(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ScoringModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('type', ScoringTypeEnum.SHOT.value)
        self._addNumberProperty('racesPoints', 0)
