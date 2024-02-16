# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/resource_well/resources_sort.py
from gui import GUI_NATIONS, NONE_NATION_NAME
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.resource_well.resource_well_constants import ResourceType
from gui.shared.money import Currency
_NO_NATION_INDEX = 0
_NATIONS_ORDER = {name:idx for idx, name in enumerate(GUI_NATIONS, 1)}
_NATIONS_ORDER[NONE_NATION_NAME] = _NO_NATION_INDEX
_CURRENCY_ORDER = {name:idx for idx, name in enumerate(Currency.GUI_ALL + (CURRENCIES_CONSTANTS.FREE_XP,))}
_RESOURCE_TYPE_ORDER = {name:idx for idx, name in enumerate((ResourceType.CURRENCY, ResourceType.BLUEPRINTS, ResourceType.PREMIUMS))}

def _nationComparator(first, second):
    return cmp(_NATIONS_ORDER.get(first.nation), _NATIONS_ORDER.get(second.nation))


def _currencyComparator(first, second):
    return cmp(_CURRENCY_ORDER.get(first.guiName), _CURRENCY_ORDER.get(second.guiName))


def _defaultComparator(first, second):
    return cmp(first[0], second[0])


def _resourceTypeComparator(first, second):
    return cmp(_RESOURCE_TYPE_ORDER.get(ResourceType.getMember(first)), _RESOURCE_TYPE_ORDER.get(ResourceType.getMember(second)))


def _resourceComparator(first, second):
    typeComparator = cmp(_RESOURCE_TYPE_ORDER.get(ResourceType.getMember(first.type)), _RESOURCE_TYPE_ORDER.get(ResourceType.getMember(second.type)))
    return typeComparator or first.type == ResourceType.BLUEPRINTS.value and _nationComparator(first, second) or first.type == ResourceType.CURRENCY.value and _currencyComparator(first, second) or _defaultComparator(first, second)


_RESOURCE_COMPARATORS = {ResourceType.BLUEPRINTS: _nationComparator,
 ResourceType.CURRENCY: _currencyComparator}

def getComparatorByType(resourceType):
    return _RESOURCE_COMPARATORS.get(ResourceType(resourceType), _defaultComparator)


def getTypeComparator():
    return _resourceTypeComparator


def getResourceComparator():
    return _resourceComparator
