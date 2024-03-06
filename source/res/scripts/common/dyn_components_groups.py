# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dyn_components_groups.py
from inspect import getargspec
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

        componentCls.groupComponentReader = ObjParam(**specs)
        componentCls.groupComponentConfig = cached_property(config)
        return componentCls

    return decorator


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
            section = ResMgr.openSection(self._configPath)
            self._groups[groupName] = self._readGroup(section[groupName])
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
            if componentReader:
                config = componentReader.read(componentSection, self._domain)
                initParamsOrder = getargspec(componentClass.__init__).args[1:]
                config.initParams = tuple((getattr(config, paramName) for paramName in initParamsOrder))
            else:
                config = None
            group.append((componentType, config))

        return group
