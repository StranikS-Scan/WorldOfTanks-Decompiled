# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_script/component_meta_class.py
import sys
import CGF
import inspect
from debug_utils import LOG_CURRENT_EXCEPTION

class CGFMetaTypes(object):
    BOOL = 'bool'
    STRING = 'string'
    FLOAT = 'real'
    INT = 'integer'
    STRING_LIST = 'CGF::ScriptList<string>'
    INT_LIST = 'CGF::ScriptList<int32>'
    FLOAT_LIST = 'CGF::ScriptList<float>'
    VECTOR2_LIST = 'CGF::ScriptList<Vector2>'
    VECTOR3_LIST = 'CGF::ScriptList<Vector3>'
    VECTOR4_LIST = 'CGF::ScriptList<Vector4>'
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


def defaultRegistrator(cls):
    global g_propertyIndex
    name = cls.__name__
    meta = []
    all_meta = []
    bases = cls.__mro__
    attrs = vars(cls)
    basePropIndex = 0
    for base in bases:
        baseMeta = getattr(base, '__meta', None)
        if baseMeta is not None:
            basePropIndex += len(baseMeta)
            all_meta.extend(baseMeta)

    for key, value in attrs.iteritems():
        if isinstance(value, ComponentProperty):
            setattr(cls, key, None)
            value.name = key
            value.ownerName = name
            value.applyIndex(basePropIndex)
            meta.append(value)

    all_meta.extend(meta)
    setattr(cls, '__meta', all_meta)
    category = getattr(cls, 'category', 'Python')
    editor_title = getattr(cls, 'editorTitle', name)
    module_path = getattr(cls, 'modulePath', None)
    version = getattr(cls, 'version', 1)
    user_visible = getattr(cls, 'userVisible', True)
    vse_visible = getattr(cls, 'vseVisible', True)
    domain = getattr(cls, 'domain', CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
    if module_path is None:
        module_path = sys.modules[cls.__module__].__file__ if cls.__module__ != '__builtin__' else '__builtin__'
    CGF.registerComponent(cls, module_path, name, editor_title, user_visible, vse_visible, domain, category, version)
    g_propertyIndex = 0
    return cls


def registerComponent(cls):
    setattr(cls, CGF.CGF_COMPONENT_MARKER, None)
    return defaultRegistrator(cls)


def registerReplicableComponent(cls):
    setattr(cls, CGF.CGF_REPLICABLE_COMPONENT_MARKER, None)
    setattr(cls, 'domain', CGF.DomainOption.DomainAll | CGF.DomainOption.LockDomain)
    return defaultRegistrator(cls)


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
