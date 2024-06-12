# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/resource_well/resource.py
from collections import OrderedDict
import typing
import nations
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from constants import PREMIUM_TYPE, SECONDS_IN_DAY, PREMIUM_ENTITLEMENTS
from gui import NONE_NATION_NAME
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, TooltipData
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.resource_well.resource_well_constants import ResourceType, ServerResourceType
from gui.resource_well.resources_sort import getComparatorByType, getTypeComparator
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.blueprints_requester import makeIntelligenceCD, makeNationalCD, getFragmentNationID
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IResourceWellController
from skeletons.gui.shared import IItemsCache
import account_helpers
import logging
if typing.TYPE_CHECKING:
    from typing import Dict, List, Tuple
_logger = logging.getLogger(__name__)
_INTELLIGENCE_BLUEPRINT = 'intelligence'
_CURRENCY_TOOLTIPS = {Currency.GOLD: TOOLTIPS_CONSTANTS.RESOURCE_WELL_GOLD,
 Currency.CREDITS: TOOLTIPS_CONSTANTS.RESOURCE_WELL_CREDITS,
 Currency.CRYSTAL: TOOLTIPS_CONSTANTS.RESOURCE_WELL_CRYSTAL,
 CURRENCIES_CONSTANTS.FREE_XP: TOOLTIPS_CONSTANTS.RESOURCE_WELL_FREE_XP}

class Resource(object):
    _itemsCache = dependency.descriptor(IItemsCache)

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
    def serverType(self):
        return self.type

    @property
    def serverName(self):
        return self.name

    @property
    def balance(self):
        return self._itemsCache.items.resourceWell.getBalance().get(self.serverType, {}).get(self.serverName, 0)

    def convertToServerCount(self, cnt):
        return cnt

    def convertToGuiCount(self, cnt):
        return cnt


class CurrencyResource(Resource):

    def __init__(self, name, rate, limit):
        super(CurrencyResource, self).__init__(name, rate, limit, ResourceType.CURRENCY.value)

    @property
    def inventoryCount(self):
        return getattr(self._itemsCache.items.stats, self.guiName, 0)

    @property
    def tooltip(self):
        return createTooltipData(isSpecial=True, specialAlias=_CURRENCY_TOOLTIPS.get(self.guiName))


class BlueprintResource(Resource):

    def __init__(self, fragmentCD, name, rate, limit):
        super(BlueprintResource, self).__init__(name, rate, limit, ResourceType.BLUEPRINTS.value)
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

    def __init__(self, fragmentCD, rate, limit):
        super(IntelligenceBlueprintResource, self).__init__(fragmentCD, _INTELLIGENCE_BLUEPRINT, rate, limit)

    @property
    def inventoryCount(self):
        return self._itemsCache.items.blueprints.getIntelligenceCount()

    def _getTooltipSpecialArgs(self):
        return [int(makeIntelligenceCD(self._fragmentCD))]


class NationalBlueprintResource(BlueprintResource):

    def __init__(self, fragmentCD, rate, limit):
        name = self.__getNation(fragmentCD)
        super(NationalBlueprintResource, self).__init__(fragmentCD, name, rate, limit)

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


