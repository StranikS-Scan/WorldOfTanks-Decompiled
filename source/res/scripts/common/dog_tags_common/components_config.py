# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/components_config.py
import itertools
from collections import defaultdict
import typing
from enum import Enum
from cache import cached_property
from dog_tags_common.config.common import ComponentPurpose
from dog_tags_common.config.dog_tag_parser import readDogTags
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import List, Optional
    from dog_tags_common.config.dog_tag_framework import ComponentDefinition, StartingComponents

class SourceData(Enum):
    ALL = 0
    DEPRECATED_ONLY = 1
    NON_DEPRECATED_ONLY = 2


class DictIterator(object):

    def __init__(self, *dicts):
        self._dicts = dicts

    @cached_property
    def _dict(self):
        return dict(self.iteritems())

    def iteritems(self):
        return itertools.chain(*[ d.iteritems() for d in self._dicts ])

    def itervalues(self):
        return itertools.chain(*[ d.itervalues() for d in self._dicts ])

    def iterkeys(self):
        return itertools.chain(*[ d.iterkeys() for d in self._dicts ])

    def items(self):
        return self._dict.items()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def __getitem__(self, item):
        return self._dict[item]

    def get(self, item, default=None):
        return self._dict.get(item, default)

    def __repr__(self):
        return self._dicts.__repr__()

    def __iter__(self):
        return self.iterkeys()


class _ComponentConfigAdapter(object):

    def __init__(self):
        self._startingDogTag, components = readDogTags()
        self._createAllCache(components)
        self._createGroupByTypeCache(components)
        self._createIsDefaultCache(components)
        self._createDefaultAnimatedDogTag(components)

    def _createAllCache(self, components):
        self._components = dict(((c.componentId, c) for c in components if not c.isDeprecated and not c.isHidden))
        self._components_d = dict(((c.componentId, c) for c in components if c.isDeprecated and not c.isHidden))

    def _createIsDefaultCache(self, components):
        self._defaults = dict(((c.componentId, c) for c in components if c.isDefault and not c.isDeprecated and not c.isHidden))
        self._defaults_d = dict(((c.componentId, c) for c in components if c.isDefault and c.isDeprecated and not c.isHidden))

    def _createGroupByTypeCache(self, components):
        self._types = defaultdict(dict)
        self._types_d = defaultdict(dict)
        for component in components:
            if component.isHidden:
                continue
            if component.isDeprecated:
                self._types_d[component.purpose][component.componentId] = component
            self._types[component.purpose][component.componentId] = component

    def _createDefaultAnimatedDogTag(self, components):
        firstAnimatedDogTag = next((c for c in components if not c.isHidden and c.purpose == ComponentPurpose.COUPLED))
        self._defaultAnimatedDogTag = [firstAnimatedDogTag.componentId, firstAnimatedDogTag.coupledComponentId]

    def getDefaultDogTag(self):
        return self._startingDogTag

    def getDefaultAnimatedDogTag(self):
        return self._defaultAnimatedDogTag

    def getComponentById(self, id_val, sourceData=SourceData.ALL):
        depr = None
        if sourceData != SourceData.NON_DEPRECATED_ONLY:
            depr = self._components_d.get(id_val, None)
            if sourceData == SourceData.DEPRECATED_ONLY:
                return depr
        return self._components.get(id_val, None) if depr is None else depr

    def getAllComponents(self, sourceData=SourceData.ALL):
        if sourceData == SourceData.NON_DEPRECATED_ONLY:
            return DictIterator(self._components)
        if sourceData == SourceData.DEPRECATED_ONLY:
            return DictIterator(self._components_d)
        if sourceData == SourceData.ALL:
            return DictIterator(self._components, self._components_d)
        raise SoftException('Unexpected sourceData type')

    def exists(self, compId):
        return compId in self._components or compId in self._components_d

    def getDefaultComponents(self, sourceData=SourceData.ALL):
        if sourceData == SourceData.NON_DEPRECATED_ONLY:
            return DictIterator(self._defaults)
        if sourceData == SourceData.DEPRECATED_ONLY:
            return DictIterator(self._defaults_d)
        if sourceData == SourceData.ALL:
            return DictIterator(self._defaults_d, self._defaults)
        raise SoftException('Unexpected sourceData type')

    def getComponentsByPurpose(self, purpose, sourceData=SourceData.ALL):
        if sourceData == SourceData.DEPRECATED_ONLY:
            return DictIterator(self._types_d.get(purpose, {}))
        if sourceData == SourceData.NON_DEPRECATED_ONLY:
            return DictIterator(self._types.get(purpose, {}))
        if sourceData == SourceData.ALL:
            return DictIterator(self._types_d.get(purpose, {}), self._types.get(purpose, {}))
        raise SoftException('Unexpected sourceData type')


componentConfigAdapter = _ComponentConfigAdapter()
