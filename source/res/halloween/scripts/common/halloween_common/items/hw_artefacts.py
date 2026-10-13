# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/halloween_common/items/hw_artefacts.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
from collections import namedtuple
from items.artefacts import DynComponentsGroupEquipment
from items import _xml
from halloween_common.hw_utils import formatVehicleInfoString
if TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
HWEquipmentVariant = namedtuple('HWEquipmentVariant', ('id', 'cooldownSeconds', 'durationSeconds', 'usageCost', 'equipmentItem', 'dynComponentsGroups'))

class HWEquipment(DynComponentsGroupEquipment):
    __slots__ = ('equipmentItem', 'usageCost', 'variantIdFormat', 'variants', '_fallbackVariant')

    def _readConfig(self, xmlCtx, scriptSection):
        super(HWEquipment, self)._readConfig(xmlCtx, scriptSection)
        section = scriptSection
        self.equipmentItem = _xml.readString(xmlCtx, section, 'equipmentItem') if section.has_key('equipmentItem') else None
        self.usageCost = _xml.readFloat(xmlCtx, section, 'usageCost')
        self.variantIdFormat = section.readString('variantIdFormat') if section.has_key('variantIdFormat') else None
        variants = _xml.getChildren(xmlCtx, section, 'variants', throwIfMissing=False)
        self.variants = {_xml.readString(xmlCtx, variant, 'id'):self._readVariant(xmlCtx, variant) for _, variant in variants}
        self._fallbackVariant = HWEquipmentVariant(id='', cooldownSeconds=self.cooldownSeconds, durationSeconds=self.durationSeconds, usageCost=self.usageCost, equipmentItem=self.equipmentItem, dynComponentsGroups=self.dynComponentsGroups)
        return

    @property
    def fallbackVariant(self):
        return self._fallbackVariant

    def getVariant(self, vehTypeDescr):
        return self._fallbackVariant if not self.variants or self.variantIdFormat is None else self.variants.get(formatVehicleInfoString(self.variantIdFormat, vehTypeDescr), self._fallbackVariant)

    @staticmethod
    def _readVariant(xmlCtx, section):
        return HWEquipmentVariant(id=_xml.readString(xmlCtx, section, 'id'), cooldownSeconds=_xml.readFloat(xmlCtx, section, 'cooldownSeconds'), durationSeconds=_xml.readFloat(xmlCtx, section, 'durationSeconds'), usageCost=_xml.readFloat(xmlCtx, section, 'usageCost'), equipmentItem=_xml.readString(xmlCtx, section, 'equipmentItem') if section.has_key('equipmentItem') else None, dynComponentsGroups=frozenset(_xml.readString(xmlCtx, section, 'dynComponentsGroups').split()))
