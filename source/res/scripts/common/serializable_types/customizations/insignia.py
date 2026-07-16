# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serializable_types/customizations/insignia.py
from __future__ import absolute_import
from collections import OrderedDict
from items.components.c11n_constants import ApplyArea
from py2to3.patched_future import with_metaclass
from serialization.field import xmlOnlyIntField, xmlOnlyApplyAreaEnumField
from serialization.serializable_component import SerializableComponent
from wrapped_reflection_framework import ReflectionMetaclass
from ..types import C11nSerializationTypes
__all__ = ('InsigniaComponent',)

class InsigniaComponent(with_metaclass(ReflectionMetaclass, SerializableComponent)):
    customType = C11nSerializationTypes.INSIGNIA
    fields = OrderedDict((('id', xmlOnlyIntField()), ('appliedTo', xmlOnlyApplyAreaEnumField(ApplyArea.NONE))))
    __slots__ = ('id', 'appliedTo')

    def __init__(self, id=0, appliedTo=ApplyArea.NONE):
        self.id = id
        self.appliedTo = appliedTo
        super(InsigniaComponent, self).__init__()

    def isGunInsignia(self):
        return self.appliedTo == ApplyArea.GUN
