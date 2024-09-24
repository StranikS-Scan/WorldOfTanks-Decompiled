# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dyn_components_groups.py
from inspect import getargspec
from functools import partial
from cache import cached_property
from constants import IS_CELLAPP, IS_DEVELOPMENT
from extension_utils import importClass, ResMgr
from soft_exception import SoftException
from xml_config_specs import ObjParam
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Any
    from ResMgr import DataSection

def groupComponent(**specs):

    def decorator(componentCls):

        def config(self):
            parts = self.keyName.split('__')
            if len(parts) == 2:
                groupName, idx = parts
                return DynComponentsGroupsRepo.getGroup(groupName)[int(idx)][1]
            else:
                return None

        allSpecs = {}
        for base in componentCls.__bases__:
            baseReader = getattr(base, 'groupComponentReader', None)
            if isinstance(baseReader, ObjParam):
                allSpecs.update(baseReader._specs)

        allSpecs.update(specs)
        componentCls.groupComponentReader = ObjParam(**allSpecs)
        componentCls.groupComponentConfig = cached_property(config)
        return componentCls

    return decorator


class _UnregisteredComponentConfig(object):
    pass


class DynComponentsGroupsRepo(object):
    _CONFIG = 'scripts/item_defs/dyn_components_groups.xml'
    _DOMAIN = 'server' if IS_CELLAPP else 'client'
    _RELOAD = IS_DEVELOPMENT
    _reader = None

    @classmethod
    def init(cls):
        cls._reader = DynComponentsGroupsReader(cls._CONFIG, cls._DOMAIN, hotReload=cls._RELOAD)

    @classmethod
    def getGroup(cls, groupName):
        return cls._reader.getGroup(groupName)


class DynComponentsGroupsReader(object):

    def __init__(self, configPath, domain='', hotReload=False):
        self._configPath = configPath
        self._domain = domain
        self._hotReload = hotReload
        section = ResMgr.openSection(configPath)
        self._groups = self._readGroups(section)

    def getGroup(self, groupName):
        if self._hotReload:
            groupSection = ResMgr.openSection(self._configPath)[groupName]
            if groupSection:
                self._groups[groupName] = self._readGroup(groupSection)
        if groupName not in self._groups:
            raise SoftException('No dynamic components group "(%s)" found!' % groupName)
        return self._groups.get(groupName, [])

    def _readGroups(self, section):
        groups = {}
        for groupName, groupSection in section.items():
            if groupName.startswith('xmlns:'):
                continue
            if groupName in groups:
                raise SoftException('Duplicated dynamic components group "(%s)" in xml config!' % groupName)
            groups[groupName] = self._readGroup(groupSection)

        return groups

    def _readGroup(self, section):
        group = []
        for componentType, componentSection in section.items():
            componentClass = importClass(componentType, componentType)
            componentReader = getattr(componentClass, 'groupComponentReader', None)
            config = componentReader.read(componentSection, self._domain) if componentReader else _UnregisteredComponentConfig()
            config.createInitParams = partial(self._createInitParams, componentClass)
            group.append((componentType, config))

        return group

    @classmethod
    def _createInitParams(cls, compCls, cfg, kwargs):
        spec = getargspec(compCls.__init__)
        specDefaults = spec.defaults or ()
        initParamsDefaults = dict(zip(spec.args[-len(specDefaults):], specDefaults))
        initParamsOrder = spec.args[1:]
        result = tuple((cls._getParam(paramName, cfg, kwargs, initParamsDefaults) for paramName in initParamsOrder))
        return result

    @staticmethod
    def _getParam(paramName, cfg, kwargs, defaults):
        if paramName == 'ctx':
            return kwargs
        else:
            for value in (kwargs.get(paramName), getattr(cfg, paramName, None), defaults.get(paramName)):
                if value is not None:
                    return value

            return
