# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tank_setup/array_provider.py
from __future__ import absolute_import
from gui.impl.lobby.tank_setup.array_providers.consumable import ConsumableDeviceProvider
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.impl import backport
from gui.impl.gen import R

class HalloweenConsumableProvider(ConsumableDeviceProvider):
    INCLUDE_TAGS = frozenset(['hwEquipment'])
    EXCLUDE_TAGS = frozenset(['hwEmptySlot'])

    def createSlot(self, item, ctx):
        model = super(HalloweenConsumableProvider, self).createSlot(item, ctx)
        itemDescription = item.shortDescription
        variant = item.descriptor.getVariant(self._getVehicle().descriptor)
        if variant:
            itemDescription += backport.text(R.strings.artefacts.hwAbility.descr.usageCost(), cost=str(int(variant.usageCost)))
        model.setDescription(itemDescription)
        return model

    def _getItemCriteria(self):
        return REQ_CRITERIA.VEHICLE.HAS_TAGS(self.INCLUDE_TAGS) | ~REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(self.EXCLUDE_TAGS) | ~REQ_CRITERIA.HIDDEN
