# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_script/component_meta_class.py
import sys
import CGF

class CGFMetaTypes(object):
    BOOL = 'bool'
    STRING = 'string'
    FLOAT = 'real'
    INT = 'integer'
    STRING_LIST = 'CGF::ScriptList<string>'
    INT_LIST = 'CGF::ScriptList<int32>'
    FLOAT_LIST = 'CGF::ScriptList<float>'
    LINK = 'BW::CGF::PyLinkConfig'
    VECTOR2 = 'Vector2'
    VECTOR3 = 'Vector3'
    VECTOR4 = 'Vector4'


class ReplicationType(object):
    LATEST_ONLY = 0
    VOLATILE = 1
    HISTORY = 2


class RPCType(object):
    SERVER_TO_CLIENT = 0
    CLIENT_TO_SERVER = 1


g_propertyIndex = 0

class ComponentProperty(object):

    def __init__(self, type=CGFMetaTypes.INT, value=0, editorName='', **kwarg):
        global g_propertyIndex
        kwarg.update({'type': type,
         'value': value,
         'editorName': editorName,
         'name': '',
         'ownerName': ''})
        self.__metadata = kwarg
        self.__index = 0
        self.__baseIndex = g_propertyIndex
        g_propertyIndex += 1

    def __get__(self, instance, owner=None):
        return self.__metadata

    def __set__(self, instance, value):
        self.__metadata = value

    def applyIndex(self, shift):
        self.__index = self.__baseIndex + shift

    @property
    def metadata(self):
        return self.__metadata

    @property
    def name(self):
        return self.metadata['name']

    @name.setter
    def name(self, value):
        self.metadata['name'] = value

    @property
    def ownerName(self):
        return self.metadata['ownerName']

    @ownerName.setter
    def ownerName(self, value):
        self.metadata['ownerName'] = value

    @property
    def index(self):
        return self.__index

    def __call__(self, *args, **kwargs):
        pass


messages = []

class CGFMetaClass(type):

    def __new__(metacls, name, bases, attrs):
        global g_propertyIndex
        messages.append('InitMetaclass {0}'.format(name))
        cls = type.__new__(metacls, name, bases, attrs)
        if name == 'CGFComponent':
            CGF.registerBaseComponent(cls)
            return cls
        elif name == 'Rule':
            return cls
        else:
            meta = []
            allMeta = []
            basePropIndex = 0
            for base in bases:
                baseMeta = getattr(base, '__meta', None)
                if baseMeta is not None:
                    basePropIndex += len(baseMeta)
                    allMeta.extend(baseMeta)

            for key, value in attrs.items():
                if isinstance(value, ComponentProperty):
                    setattr(cls, key, None)
                    value.name = key
                    value.ownerName = name
                    value.applyIndex(basePropIndex)
                    meta.append(value)

            allMeta.extend(meta)
            setattr(cls, '__meta', allMeta)
            category = getattr(cls, 'category', 'Python')
            editorTitle = getattr(cls, 'editorTitle', name)
            modulePath = getattr(cls, 'modulePath', None)
            version = getattr(cls, 'version', 1)
            if modulePath is None:
                modulePath = sys.modules[cls.__module__].__file__ if cls.__module__ != '__builtin__' else '__builtin__'
            CGF.registerComponent(cls, modulePath, name, editorTitle, category, version)
            g_propertyIndex = 0
            return cls

    def __call__(cls, *args, **kwds):
        component = cls.__new__(cls, *args, **kwds)
        for key, value in kwds.items():
            component.__setattr__(key, value)

        component.__init__(*args)
        return component


class CGFComponent(object):
    __metaclass__ = CGFMetaClass

    def __init__(self):
        super(CGFComponent, self).__init__()


class CGFConverterMetaClass(type):

    def __new__(metacls, name, bases, attrs):
        cls = type.__new__(metacls, name, bases, attrs)
        if name == 'CGFComponentConverter':
            return cls
        CGF.registerScriptComponentConverter(name, cls)
        return cls


class CGFComponentConverter(object):
    __metaclass__ = CGFConverterMetaClass

    def sourceVersion(self):
        pass

    def targetVersion(self):
        pass

    def convert(self, sourceConfig, convertedConfig):
        pass
