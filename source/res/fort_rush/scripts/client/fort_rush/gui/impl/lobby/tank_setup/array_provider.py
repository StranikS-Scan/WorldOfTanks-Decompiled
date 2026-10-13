# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/tank_setup/array_provider.py
from __future__ import absolute_import
from past.builtins import xrange
from gui.impl.lobby.tank_setup.array_providers.consumable import ConsumableDeviceProvider
from gui.shared.utils.requesters import REQ_CRITERIA
from items import ITEM_TYPES

class FortRushConsumableProvider(ConsumableDeviceProvider):

    def _getExcludeTags(self):
        vehicle = self._getVehicle()
        if vehicle is None:
            return frozenset()
        else:
            supplySlots = vehicle.descriptor.type.supplySlots
            excludeTags = set()
            for idx in xrange(supplySlots.getAmountForType(ITEM_TYPES.equipment)):
                slot = supplySlots.getSlotByIdxInItemType(ITEM_TYPES.equipment, idx)
                excludeTags.update(getattr(slot, 'excludeTags', ()))

            return frozenset(excludeTags)

    def _getItemCriteria(self):
        criteria = super(FortRushConsumableProvider, self)._getItemCriteria()
        excludeTags = self._getExcludeTags()
        return criteria if not excludeTags else criteria | ~REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(excludeTags)
