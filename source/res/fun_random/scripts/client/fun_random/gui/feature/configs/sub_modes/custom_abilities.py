# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/configs/sub_modes/custom_abilities.py
from __future__ import absolute_import
import typing
from dict2model import fields, models, schemas

class FunSubModeCustomAbilityConfigModel(models.Model):
    __slots__ = ('intCD',)

    def __init__(self, intCD):
        super(FunSubModeCustomAbilityConfigModel, self).__init__()
        self.intCD = intCD


class FunSubModeCustomAbilitySlotConfigModel(models.Model):
    __slots__ = ('command', 'tooltipAlias')

    def __init__(self, command, tooltipAlias):
        super(FunSubModeCustomAbilitySlotConfigModel, self).__init__()
        self.command = command
        self.tooltipAlias = tooltipAlias


class FunSubModeCustomAbilityLayoutConfigModel(models.Model):
    __slots__ = ('abilityIndex', 'slotIndex')

    def __init__(self, abilityIndex, slotIndex):
        super(FunSubModeCustomAbilityLayoutConfigModel, self).__init__()
        self.abilityIndex = abilityIndex
        self.slotIndex = slotIndex


class FunSubModeCustomAbilitiesConfigModel(models.Model):
    __slots__ = ('abilities', 'slots', 'layouts')

    def __init__(self, abilities=None, slots=None, layouts=None):
        super(FunSubModeCustomAbilitiesConfigModel, self).__init__()
        self.abilities = abilities if abilities is not None else []
        self.slots = slots if slots is not None else []
        self.layouts = layouts if layouts is not None else []
        return

    @property
    def exists(self):
        return bool(self.layouts)


funSubModeCustomAbilitySchema = schemas.Schema[FunSubModeCustomAbilityConfigModel](fields={'intCD': fields.Integer(required=True)}, modelClass=FunSubModeCustomAbilityConfigModel)
funSubModeCustomAbilitySlotSchema = schemas.Schema[FunSubModeCustomAbilitySlotConfigModel](fields={'command': fields.String(required=False, default=''),
 'tooltipAlias': fields.String(required=False, default='')}, modelClass=FunSubModeCustomAbilitySlotConfigModel)
funSubModeCustomAbilityLayoutSchema = schemas.Schema[FunSubModeCustomAbilityLayoutConfigModel](fields={'abilityIndex': fields.Integer(required=True),
 'slotIndex': fields.Integer(required=True)}, modelClass=FunSubModeCustomAbilityLayoutConfigModel)
funSubModeCustomAbilitiesSchema = schemas.Schema[FunSubModeCustomAbilitiesConfigModel](fields={'abilities': fields.UniCapList(fieldOrSchema=funSubModeCustomAbilitySchema, required=False),
 'slots': fields.UniCapList(fieldOrSchema=funSubModeCustomAbilitySlotSchema, required=False),
 'layouts': fields.UniCapList(fieldOrSchema=funSubModeCustomAbilityLayoutSchema, required=False)}, modelClass=FunSubModeCustomAbilitiesConfigModel)
