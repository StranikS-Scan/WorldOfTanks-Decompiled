# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/xml_config_specs.py
import json
from Math import Vector2, Vector3, Vector4
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any
    from ResMgr import DataSection

class IParam(object):

    def read(self, section, name=''):
        raise NotImplementedError


class SimpleParam(IParam):
    _DEFAULT = None
    _SIMPLE_METHOD = None

    def __init__(self, default=None, name=None):
        self._name = name
        self._default = default

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default if self._default is not None else self._DEFAULT

    def read(self, section, name=''):
        return self.default if not section else self._read(section, self.name if self.name is not None else name)

    def _read(self, section, name):
        method = getattr(section, self._SIMPLE_METHOD)
        return method(name, self.default)


class IntParam(SimpleParam):
    _DEFAULT = 0
    _SIMPLE_METHOD = 'readInt'


class BoolParam(SimpleParam):
    _DEFAULT = False
    _SIMPLE_METHOD = 'readBool'


class FloatParam(SimpleParam):
    _DEFAULT = 0.0
    _SIMPLE_METHOD = 'readFloat'


class StrParam(SimpleParam):
    _DEFAULT = ''
    _SIMPLE_METHOD = 'readString'


class Vector2Param(SimpleParam):
    _DEFAULT = Vector2()
    _SIMPLE_METHOD = 'readVector2'


class Vector3Param(SimpleParam):
    _DEFAULT = Vector3()
    _SIMPLE_METHOD = 'readVector3'


class Vector4Param(SimpleParam):
    _DEFAULT = Vector4()
    _SIMPLE_METHOD = 'readVector4'


class JsonParam(SimpleParam):

    def _read(self, section, name):
        res = json.loads(section.readString(name) or 'null')
        return res if res is not None else self.default


class ListParam(SimpleParam):
    _DEFAULT = []

    def __init__(self, valueParam=StrParam(), itemName='item', name=None):
        super(ListParam, self).__init__(name=name)
        self._itemName = itemName
        self._valueParam = valueParam

    def _read(self, section, name):
        valueName = self._valueParam.name if self._valueParam.name is not None else ''
        res = [ self._valueParam.read(itemSection, valueName) for itemName, itemSection in section[name].items() if self._itemName is None or self._itemName == itemName ]
        return res


class DictParam(SimpleParam):
    _DEFAULT = {}

    def __init__(self, valueParam=StrParam(), keyParam=StrParam(), itemName='item', name=None):
        super(DictParam, self).__init__(name=name)
        self._itemName = itemName
        self._keyParam = keyParam
        self._valueParam = valueParam

    def _read(self, section, name):
        keyName = self._keyParam.name if self._keyParam.name is not None else 'key'
        valueName = self._valueParam.name if self._valueParam.name is not None else 'value'
        res = {self._keyParam.read(itemSection, keyName):self._valueParam.read(itemSection, valueName) for itemName, itemSection in section[name].items() if self._itemName is None or self._itemName == itemName}
        return res


class ObjParam(SimpleParam):

    class Obj(object):
        pass

    _DEFAULT = Obj()

    def __init__(self, name=None, **specs):
        super(ObjParam, self).__init__(name=name)
        self._specs = {paramName:paramReader for paramName, paramReader in specs.items() if isinstance(paramReader, IParam)}

    def _read(self, section, name):
        obj = self.Obj()
        paramSection = section[name]
        for paramName, paramReader in self._specs.items():
            setattr(obj, paramName, paramReader.read(paramSection, paramName))

        return obj


class EnumParam(StrParam):

    def __init__(self, enum, default, name=None):
        super(EnumParam, self).__init__(name=name)
        self._enum = enum
        self._defaultValue = default

    def _read(self, section, name):
        attrName = super(EnumParam, self)._read(section, name)
        return self._defaultValue if not attrName else getattr(self._enum, attrName)
