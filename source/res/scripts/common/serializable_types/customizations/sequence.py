# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/sequence.py
from collections import OrderedDict
from serialization.field import intField
from serialization.serializable_component import SerializableComponent
from wrapped_reflection_framework import ReflectionMetaclass
from ..types import C11nSerializationTypes
__all__ = ('SequenceComponent',)

class SequenceComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = C11nSerializationTypes.SEQUENCE
    fields = OrderedDict((('id', intField()), ('slotId', intField())))
    __slots__ = ('id', 'slotId')

    def __init__(self, id=0, slotId=0):
        self.id = id
        self.slotId = slotId
        super(SequenceComponent, self).__init__()
