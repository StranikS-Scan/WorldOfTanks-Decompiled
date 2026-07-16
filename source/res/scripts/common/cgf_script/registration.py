# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_script/registration.py
from __future__ import absolute_import
import sys
import CGF
import BigWorld
from future.utils import viewitems
g_propertyIndex = 0

class ComponentProperty(object):

    def __init__(self, type=CGF.PropertyType.Int, value=None, editorName='', **kwarg):
        global g_propertyIndex
        if type == CGF.PropertyType.Link and value is None:
            value = CGF.GameObject
        kwarg.update({'type': type,
         'value': value,
         'editorName': editorName,
         'name': '',
         'ownerName': ''})
        self.__metadata = kwarg
        self.__index = 0
        self.__baseIndex = g_propertyIndex
        g_propertyIndex += 1
        return

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
    name = 'script::{}'.format(cls.__name__)
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
        baseAttrs = vars(base)
        for key, value in viewitems(baseAttrs):
            if isinstance(value, ComponentProperty):
                setattr(cls, key, None)
                value.name = key
                value.ownerName = name
                value.applyIndex(basePropIndex)
                meta.append(value)

    for key, value in viewitems(attrs):
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
    user_visible = getattr(cls, 'userVisible', True)
    vse_visible = getattr(cls, 'vseVisible', True)
    name = getattr(cls, 'serialName', name)
    domain = getattr(cls, 'domain', CGF.Domain.All)
    if module_path is None:
        module_path = sys.modules[cls.__module__].__file__ if cls.__module__ != '__builtin__' else '__builtin__'
    CGF.registerComponent(cls, module_path, name, editor_title, user_visible, vse_visible, domain, category)
    g_propertyIndex = 0
    return cls


def registerComponent(cls):
    setattr(cls, CGF.CGF_COMPONENT_MARKER, None)
    return defaultRegistrator(cls)


def registerReplicableComponent(cls):
    setattr(cls, CGF.CGF_REPLICABLE_COMPONENT_MARKER, None)
    return defaultRegistrator(cls)


def registerModule(cls):
    modulePath = sys.modules[cls.__module__].__file__ if cls.__module__ != '__builtin__' else '__builtin__'
    CGF.registerModulePath(cls, modulePath)
    CGF.registerModule(cls)


def bonusCapsPredicate(caps, spaceID):
    try:
        from Avatar import PlayerAvatar
        from ClientArena import ClientArena
        player = BigWorld.player()
    except:
        return False

    return player.hasBonusCap(caps) if spaceID != ClientArena.DEFAULT_ARENA_WORLD_ID and isinstance(player, PlayerAvatar) else False
