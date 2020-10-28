# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/factories.py
from soft_exception import SoftException
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule
from gui.Scaleform.framework.entities.View import View
from gui.shared.events import LoadViewEvent

class EntityFactory(object):

    def __init__(self, managedLayers):
        super(EntityFactory, self).__init__()
        self.__managedLayers = managedLayers

    def getManagedLayers(self):
        return self.__managedLayers

    def validate(self, settings):
        clazz = settings.clazz
        alias = settings.alias
        if not alias:
            raise SoftException('Invalid alias in settings {0}'.format(settings))
        if clazz is None:
            raise SoftException('Invalid class in settings {0}'.format(settings))
        return

    def create(self, settings, *args, **kwargs):
        clazz = settings.clazz
        pyEntity = None
        try:
            pyEntity = clazz(*args, **kwargs)
        except Exception:
            LOG_ERROR('There is error while daapi python-side class initialization:', clazz)
            LOG_CURRENT_EXCEPTION()

        return pyEntity

    def initialize(self, pyEntity, gfxEntity, extra=None):
        return pyEntity


DAAPIModuleType = type(BaseDAAPIModule)
ViewEntityType = type(View)

class DAAPIModuleFactory(EntityFactory):

    def validate(self, settings):
        super(DAAPIModuleFactory, self).validate(settings)
        if BaseDAAPIModule not in getattr(settings.clazz, '__mro__', tuple()):
            raise SoftException('Class does not extend BaseDAAPIModule in settings {0}'.format(settings))

    def castType(self, clazz):
        return isinstance(clazz, DAAPIModuleType)

    def initialize(self, pyEntity, gfxEntity, extra=None):
        pyEntity.setFlashObject(gfxEntity, autoPopulate=False)
        return pyEntity

    def create(self, settings, *args, **kwargs):
        pyEntity = super(DAAPIModuleFactory, self).create(settings, *args, **kwargs)
        if pyEntity is not None and isinstance(pyEntity, BaseDAAPIComponent):
            pyEntity.setAlias(settings.alias)
        return pyEntity


class ViewFactory(DAAPIModuleFactory):

    def validate(self, settings):
        super(ViewFactory, self).validate(settings)
        url = settings.url
        if not url:
            raise SoftException('Invalid url in settings {0}'.format(settings))
        if View not in getattr(settings.clazz, '__mro__', tuple()):
            raise SoftException('Class does not extend View in settings {0}'.format(settings))

    def create(self, settings, *args, **kwargs):
        pyEntity = super(ViewFactory, self).create(settings, *args, **kwargs)
        if pyEntity is not None:
            pyEntity.setSettings(settings)
        return pyEntity

    def initialize(self, pyEntity, gfxEntity, extra=None):
        pyEntity = super(ViewFactory, self).initialize(pyEntity, gfxEntity)
        if extra is not None:
            if 'name' in extra:
                pyEntity.setUniqueName(extra['name'])
        return pyEntity


class EntitiesFactories(object):
    __slots__ = ('__settings', '__factories', '__eventToAlias', '__aliasToEvent', '__layers')

    def __init__(self, factories):
        super(EntitiesFactories, self).__init__()
        self.__settings = {}
        self.__factories = factories
        self.__eventToAlias = {}
        self.__aliasToEvent = {}
        self.__layers = {}
        for idx, factory in enumerate(self.__factories):
            layers = factory.getManagedLayers()
            for layer in layers:
                self.__layers[layer] = idx

    def initSettings(self, settingsList):
        result = set()
        add = self.addSettings
        for settings in settingsList:
            result.add(add(settings))

        return result

    def clearSettings(self, aliases):
        remove = self.removeSettings
        for alias in aliases:
            remove(alias)

    def addSettings(self, settings):
        layer = settings.layer
        if layer not in self.__layers:
            raise SoftException('Invalid layer in settings {0}'.format(settings))
        factory = self.__factories[self.__layers[layer]]
        factory.validate(settings)
        alias = settings.alias
        eventType = settings.event
        if alias in self.__settings:
            raise SoftException('Alias {0} is already added to settings'.format(alias))
        self.__settings[alias] = settings
        if eventType:
            self.__eventToAlias[eventType] = alias
            self.__aliasToEvent[alias] = eventType
        return alias

    def removeSettings(self, alias):
        if alias in self.__settings:
            settings = self.__settings.pop(alias)
            eventType = settings.event
            if eventType:
                self.__eventToAlias.pop(eventType, None)
                self.__aliasToEvent.pop(alias, None)
        else:
            LOG_ERROR('Settings not found', alias)
        return

    def getSettings(self, alias):
        return self.__settings[alias] if alias in self.__settings else None

    def getAliasByEvent(self, eventType):
        alias = None
        if eventType in self.__eventToAlias:
            alias = self.__eventToAlias[eventType]
        return alias

    def makeLoadEvent(self, loadParams, ctx=None):
        event = None
        if loadParams.viewKey.alias in self.__aliasToEvent:
            event = LoadViewEvent(loadParams, ctx=ctx)
        return event

    def makeShowPopoverEvent(self, loadParams, ctx=None):
        event = None
        if loadParams.viewKey.alias in self.__aliasToEvent:
            event = LoadViewEvent(loadParams, ctx=ctx)
        return event

    def factory(self, alias, *args, **kwargs):
        entity = None
        factoryIdx = -1
        if alias in self.__settings:
            settings = self.__settings[alias]
            factoryIdx = self.__layers[settings.layer]
            factory = self.__factories[factoryIdx]
            entity = factory.create(settings, *args, **kwargs)
        else:
            LOG_ERROR('Settings not found', alias)
        return (entity, factoryIdx)

    def initialize(self, pyEntity, gfxEntity, factoryIdx, extra=None):
        if -1 < factoryIdx < len(self.__factories):
            factory = self.__factories[factoryIdx]
            pyEntity = factory.initialize(pyEntity, gfxEntity, extra=extra)
        else:
            LOG_ERROR('Factory not found, pyEntity is not initialized', factoryIdx, pyEntity)
        return pyEntity
