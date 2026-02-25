# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/configs/sub_modes/custom_shells.py
from __future__ import absolute_import
import typing
from dict2model import fields, models, schemas
from fun_random.gui.feature.fun_constants import FunCustomShellsSource

class FunSubModeCustomShellConfigModel(models.Model):
    __slots__ = ('intCD',)

    def __init__(self, intCD):
        super(FunSubModeCustomShellConfigModel, self).__init__()
        self.intCD = intCD


class FunSubModeCustomShellSlotConfigModel(models.Model):
    __slots__ = ('command', 'imageOverride', 'tooltipOverride')

    def __init__(self, command, imageOverride, tooltipOverride):
        super(FunSubModeCustomShellSlotConfigModel, self).__init__()
        self.command = command
        self.imageOverride = imageOverride
        self.tooltipOverride = tooltipOverride


class FunSubModeCustomShellLayoutConfigModel(models.Model):
    __slots__ = ('shellSource', 'shellIndex', 'shellCount', 'slotIndex')

    def __init__(self, shellSource, shellIndex, shellCount, slotIndex):
        super(FunSubModeCustomShellLayoutConfigModel, self).__init__()
        self.shellSource = shellSource
        self.shellIndex = shellIndex
        self.shellCount = shellCount
        self.slotIndex = slotIndex


class FunSubModeCustomShellsConfigModel(models.Model):
    __slots__ = ('shells', 'slots', 'layouts')

    def __init__(self, shells=None, slots=None, layouts=None):
        super(FunSubModeCustomShellsConfigModel, self).__init__()
        self.shells = shells if shells is not None else []
        self.slots = slots if slots is not None else []
        self.layouts = layouts if layouts is not None else []
        return

    @property
    def exists(self):
        return bool(self.layouts)


funSubModeCustomShellSchema = schemas.Schema[FunSubModeCustomShellConfigModel](fields={'intCD': fields.Integer(required=True)}, modelClass=FunSubModeCustomShellConfigModel)
funSubModeCustomShellSlotSchema = schemas.Schema[FunSubModeCustomShellSlotConfigModel](fields={'command': fields.String(required=False, default=''),
 'imageOverride': fields.String(required=False, default=''),
 'tooltipOverride': fields.String(required=False, default='')}, modelClass=FunSubModeCustomShellSlotConfigModel)
funSubModeCustomShellLayoutSchema = schemas.Schema[FunSubModeCustomShellLayoutConfigModel](fields={'shellSource': fields.StrEnum(enumClass=FunCustomShellsSource, required=True),
 'shellIndex': fields.Integer(required=True),
 'shellCount': fields.Integer(required=False, default=0),
 'slotIndex': fields.Integer(required=True)}, modelClass=FunSubModeCustomShellLayoutConfigModel)
funSubModeCustomShellsSchema = schemas.Schema[FunSubModeCustomShellsConfigModel](fields={'shells': fields.UniCapList(fieldOrSchema=funSubModeCustomShellSchema, required=False),
 'slots': fields.UniCapList(fieldOrSchema=funSubModeCustomShellSlotSchema, required=False),
 'layouts': fields.UniCapList(fieldOrSchema=funSubModeCustomShellLayoutSchema, required=False)}, modelClass=FunSubModeCustomShellsConfigModel)
