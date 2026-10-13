# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/halloween_common/items/hw_supply_slots_components.py
from __future__ import absolute_import
from items.components.supply_slots_components import EquipmentSlot
from items.vehicles import getItemByCompactDescr

class HWEquipmentSlot(EquipmentSlot):

    def readFromSection(self, section):
        super(HWEquipmentSlot, self).readFromSection(section)
        self.tags = frozenset(section.readString('tags').split())

    def _checkSlotCompatibility(self, parsedCompDescr=None, descr=None):
        item = descr or getItemByCompactDescr(parsedCompDescr)
        eqTags = getattr(item, 'tags', set())
        return (False, 'Equipment tags ({}) does not contain any of slot tags ({})'.format(eqTags, self.tags)) if self.tags and not eqTags.intersection(self.tags) else super(HWEquipmentSlot, self)._checkSlotCompatibility(parsedCompDescr, descr)
