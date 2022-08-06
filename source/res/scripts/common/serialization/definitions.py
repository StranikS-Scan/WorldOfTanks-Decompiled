# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serialization/definitions.py
from collections import namedtuple
import enum
from constants import IS_EDITOR
__all__ = ('FieldType', 'FieldTypes', 'FieldFlags')
if IS_EDITOR:
    FieldType = namedtuple('FieldType', 'type default flags saveTag')
    FieldType.__new__.func_defaults = (None,) * len(FieldType._fields)
else:
    FieldType = namedtuple('FieldType', 'type default flags')

class FieldTypes(object):
    VARINT = 2
    TAGS = 4
    OPTIONS_ENUM = 8
    FLOAT = 16
    APPLY_AREA_ENUM = 32
    TYPED_ARRAY = 64
    CUSTOM_TYPE_OFFSET = 128
    STRING = 512


@enum.unique
class FieldFlags(enum.IntEnum):
    NONE = 0
    DEPRECATED = 1
    WEAK_EQUAL_IGNORED = 2
    NON_XML = 4
    NON_BIN = 8
    NON_SERIALIZABLE = NON_XML | NON_BIN
    SAVE_AS_STRING = 16
    SAVE_AS_EDITOR_ONLY = 32
