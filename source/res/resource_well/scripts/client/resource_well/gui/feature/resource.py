# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/feature/resource.py
from __future__ import absolute_import
from collections import OrderedDict
import typing
from future.builtins import str
from future.utils import itervalues, iteritems
import nations
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from gui import NONE_NATION_NAME
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, TooltipData
from gui.shared.money import Currency
from gui.shared.utils.requesters.blueprints_requester import makeIntelligenceCD, makeNationalCD, getFragmentNationID
from helpers import dependency
from resource_well.gui.feature.constants import ResourceType
from resource_well.gui.feature.resources_sort import sortByResourceType, getSorterByResourceType
from shared_utils import findFirst
from skeletons.gui.resource_well import IResourceWellController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, List, Tuple
_INTELLIGENCE_BLUEPRINT = 'intelligence'
_CURRENCY_TOOLTIPS = {Currency.GOLD: TOOLTIPS_CONSTANTS.GOLD_INFO_SIMPLE,
 Currency.CREDITS: TOOLTIPS_CONSTANTS.CREDITS_INFO_SIMPLE,
 Currency.CRYSTAL: TOOLTIPS_CONSTANTS.CRYSTAL_INFO_SIMPLE,
 CURRENCIES_CONSTANTS.FREE_XP: TOOLTIPS_CONSTANTS.FREEXP_INFO_SIMPLE}

class Resource(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    _resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, name, rate, limit, resourceType):
        self._name = name
        self._rate = rate
        self._limit = limit
        self._type = resourceType

    @property
    def inventoryCount(self):
        raise NotImplementedError

    @property
    def tooltip(self):
        return createTooltipData()

    @property
    def name(self):
        return self._name

    @property
    def rate(self):
        return self._rate

    @property
    def limit(self):
        return self._limit

    @property
    def type(self):
        return self._type

    @property
    def guiName(self):
        return self._name

    @property
    def balance(self):
        return self._resourceWell.getBalance().get(self.type, {}).get(self.name, 0)


class CurrencyResource(Resource):

    @property
    def inventoryCount(self):
        return getattr(self._itemsCache.items.stats, self.guiName, 0)

    @property
    def tooltip(self):
        return createTooltipData(isSpecial=True, specialAlias=_CURRENCY_TOOLTIPS.get(self.guiName))


class BlueprintResource(Resource):

    def __init__(self, fragmentCD, name, rate, limit, resourceType):
        super(BlueprintResource, self).__init__(name, rate, limit, resourceType)
        self._fragmentCD = fragmentCD

    @property
    def inventoryCount(self):
        raise NotImplementedError

    @property
    def tooltip(self):
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO, specialArgs=self._getTooltipSpecialArgs())

    @property
    def nation(self):
        return NONE_NATION_NAME

    @property
    def name(self):
        return int(self._fragmentCD)

    def _getTooltipSpecialArgs(self):
        return []


class IntelligenceBlueprintResource(BlueprintResource):

    def __init__(self, fragmentCD, rate, limit, resourceType):
        super(IntelligenceBlueprintResource, self).__init__(fragmentCD, _INTELLIGENCE_BLUEPRINT, rate, limit, resourceType)

    @property
    def inventoryCount(self):
        return self._itemsCache.items.blueprints.getIntelligenceCount()

    def _getTooltipSpecialArgs(self):
        return [int(makeIntelligenceCD(self._fragmentCD))]


class NationalBlueprintResource(BlueprintResource):

    def __init__(self, fragmentCD, rate, limit, resourceType):
        name = self.__getNation(fragmentCD)
        super(NationalBlueprintResource, self).__init__(fragmentCD, name, rate, limit, resourceType)

    @property
    def inventoryCount(self):
        return self._itemsCache.items.blueprints.getNationalFragments(self._fragmentCD)

    @property
    def nation(self):
        return self.__getNation(self._fragmentCD)

    def _getTooltipSpecialArgs(self):
        return [int(makeNationalCD(self._fragmentCD))]

    @staticmethod
    def __getNation(fragmentCD):
        return nations.MAP.get(getFragmentNationID(fragmentCD), nations.NONE_INDEX)


def _currencyResourceFactory(resources):
    return [ CurrencyResource(resource.name, resource.rate, resource.limit, ResourceType.CURRENCY.value) for resource in resources if resource.name in Currency.GUI_ALL + (CURRENCIES_CONSTANTS.FREE_XP,) ]


def _blueprintResourceFactory(resources):
    result = []
    for resource in resources:
        fragmentCD = int(resource.name)
        fragmentType = getFragmentType(fragmentCD)
        if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
            result.append(IntelligenceBlueprintResource(fragmentCD, resource.rate, resource.limit, ResourceType.BLUEPRINTS.value))
        if fragmentType == BlueprintTypes.NATIONAL:
            result.append(NationalBlueprintResource(fragmentCD, resource.rate, resource.limit, ResourceType.BLUEPRINTS.value))

    return result


_RESOURCE_FACTORIES = {ResourceType.CURRENCY: _currencyResourceFactory,
 ResourceType.BLUEPRINTS: _blueprintResourceFactory}

def processResourcesConfig(resourcesConfig):
    result = {}
    for resourceTypeStr, resources in resourcesConfig.items():
        resourceType = ResourceType.getMember(resourceTypeStr)
        factory = _RESOURCE_FACTORIES.get(resourceType)
        sorter = getSorterByResourceType(resourceType)
        if resourceType and factory and sorter:
            result[resourceType] = sorted(factory(itervalues(resources)), key=sorter)

    return OrderedDict(sorted(iteritems(result), key=lambda x: sortByResourceType(x[0])))


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def processLoadingResources(rewardID, loadingResources, resourceWell=None):
    processedResources = []
    processedConfig = processResourcesConfig(resourceWell.config.getRewardConfig(rewardID).resources)
    for name, count in iteritems(loadingResources):
        for resources in itervalues(processedConfig):
            resource = findFirst(lambda res, resName=name: res.guiName == resName, resources)
            if resource is not None:
                processedResources.append((resource, count))

    return processedResources


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def mergeResources(splitResources, rewardID, resourceWell=None):
    mergedResources = []
    resourcesConfig = resourceWell.config.getRewardConfig(rewardID).resources
    for resType, resource in iteritems(splitResources):
        for name, count in iteritems(resource):
            resourceConfig = findFirst(lambda config, resName=name: config.name == str(resName), itervalues(resourcesConfig[resType]))
            if resourceConfig is not None:
                factory = _RESOURCE_FACTORIES.get(ResourceType.getMember(resType))
                if callable(factory):
                    mergedResources.append((factory([resourceConfig])[0], count))

    return mergedResources


def splitResourcesByType(resources):
    return [ (resource.type, resource.name, count) for resource, count in resources ]
