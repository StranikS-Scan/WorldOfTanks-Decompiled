# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/type.py
from inspect import getmembers
from enumerations import Enumeration
from enum import IntEnum
from misc import EDITOR_TYPE, ASPECT
from typing import Any, List
__all__ = ('VScriptType', 'VScriptEnum', 'VScriptStruct', 'VScriptStructField')

class VScriptType(object):

    @classmethod
    def slotType(cls):
        return cls.vs_pyType().__name__

    @classmethod
    def vs_pyType(cls):
        return cls

    @classmethod
    def vs_name(cls):
        return cls.slotType() + 'T'

    @classmethod
    def vs_aspects(cls):
        return ASPECT.ALL

    @classmethod
    def vs_editor(cls):
        return EDITOR_TYPE.NONE

    @classmethod
    def vs_equals(cls, a, b):
        return a == b

    @classmethod
    def vs_toString(cls, value):
        pass

    @classmethod
    def vs_fromString(cls, str_):
        return None

    @classmethod
    def vs_connectionColor(cls):
        pass

    @classmethod
    def vs_iconConnected(cls):
        pass

    @classmethod
    def vs_iconDisconnected(cls):
        pass


class VScriptEnum(object):

    @classmethod
    def slotType(cls):
        return cls.vs_enum().__name__

    @classmethod
    def vs_enum(cls):
        return cls

    @classmethod
    def _vs_collectEnumEntries(cls):
        entriesData = {}
        if isinstance(cls.vs_enum(), Enumeration):
            enum = cls.vs_enum()
            for item in enum.all():
                entriesData[item.name()] = item.index()

        if isinstance(cls.vs_enum(), IntEnum):
            enum = cls.vs_enum()
            for item in enum:
                entriesData[item.name] = item.value

        else:
            for name, member in getmembers(cls.vs_enum()):
                if not name.startswith('_') and isinstance(member, int):
                    entriesData[name] = member

        return entriesData

    @classmethod
    def vs_name(cls):
        return cls.slotType() + 'T'

    @classmethod
    def vs_aspects(cls):
        return ASPECT.ALL


class VScriptStructField(object):

    def __init__(self, displayName, fieldType):
        self.name = '#' + displayName
        self.type = fieldType

    def __get__(self, instance, owner):
        return getattr(instance, self.name, None)

    def __set__(self, instance, value):
        setattr(instance, self.name, value)


class AllowVScriptStruct(type):

    def __new__(cls, name, bases, members):
        fieldData = {}
        for key, value in members.iteritems():
            if isinstance(value, VScriptStructField):
                fieldData[value.name[1:]] = value.type

        members.update({'vs_fields': fieldData})
        return type.__new__(cls, name, bases, members)


class VScriptStruct(object):
    __metaclass__ = AllowVScriptStruct

    def __new__(cls, *args, **kwargs):
        return super(VScriptStruct, cls).__new__(cls)

    @classmethod
    def slotType(cls):
        return cls.__name__

    @classmethod
    def vs_aspects(cls):
        return ASPECT.ALL

    @classmethod
    def vs_module(cls):
        return cls.__module__

    @classmethod
    def vs_name(cls):
        return cls.slotType() + 'T'
