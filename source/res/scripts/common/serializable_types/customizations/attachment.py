# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/attachment.py
from collections import OrderedDict
from constants import IS_EDITOR
from serialization.field import intField, xmlOnlyIntField, xmlOnlyFloatArrayField
from serialization.serializable_component import SerializableComponent
from wrapped_reflection_framework import ReflectionMetaclass
from ..types import C11nSerializationTypes
__all__ = ('AttachmentComponent',)

class AttachmentComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = C11nSerializationTypes.ATTACHMENT
    if IS_EDITOR:
        slotIdFieldType = intField()
    else:
        slotIdFieldType = xmlOnlyIntField(0)
    fields = OrderedDict((('id', intField()),
     ('slotId', slotIdFieldType),
     ('position', xmlOnlyFloatArrayField()),
     ('rotation', xmlOnlyFloatArrayField())))
    __slots__ = ('id', 'slotId', 'position', 'rotation')

    def __init__(self, id=0, slotId=0, position=None, rotation=None):
        self.id = id
        self.slotId = slotId
        self.position = position or [0, 0, 0]
        self.rotation = rotation or [0, 0, 0]
        super(AttachmentComponent, self).__init__()
