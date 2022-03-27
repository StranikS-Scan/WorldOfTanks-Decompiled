# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/meta_stats_card_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.meta_stat_indicator_model import MetaStatIndicatorModel

class Submode(Enum):
    ONEVSSEVEN = 'oneVsSeven'
    TANKER = 'tanker'
    ONEVSONE = 'oneVsOne'


class MetaStatsCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MetaStatsCardModel, self).__init__(properties=properties, commands=commands)

    def getSubmode(self):
        return Submode(self._getString(0))

    def setSubmode(self, value):
        self._setString(0, value.value)

    def getBattlesPlayed(self):
        return self._getNumber(1)

    def setBattlesPlayed(self, value):
        self._setNumber(1, value)

    def getDamage(self):
        return self._getNumber(2)

    def setDamage(self, value):
        self._setNumber(2, value)

    def getStatIndicators(self):
        return self._getArray(3)

    def setStatIndicators(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(MetaStatsCardModel, self)._initialize()
        self._addStringProperty('submode')
        self._addNumberProperty('battlesPlayed', 0)
        self._addNumberProperty('damage', 0)
        self._addArrayProperty('statIndicators', Array())
