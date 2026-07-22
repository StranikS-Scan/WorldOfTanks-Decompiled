# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/maps_blacklist_slot_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MapStateEnum(Enum):
    MAPS_BLACKLIST_SLOT_STATE_ACTIVE = 'active'
    MAPS_BLACKLIST_SLOT_STATE_CHANGE = 'change'
    MAPS_BLACKLIST_SLOT_STATE_DISABLED = 'disabled'
    MAPS_BLACKLIST_SLOT_STATE_DISABLED_BY_KILL_SWITCH = 'disabledByKillSwitch'
    MAPS_BLACKLIST_SLOT_STATE_COOLDOWN = 'cooldown'
    MAPS_BLACKLIST_SLOT_STATE_SELECTED = 'selected'
    MAPS_BLACKLIST_SLOT_STATE_ACTIVE_NO_HOVER = 'activeNoHover'


class SlotTypeEnum(Enum):
    DEFAULT = 'defaultSlots'
    PREMIUM = 'premiumSlots'
    SUBSCRB = 'subscrbSlots'
    REWARDS = 'rewardsSlots'


class MapsBlacklistSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(MapsBlacklistSlotModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return SlotTypeEnum(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getState(self):
        return MapStateEnum(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getMapId(self):
        return self._getString(2)

    def setMapId(self, value):
        self._setString(2, value)

    def getSeasonId(self):
        return self._getNumber(3)

    def setSeasonId(self, value):
        self._setNumber(3, value)

    def getCooldownTime(self):
        return self._getNumber(4)

    def setCooldownTime(self, value):
        self._setNumber(4, value)

    def getExpirationTime(self):
        return self._getNumber(5)

    def setExpirationTime(self, value):
        self._setNumber(5, value)

    def getFiltered(self):
        return self._getBool(6)

    def setFiltered(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(MapsBlacklistSlotModel, self)._initialize()
        self._addStringProperty('type')
        self._addStringProperty('state')
        self._addStringProperty('mapId', '')
        self._addNumberProperty('seasonId', 0)
        self._addNumberProperty('cooldownTime', 0)
        self._addNumberProperty('expirationTime', 0)
        self._addBoolProperty('filtered', True)