class TankPremiumDayResource(Resource):

    def __init__(self, rate, limit):
        ratePerDay = rate * SECONDS_IN_DAY
        limitPerDay = limit // SECONDS_IN_DAY
        super(TankPremiumDayResource, self).__init__(PREMIUM_ENTITLEMENTS.PLUS, ratePerDay, limitPerDay, ResourceType.PREMIUMS.value)

    @property
    def inventoryCount(self):
        premiumInfo = self._itemsCache.items.stats.premiumInfo
        expiryUTCTime = premiumInfo.get(PREMIUM_TYPE.PLUS, {}).get('expiryTime', 0)
        delta = account_helpers.getPremiumExpiryDelta(expiryUTCTime)
        return max(delta.days, 0)

    @property
    def tooltip(self):
        return createTooltipData(makeTooltip(header=TOOLTIPS.AWARDITEM_PREMIUM_PLUS_HEADER, body=TOOLTIPS.AWARDITEM_PREMIUM_PLUS_BODY))

    @property
    def serverType(self):
        return ServerResourceType.ENTITLEMENTS.value

    def convertToServerCount(self, cnt):
        return cnt * SECONDS_IN_DAY

    @property
    def balance(self):
        balance = self._itemsCache.items.resourceWell.getBalance()
        balanceInSeconds = balance.get(self.serverType, {}).get(self.serverName, 0)
        return balanceInSeconds // SECONDS_IN_DAY

    def convertToGuiCount(self, cnt):
        return cnt // SECONDS_IN_DAY


def _currencyResourceFactory(resources):
    return [ CurrencyResource(resource.name, resource.rate, resource.limit) for resource in resources if resource.name in Currency.GUI_ALL + (CURRENCIES_CONSTANTS.FREE_XP,) ]


def _blueprintResourceFactory(resources):
    result = []
    for resource in resources:
        fragmentCD = int(resource.name)
        fragmentType = getFragmentType(fragmentCD)
        if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
            result.append(IntelligenceBlueprintResource(fragmentCD, resource.rate, resource.limit))
        if fragmentType == BlueprintTypes.NATIONAL:
            result.append(NationalBlueprintResource(fragmentCD, resource.rate, resource.limit))

    return result


def _entitlementResourceFactory(resources):
    result = []
    for resource in resources:
        if resource.name == PREMIUM_ENTITLEMENTS.PLUS:
            result.append(TankPremiumDayResource(resource.rate, resource.limit))
        _logger.error("ResourceWell: resource type '%s' is not supported", resource.name)

    return result


_RESOURCE_FACTORIES = {ServerResourceType.CURRENCY.value: _currencyResourceFactory,
 ServerResourceType.BLUEPRINTS.value: _blueprintResourceFactory,
 ServerResourceType.ENTITLEMENTS.value: _entitlementResourceFactory}

def processResourcesConfig(resourcesConfig):
    result = {}
    resourceItems = []
    for resourceType, resources in resourcesConfig.iteritems():
        factory = _RESOURCE_FACTORIES.get(resourceType)
        if callable(factory):
            resourceItems += factory(resources.values())

    for resource in resourceItems:
        result.setdefault(resource.type, []).append(resource)

    for resourceType, resources in result.iteritems():
        resources.sort(cmp=getComparatorByType(resourceType))

    return OrderedDict(sorted(result.items(), key=lambda (resType, _): resType, cmp=getTypeComparator()))


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def processLoadingResources(loadingResources, resourceWell=None):
    processedResources = []
    processedConfig = processResourcesConfig(resourceWell.getResources())
    for name, count in loadingResources.iteritems():
        for resources in processedConfig.itervalues():
            resource = findFirst(lambda res, resName=name: res.guiName == resName, resources)
            if resource is not None:
                processedResources.append((resource, count))

    return processedResources


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def mergeResources(splitResources, resourceWell=None):
    mergedResources = []
    resourcesConfig = resourceWell.getResources()
    for resType, resource in splitResources.iteritems():
        for name, count in resource.iteritems():
            resourceConfig = findFirst(lambda config, resName=name: config.name == str(resName), resourcesConfig[resType].values())
            if resourceConfig is not None:
                factory = _RESOURCE_FACTORIES.get(resType)
                if callable(factory):
                    resource = factory([resourceConfig])[0]
                    guiCount = resource.convertToGuiCount(count)
                    mergedResources.append((resource, guiCount))
                else:
                    _logger.error("ResourceWell: resource type '%s' is not supported", resType)

    return mergedResources


def convertResourcesToServerLayout(resources):
    return [ (resource.serverType, resource.serverName, resource.convertToServerCount(count)) for resource, count in resources ]
