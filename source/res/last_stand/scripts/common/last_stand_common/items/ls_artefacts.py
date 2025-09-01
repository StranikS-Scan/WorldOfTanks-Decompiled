# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/common/last_stand_common/items/ls_artefacts.py
from typing import TYPE_CHECKING
from collections import namedtuple
from items.artefacts import DynComponentsGroupEquipment
from items import _xml
from last_stand_common.ls_utils import formatVehicleInfoString
if TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
LSEquipmentVariant = namedtuple('LSEquipmentVariant', ('id', 'cooldownSeconds', 'durationSeconds', 'usageCost', 'equipmentItem', 'dynComponentsGroups'))

class LSEquipment(DynComponentsGroupEquipment):
    __slots__ = ('equipmentItem', 'usageCost', 'variantIdFormat', 'variants', '_fallbackVariant')

    def _readConfig(self, xmlCtx, section):
        super(LSEquipment, self)._readConfig(xmlCtx, section)
        self.equipmentItem = _xml.readString(xmlCtx, section, 'equipmentItem') if section.has_key('equipmentItem') else None
        self.usageCost = _xml.readFloat(xmlCtx, section, 'usageCost')
        self.variantIdFormat = section.readString('variantIdFormat') if section.has_key('variantIdFormat') else None
        variants = _xml.getChildren(xmlCtx, section, 'variants', throwIfMissing=False)
        self.variants = {_xml.readString(xmlCtx, variant, 'id'):self._readVariant(xmlCtx, variant) for _, variant in variants}
        self._fallbackVariant = LSEquipmentVariant(id='', cooldownSeconds=self.cooldownSeconds, durationSeconds=self.durationSeconds, usageCost=self.usageCost, equipmentItem=self.equipmentItem, dynComponentsGroups=self.dynComponentsGroups)
        return

    @property
    def fallbackVariant(self):
        return self._fallbackVariant

    def getVariant(self, vehTypeDescr):
        return self._fallbackVariant if not self.variants or self.variantIdFormat is None else self.variants.get(formatVehicleInfoString(self.variantIdFormat, vehTypeDescr), self._fallbackVariant)

    @staticmethod
    def _readVariant(xmlCtx, section):
        return LSEquipmentVariant(id=_xml.readString(xmlCtx, section, 'id'), cooldownSeconds=_xml.readFloat(xmlCtx, section, 'cooldownSeconds'), durationSeconds=_xml.readFloat(xmlCtx, section, 'durationSeconds'), usageCost=_xml.readFloat(xmlCtx, section, 'usageCost'), equipmentItem=_xml.readString(xmlCtx, section, 'equipmentItem') if section.has_key('equipmentItem') else None, dynComponentsGroups=frozenset(_xml.readString(xmlCtx, section, 'dynComponentsGroups').split()))
