# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/tooltips/excluded_maps_reward_slots_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MapStateEnum(Enum):
    MAPS_BLACKLIST_SLOT_STATE_ACTIVE = 'active'
    MAPS_BLACKLIST_SLOT_STATE_CHANGE = 'change'
    MAPS_BLACKLIST_SLOT_STATE_DISABLED = 'disabled'
    MAPS_BLACKLIST_SLOT_STATE_COOLDOWN = 'cooldown'
    MAPS_BLACKLIST_SLOT_STATE_SELECTED = 'selected'
    MAPS_BLACKLIST_SLOT_STATE_ACTIVE_NO_HOVER = 'activeNoHover'


class ExcludedMapsRewardSlotsTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ExcludedMapsRewardSlotsTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return MapStateEnum(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getCooldownTime(self):
        return self._getNumber(1)

    def setCooldownTime(self, value):
        self._setNumber(1, value)

    def getExpirationTime(self):
        return self._getNumber(2)

    def setExpirationTime(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ExcludedMapsRewardSlotsTooltipViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('cooldownTime', 0)
        self._addNumberProperty('expirationTime', 0)
