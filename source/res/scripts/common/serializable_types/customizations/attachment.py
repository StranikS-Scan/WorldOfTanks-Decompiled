# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/attachment.py
from __future__ import absolute_import
from collections import OrderedDict
from py2to3.patched_future import with_metaclass
from serialization.field import intField
from serialization.serializable_component import SerializableComponent
from wrapped_reflection_framework import ReflectionMetaclass
from ..types import C11nSerializationTypes
__all__ = ('AttachmentComponent',)

class AttachmentComponent(with_metaclass(ReflectionMetaclass, SerializableComponent)):
    customType = C11nSerializationTypes.ATTACHMENT
    fields = OrderedDict((('id', intField()),
     ('slotId', intField()),
     ('scaleFactorId', intField()),
     ('rotated', intField())))
    __slots__ = ('id', 'slotId', 'scaleFactorId', 'rotated')

    def __init__(self, id=0, slotId=0, scaleFactorId=0, rotated=0):
        self.id = id
        self.slotId = slotId
        self.scaleFactorId = scaleFactorId
        self.rotated = rotated
        super(AttachmentComponent, self).__init__()

    @property
    def isRotated(self):
        return bool(self.rotated)

    def setScaleFactorId(self, itemScaleFactorId, slotScaleFactorId):
        self.scaleFactorId = min(itemScaleFactorId, slotScaleFactorId)
