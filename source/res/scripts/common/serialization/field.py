# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serialization/field.py
from .definitions import FieldTypes, FieldType, FieldFlags
__all__ = ('arrayField', 'intField', 'strField', 'xmlOnlyIntField', 'xmlOnlyFloatField', 'xmlOnlyFloatArrayField', 'applyAreaEnumField', 'xmlOnlyApplyAreaEnumField', 'xmlOnlyTagsField', 'optionsEnumField', 'customFieldType', 'intArrayField', 'customArrayField')

def arrayField(itemType, default=None, flags=FieldFlags.NONE):
    return FieldType(FieldTypes.TYPED_ARRAY | itemType, default or [], flags)


def intField(default=0, nonXml=False):
    return FieldType(FieldTypes.VARINT, default, FieldFlags.NON_XML if nonXml else FieldFlags.NONE)


def strField(default=''):
    return FieldType(FieldTypes.STRING, default, FieldFlags.NONE)


def xmlOnlyIntField(default=0):
    return FieldType(FieldTypes.VARINT, default, FieldFlags.NON_BIN)


def xmlOnlyFloatField(default=0):
    return FieldType(FieldTypes.FLOAT, default, FieldFlags.NON_BIN)


def xmlOnlyFloatArrayField(default=None):
    return FieldType(FieldTypes.TYPED_ARRAY | FieldTypes.FLOAT, default or [], FieldFlags.NON_BIN)


def applyAreaEnumField(default=0):
    return FieldType(FieldTypes.APPLY_AREA_ENUM, default, FieldFlags.WEAK_EQUAL_IGNORED)


def xmlOnlyApplyAreaEnumField(default=0, flags=FieldFlags.NONE):
    return FieldType(FieldTypes.APPLY_AREA_ENUM, default, FieldFlags.WEAK_EQUAL_IGNORED | FieldFlags.NON_BIN | flags)


def xmlOnlyTagsField(default=()):
    return FieldType(FieldTypes.TAGS, default, FieldFlags.WEAK_EQUAL_IGNORED | FieldFlags.NON_BIN)


def optionsEnumField(default=0):
    return FieldType(FieldTypes.OPTIONS_ENUM, default, FieldFlags.NONE)


def customFieldType(customType):
    return FieldType(FieldTypes.CUSTOM_TYPE_OFFSET * customType, None, FieldFlags.NONE)


def intArrayField(default=None, flags=FieldFlags.NONE):
    return arrayField(FieldTypes.VARINT, default or [], flags)


def customArrayField(customType, default=None):
    return arrayField(FieldTypes.CUSTOM_TYPE_OFFSET * customType, default)
