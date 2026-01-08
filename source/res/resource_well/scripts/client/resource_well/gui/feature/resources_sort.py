# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/feature/resources_sort.py
from __future__ import absolute_import
import typing
from gui import GUI_NATIONS, NONE_NATION_NAME
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.shared.money import Currency
from resource_well.gui.feature.constants import ResourceType
_NO_NATION_INDEX = 0
_NATIONS_ORDER = {name:idx for idx, name in enumerate(GUI_NATIONS, 1)}
_NATIONS_ORDER[NONE_NATION_NAME] = _NO_NATION_INDEX
_CURRENCY_ORDER = {name:idx for idx, name in enumerate(Currency.GUI_ALL + (CURRENCIES_CONSTANTS.FREE_XP,))}
_RESOURCE_TYPE_ORDER = (ResourceType.CURRENCY, ResourceType.BLUEPRINTS)

def sortCurrencyResource(resource):
    return _CURRENCY_ORDER.get(resource.guiName, len(_CURRENCY_ORDER))


def sortBlueprintsResource(resource):
    return _NATIONS_ORDER.get(resource.nation, len(_NATIONS_ORDER))


_RESOURCE_SORTERS = {ResourceType.BLUEPRINTS: sortBlueprintsResource,
 ResourceType.CURRENCY: sortCurrencyResource}

def getSorterByResourceType(resourceType):
    return _RESOURCE_SORTERS.get(resourceType)


def sortAnyResource(resource):
    resourceType = ResourceType.getMember(resource.type)
    sorter = getSorterByResourceType(resourceType)
    return (sortByResourceType(resourceType), sorter(resource)) if resourceType and sorter else (0, 0)


def sortByResourceType(resourceType):
    return _RESOURCE_TYPE_ORDER.index(resourceType) if resourceType in _RESOURCE_TYPE_ORDER else len(_RESOURCE_TYPE_ORDER)
