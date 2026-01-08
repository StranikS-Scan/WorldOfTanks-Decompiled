# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_interfaces.py
from __future__ import absolute_import
from GenericComponents import COMPOSITION_ROOT_SLOT_NAME
from constants import DEFAULT_GUN_INSTALLATION_INDEX
from gui.shared.utils.decorators import ReprInjector
from items.components.gun_installation_components import GunInstallationSlot

@ReprInjector.simple(('getVehicleSlotName', 'slotName'))
class IVehicleSlotComponent(object):

    def getVehicleSlotName(self):
        return COMPOSITION_ROOT_SLOT_NAME


class IVehicleGunSlotComponent(IVehicleSlotComponent):

    def getGunInstallationIndex(self):
        return DEFAULT_GUN_INSTALLATION_INDEX

    def getVehicleSlotName(self):
        return GunInstallationSlot.getPartSlotNameByIndex(self.getGunInstallationIndex())
