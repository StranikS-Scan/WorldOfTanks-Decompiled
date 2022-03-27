# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/meta_stat_indicator_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class Indicator(Enum):
    WINRATE = 'winRate'
    XP = 'xp'
    TANKSDESTROYEDBYSTRATEGIST = 'tanksDestroyedByStrategist'
    TANKSDESTROYEDBYSTRATEGISTSUPPLIES = 'tanksDestroyedByStrategistSupplies'
    TANKSDESTROYEDBYTANKER = 'tanksDestroyedByTanker'
    SUPPLIESDESTROYEDBYTANKER = 'suppliesDestroyedByTanker'
    AVGAPM = 'avgAPM'
    PEAKAPM = 'peakAPM'


class MetaStatIndicatorModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MetaStatIndicatorModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return Indicator(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(MetaStatIndicatorModel, self)._initialize()
        self._addStringProperty('type')
        self._addNumberProperty('value', 0)
