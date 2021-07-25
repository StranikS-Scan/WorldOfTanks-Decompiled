# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/perk_blocks.py
from visual_script.block import Meta, Block
from visual_script.slot_types import SLOT_TYPE
from constants import IS_EDITOR
if not IS_EDITOR:
    from items import perks
    from items.components.perks_constants import PERK_BONUS_VALUE_PRECISION
    from debug_utils import LOG_ERROR

class Perk(Meta):

    @classmethod
    def blockCategory(cls):
        pass


class AddFactorModifierBase(Block, Perk):

    def __init__(self, *args, **kwargs):
        super(AddFactorModifierBase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._vehId = self._makeDataInputSlot('vehId', SLOT_TYPE.INT)
        self._perkId = self._makeDataInputSlot('perkId', SLOT_TYPE.INT)
        self._scopeId = self._makeDataInputSlot('scopeId', SLOT_TYPE.INT)
        self._value = self._makeDataInputSlot('value', SLOT_TYPE.FLOAT)
        self._factor = self._makeDataInputSlot('factor', SLOT_TYPE.STR)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        pass


class RemoveFactorModifiersBase(Block, Perk):

    def __init__(self, *args, **kwargs):
        super(RemoveFactorModifiersBase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._vehId = self._makeDataInputSlot('vehId', SLOT_TYPE.INT)
        self._perkId = self._makeDataInputSlot('perkId', SLOT_TYPE.INT)
        self._scopeId = self._makeDataInputSlot('scopeId', SLOT_TYPE.INT)
        self._factor = self._makeDataInputSlot('factor', SLOT_TYPE.STR)
        self._numMods = self._makeDataInputSlot('numMods', SLOT_TYPE.INT)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        pass


class DropAllPerkModifiersBase(Block, Perk):

    def __init__(self, *args, **kwargs):
        super(DropAllPerkModifiersBase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._vehId = self._makeDataInputSlot('vehId', SLOT_TYPE.INT)
        self._perkId = self._makeDataInputSlot('perkId', SLOT_TYPE.INT)
        self._scopeId = self._makeDataInputSlot('scopeId', SLOT_TYPE.INT)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        pass


class VehicleInRangeLoopBase(Block, Perk):

    def __init__(self, *args, **kwargs):
        super(VehicleInRangeLoopBase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._vehTeam = self._makeDataInputSlot('vehTeam', SLOT_TYPE.INT)
        self._vehClass = self._makeDataInputSlot('vehClass', SLOT_TYPE.STR)
        self._range = self._makeDataInputSlot('range', SLOT_TYPE.INT)
        self._interval = self._makeDataInputSlot('interval', SLOT_TYPE.FLOAT)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        pass


class ModifyTerrainResistanceBase(Block):

    def __init__(self, *args, **kwargs):
        super(ModifyTerrainResistanceBase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._perk = self._makeDataInputSlot('perk', SLOT_TYPE.PERK)
        self._firmGroundFactor = self._makeDataInputSlot('firmGroundFactor', SLOT_TYPE.FLOAT)
        self._mediumGroundFactor = self._makeDataInputSlot('mediumGroundFactor', SLOT_TYPE.FLOAT)
        self._softGroundFactor = self._makeDataInputSlot('softGroundFactor', SLOT_TYPE.FLOAT)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        pass


class AddEquipmentCooldownModifierBase(Block, Perk):

    def __init__(self, *args, **kwargs):
        super(AddEquipmentCooldownModifierBase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._perk = self._makeDataInputSlot('perk', SLOT_TYPE.PERK)
        self._value = self._makeDataInputSlot('value', SLOT_TYPE.FLOAT)
        self._equipmentName = self._makeDataInputSlot('equipmentName', SLOT_TYPE.STR)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        pass


class RemoveEquipmentCooldownModifierBase(Block, Perk):

    def __init__(self, *args, **kwargs):
        super(RemoveEquipmentCooldownModifierBase, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._perk = self._makeDataInputSlot('perk', SLOT_TYPE.PERK)
        self._equipmentName = self._makeDataInputSlot('equipmentName', SLOT_TYPE.STR)
        self._outSlot = self._makeEventOutputSlot('out')

    def _execute(self):
        pass


class PerkArgumentBase(Block):

    def __init__(self, *args, **kwargs):
        super(PerkArgumentBase, self).__init__(*args, **kwargs)
        self._perk = self._makeDataInputSlot('perk', SLOT_TYPE.PERK)
        self._argument = self._makeDataInputSlot('argument', SLOT_TYPE.STR)
        self._outSlot1 = self._makeDataOutputSlot('value', SLOT_TYPE.FLOAT, self._execute)
        self._outSlot2 = self._makeDataOutputSlot('maxStacks', SLOT_TYPE.INT, self._execute)

    def _execute(self):
        argument = self._argument.getValue()
        perk = self._perk.getValue()
        perkId = perk.perkID
        level = perk.perkLevel
        perkItem = perks.g_cache.perks().perks.get(perkId)
        argRecord = perkItem.defaultBlockSettings.get(argument)
        if not argRecord:
            LOG_ERROR('Perk item do not contain argument {}'.format(argument))
            return
        value = perkItem.getArgBonusByLevel(argument, level)
        self._outSlot1.setValue(round(value, PERK_BONUS_VALUE_PRECISION))
        maxStacks = argRecord.maxStacks
        self._outSlot2.setValue(maxStacks)
