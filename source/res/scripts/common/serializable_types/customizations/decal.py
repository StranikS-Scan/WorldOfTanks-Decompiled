# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/decal.py
from collections import OrderedDict
from items.components.c11n_constants import ApplyArea
from serialization.field import intField, applyAreaEnumField
from serialization.serializable_component import SerializableComponent
from wrapped_reflection_framework import ReflectionMetaclass
from ..types import C11nSerializationTypes
__all__ = ('DecalComponent',)

class DecalComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = C11nSerializationTypes.DECAL
    fields = OrderedDict((('id', intField()), ('appliedTo', applyAreaEnumField(ApplyArea.NONE)), ('progressionLevel', intField(0))))
    __slots__ = ('id', 'appliedTo', 'progressionLevel')

    def __init__(self, id=0, appliedTo=ApplyArea.NONE, progressionLevel=0):
        self.id = id
        self.appliedTo = appliedTo
        self.progressionLevel = progressionLevel
        super(DecalComponent, self).__init__()
