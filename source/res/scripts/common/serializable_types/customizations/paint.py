# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/paint.py
from collections import OrderedDict
from typing import Dict
from items.components.c11n_constants import ApplyArea
from serialization.field import intField, applyAreaEnumField
from serialization.serializable_component import SerializableComponent
from wrapped_reflection_framework import ReflectionMetaclass
from ..types import C11nSerializationTypes
__all__ = ('PaintComponent',)

class PaintComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = C11nSerializationTypes.PAINT
    fields = OrderedDict((('id', intField()), ('appliedTo', applyAreaEnumField(ApplyArea.PAINT_REGIONS_VALUE))))
    __slots__ = ('id', 'appliedTo')

    def __init__(self, id=0, appliedTo=ApplyArea.PAINT_REGIONS_VALUE):
        self.id = id
        self.appliedTo = appliedTo
        super(PaintComponent, self).__init__()

    def toDict(self):
        at = self.appliedTo
        p = self.id
        return {i:p for i in ApplyArea.RANGE if i & at}
