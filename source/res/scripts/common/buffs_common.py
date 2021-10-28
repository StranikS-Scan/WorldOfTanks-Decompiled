# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/buffs_common.py
import itertools
import ResMgr
from typing import Optional, Any, List
from debug_utils import LOG_ERROR
BUFFS_CONFIG_FILE = 'scripts/item_defs/buffs.xml'

class BuffsRepository(object):
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def init(cls, config_path=BUFFS_CONFIG_FILE):
        repo = cls.getInstance()
        repo._loadFromConfig(config_path)

    @classmethod
    def fini(cls):
        repo = cls.getInstance()
        repo._destroy()

    def __init__(self):
        self._buffsFactories = {}
        self._indexNameMapping = {}

    def _destroy(self):
        self._buffsFactories = {}
        self._indexNameMapping = {}

    def getBuffFactoryByIndex(self, index):
        name = self._indexNameMapping.get(index, None)
        if not name:
            LOG_ERROR('Handled unknown buff index %s', index)
            return
        else:
            return self.getBuffFactoryByName(name)

    def getBuffFactoryByName(self, name):
        return self._buffsFactories.get(name, None)

    def getBuffIndexByBuffName(self, buffName):
        return next((id_ for id_, name in self._indexNameMapping.iteritems() if name == buffName), -1)

    def getBuffNameByIndex(self, index):
        return self._indexNameMapping.get(index)

    def _loadFromConfig(self, config_path):
        xmlSection = ResMgr.openSection(config_path)
        buffIndexCounter = itertools.count()
        for buffName, buffData in xmlSection.items():
            buffIndex = next(buffIndexCounter)
            self._buffsFactories[buffName] = self._buffFactory(buffIndex, buffName, buffData)
            self._indexNameMapping[buffIndex] = buffName

    @property
    def _buffFactory(self):
        raise NotImplementedError


class Buff(object):

    def __init__(self, index, name, components):
        self.index = index
        self.name = name
        self._components = components

    def apply(self, ctx=None):
        for component in self._components:
            component.apply(ctx)

    def unapply(self):
        for component in reversed(self._components):
            component.unapply()


class BuffComponent(object):

    def __init__(self, name, config, owner):
        self._name = name
        self._config = config
        self._owner = owner

    def apply(self, ctx=None):
        pass

    def unapply(self):
        pass


class BuffFactory(object):
    COMPONENT_CONFIG_NAME_FMT = '{}Config'
    COMPONENTS_FACTORIES = {}
    COMPONENTS_CONFIGS = None

    def __init__(self, index, name, configSection):
        self._index = index
        self._name = name
        self._configSection = configSection
        self._componentFactories = self._createComponentFactories()

    def createBuff(self, owner):
        components = [ factory.createComponent(owner) for factory in self._componentFactories ]
        for component in components:
            component._buffName = self._name

        return self._buffClass(self._index, self._name, components)

    @classmethod
    def registerBuffComponent(cls, name, configCls=None):

        def decorator(componentCls):
            configName = cls.COMPONENT_CONFIG_NAME_FMT.format(componentCls.__name__)
            configClass = configCls or getattr(cls.COMPONENTS_CONFIGS, configName)

            class Factory(BuffComponentFactory):
                Config = configClass

                @property
                def _componentClass(self):
                    return componentCls

            cls.COMPONENTS_FACTORIES[name] = Factory
            return componentCls

        return decorator

    def _createComponentFactories(self):
        if self._configSection[self._component] is None:
            return []
        else:
            return [ self._xmlFactories[componentName](componentName, componentData) for componentName, componentData in self._configSection[self._component].items() ]

    @property
    def _buffClass(self):
        raise NotImplementedError

    @property
    def _xmlFactories(self):
        raise NotImplementedError

    @property
    def _component(self):
        raise NotImplementedError


class BuffComponentFactory(object):

    class Config(object):

        def __init__(self, _):
            pass

    def __init__(self, name, configSection):
        self._name = name
        self._config = self.Config(configSection)

    def createComponent(self, owner):
        return self._componentClass(self._name, self._config, owner)

    @property
    def _componentClass(self):
        raise NotImplementedError
