# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/map_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SlotStateEnum(Enum):
    EMPTY = 'empty'
    SELECTED = 'selected'
    DISABLED = 'disabled'
    DISABLEDBYKILLSWITCH = 'disabledByKillSwitch'


class SlotTypeEnum(Enum):
    DEFAULT = 'defaultSlots'
    PREMIUM = 'premiumSlots'
    SUBSCRB = 'subscrbSlots'
    REWARDS = 'rewardsSlots'


class MapModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MapModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return SlotTypeEnum(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getMapId(self):
        return self._getString(1)

    def setMapId(self, value):
        self._setString(1, value)

    def getSlotState(self):
        return SlotStateEnum(self._getString(2))

    def setSlotState(self, value):
        self._setString(2, value.value)

    def getCooldownEndTimeInSecs(self):
        return self._getNumber(3)

    def setCooldownEndTimeInSecs(self, value):
        self._setNumber(3, value)

    def getExpirationTime(self):
        return self._getNumber(4)

    def setExpirationTime(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(MapModel, self)._initialize()
        self._addStringProperty('type')
        self._addStringProperty('mapId', '')
        self._addStringProperty('slotState')
        self._addNumberProperty('cooldownEndTimeInSecs', 0)
        self._addNumberProperty('expirationTime', 0)
