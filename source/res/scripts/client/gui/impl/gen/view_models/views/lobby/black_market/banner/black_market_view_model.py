# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/black_market/banner/black_market_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class StatusEnum(Enum):
    ANNOUNCE = 'announce'
    ACTIVE = 'active'
    DISABLED = 'disabled'


class PhaseEnum(Enum):
    LOOTBOX = 'lootbox'
    SPECIAL = 'special'


class BlackMarketViewModel(ViewModel):
    __slots__ = ('toBlackMarketEvent',)

    def __init__(self, properties=5, commands=1):
        super(BlackMarketViewModel, self).__init__(properties=properties, commands=commands)

    def getIsAloneBanner(self):
        return self._getBool(0)

    def setIsAloneBanner(self, value):
        self._setBool(0, value)

    def getIsNew(self):
        return self._getBool(1)

    def setIsNew(self, value):
        self._setBool(1, value)

    def getTimer(self):
        return self._getNumber(2)

    def setTimer(self, value):
        self._setNumber(2, value)

    def getStatus(self):
        return StatusEnum(self._getString(3))

    def setStatus(self, value):
        self._setString(3, value.value)

    def getEventPhase(self):
        return PhaseEnum(self._getString(4))

    def setEventPhase(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(BlackMarketViewModel, self)._initialize()
        self._addBoolProperty('isAloneBanner', False)
        self._addBoolProperty('isNew', False)
        self._addNumberProperty('timer', 123456789)
        self._addStringProperty('status', StatusEnum.ACTIVE.value)
        self._addStringProperty('eventPhase', PhaseEnum.SPECIAL.value)
        self.toBlackMarketEvent = self._addCommand('toBlackMarketEvent')
