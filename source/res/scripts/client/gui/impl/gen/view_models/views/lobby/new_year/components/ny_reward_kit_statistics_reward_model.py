# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_reward_kit_statistics_reward_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class Type(Enum):
    NONE = ''
    VEHICLES = 'vehicles'
    CUSTOMIZATIONS = 'customizations'
    PREMIUMPLUS = 'premium_plus'
    GOLD = 'gold'
    CREDITS = 'credits'
    CURRENCIES = 'currencies'
    GUESTC = 'guest_c'
    MODERNIZEDEQUIPMENT = 'modernizedEquipment'
    NYTOYS = 'nyToys'


class NyRewardKitStatisticsRewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyRewardKitStatisticsRewardModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return Type(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyRewardKitStatisticsRewardModel, self)._initialize()
        self._addStringProperty('type', Type.NONE.value)
        self._addNumberProperty('count', 0)
