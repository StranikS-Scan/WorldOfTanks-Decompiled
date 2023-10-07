# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/buffs_common.py
import enum
import itertools
import ResMgr
from items.artefacts import VehicleFactorsXmlReader
from items import _xml
from typing import Optional, Any, List
from debug_utils import LOG_ERROR
import sys
from halloween_common.items.hw_artefacts import getVisualEffects
BUFFS_CONFIG_FILE = 'halloween/scripts/item_defs/buffs.xml'

class BuffComponentVisibilityMode(enum.IntEnum):
    NONE = 0
    SELF = 1
    OTHERS = 2
    ALL = 3


class BuffTarget(enum.IntEnum):
    VICTIM = 0
    ATTACKER = 1


class BuffsRepository(object):
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def init(cls, configPath=BUFFS_CONFIG_FILE):
        repo = cls.getInstance()
        repo._loadFromConfig(configPath)

    @classmethod
    def fini(cls):
        repo = cls.getInstance()
        repo._destroy()

    def __init__(self):
        self._buffsFactories = {}
        self._indexNameMapping = {}
        self._specialBuffs = {}
        self._specialBuffsIndexNameMapping = {}

    def _destroy(self):
        self._buffsFactories = {}
        self._indexNameMapping = {}
        self._specialBuffs = {}
        self._specialBuffsIndexNameMapping = {}

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

    def getSpecialBuffs(self, buffName=None):
        if buffName is not None:
            buff = self._specialBuffs.get(buffName)
            if buff is not None:
                return [buff]
            return
        else:
            return list(self._specialBuffs.values()) if self._specialBuffs else None

    def getSpecialBuffById(self, buffID):
        buffName = self._specialBuffsIndexNameMapping.get(buffID, '')
        return self._specialBuffs.get(buffName)

    def _loadFromConfig(self, configPath):
        xmlSection = ResMgr.openSection(configPath)
        if xmlSection is None:
            return
        else:
            buffIndexCounter = itertools.count()
            for buffName, buffData in xmlSection.items():
                isSpecial = buffName.startswith('special_')
                if isSpecial:
                    clazzName = buffName[len('special_'):]
                    clazz = getattr(sys.modules[__name__], clazzName, None)
                    if clazz is not None:
                        buff = clazz()
                        buff.readConfig(xmlSection, buffData)
                        self._specialBuffs[buff.name] = buff
                        self._specialBuffsIndexNameMapping[buff.id] = buff.name
                buffIndex = next(buffIndexCounter)
                self._buffsFactories[buffName] = self._buffFactory(buffIndex, buffName, buffData)
                self._indexNameMapping[buffIndex] = buffName

            return

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

    @property
    def componentFactories(self):
        return self._componentFactories

    def createBuff(self, owner):
        components = [ factory.createComponent(owner) for factory in self._componentFactories ]
        for component in components:
            component._buffName = self._name

        return self._buffClass(self._index, self._name, components)

    def getComponentFactoriesByName(self, componentName):
        return [ factory for factory in self.componentFactories if factory.name == componentName ]

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

    @property
    def name(self):
        return self._name

    @property
    def config(self):
        return self._config

    def createComponent(self, owner):
        return self._componentClass(self._name, self._config, owner)

    @property
    def _componentClass(self):
        raise NotImplementedError


class HWGettingFatApple(object):
    __slots__ = ('id', 'name', 'componentName', 'increaseMaxHealth', 'maxHealth', 'factors', 'minValueFactors', 'effects')

    def __init__(self):
        self.id = 0
        self.name = ''
        self.componentName = ''
        self.increaseMaxHealth = 0
        self.maxHealth = 0
        self.factors = {}
        self.minValueFactors = {}
        self.effects = {}

    def readConfig(self, xmlCtx, section):
        self.id = _xml.readInt(xmlCtx, section, 'id')
        self.name = _xml.readStringOrEmpty(xmlCtx, section, 'name')
        self.componentName = _xml.readStringOrEmpty(xmlCtx, section, 'componentName')
        self.increaseMaxHealth = _xml.readFloat(xmlCtx, section, 'increaseMaxHealth', 1)
        self.maxHealth = _xml.readInt(xmlCtx, section, 'maxHealth', 1)
        self.factors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'factors')
        self.minValueFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'minValueFactors')
        self.effects = getVisualEffects(xmlCtx, section)
