# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/client_perk_blocks.py
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from visual_script.block import SLOT_TYPE
from visual_script.perk_blocks import PerkBlock

class AddFactorModifier(PerkBlock):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(AddFactorModifier, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', AddFactorModifier._execute)
        self._vehIntId = self._makeDataInputSlot('vehId', SLOT_TYPE.INT)
        self._perkId = self._makeDataInputSlot('perkId', SLOT_TYPE.INT)
        self._scopeId = self._makeDataInputSlot('scopeId', SLOT_TYPE.INT)
        self._value = self._makeDataInputSlot('value', SLOT_TYPE.FLOAT)
        self._factor = self._makeDataInputSlot('factor', SLOT_TYPE.STR)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        vehIntId = self._vehIntId.getValue()
        perkId = self._perkId.getValue()
        scopeId = self._scopeId.getValue()
        value = self._value.getValue()
        factor = self._factor.getValue()
        perksController = self.itemsCache.items.getItemByCD(vehIntId).getPerksController()
        perksController.modifyFactor(factor, scopeId, perkId, value)
        self._outSlot.call()


class RemoveFactorModifiers(PerkBlock):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(RemoveFactorModifiers, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', RemoveFactorModifiers._execute)
        self._vehIntId = self._makeDataInputSlot('vehId', SLOT_TYPE.INT)
        self._perkId = self._makeDataInputSlot('perkId', SLOT_TYPE.INT)
        self._scopeId = self._makeDataInputSlot('scopeId', SLOT_TYPE.INT)
        self._factor = self._makeDataInputSlot('factor', SLOT_TYPE.STR)
        self._numMods = self._makeDataInputSlot('numMods', SLOT_TYPE.INT)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        vehIntId = self._vehIntId.getValue()
        perkId = self._perkId.getValue()
        scopeId = self._scopeId.getValue()
        factor = self._factor.getValue()
        numMods = self._numMods.getValue()
        perksController = self.itemsCache.items.getItemByCD(vehIntId).getPerksController()
        if numMods > 0:
            perksController.removeNumFactorModifiers(factor, scopeId, perkId, numMods)
        else:
            perksController.dropFactorModifiers(factor, scopeId, perkId)
        self._outSlot.call()


class DropAllPerkModifiers(PerkBlock):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(DropAllPerkModifiers, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', DropAllPerkModifiers._execute)
        self._vehIntId = self._makeDataInputSlot('vehId', SLOT_TYPE.INT)
        self._perkId = self._makeDataInputSlot('perkId', SLOT_TYPE.INT)
        self._scopeId = self._makeDataInputSlot('scopeId', SLOT_TYPE.INT)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        vehIntId = self._vehIntId.getValue()
        perkId = self._perkId.getValue()
        scopeId = self._scopeId.getValue()
        perksController = self.itemsCache.items.getItemByCD(vehIntId).getPerksController()
        perksController.dropAllPerkModifiers(scopeId, perkId)
        self._outSlot.call()
