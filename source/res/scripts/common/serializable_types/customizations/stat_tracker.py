# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/stat_tracker.py
from __future__ import absolute_import
from collections import OrderedDict
from py2to3.patched_future import with_metaclass
from serialization.field import intField
from serialization.serializable_component import SerializableComponent
from wrapped_reflection_framework import ReflectionMetaclass
from ..types import C11nSerializationTypes
__all__ = ('StatTrackerComponent',)

class StatTrackerComponent(with_metaclass(ReflectionMetaclass, SerializableComponent)):
    customType = C11nSerializationTypes.STAT_TRACKER
    fields = OrderedDict((('id', intField()), ('slotId', intField())))
    __slots__ = ('id', 'slotId')

    def __init__(self, id=0, slotId=0):
        self.id = id
        self.slotId = slotId
        super(StatTrackerComponent, self).__init__()
