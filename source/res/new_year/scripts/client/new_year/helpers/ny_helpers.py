# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/helpers/ny_helpers.py
from dependency_injection_container import replace_none_kwargs
from skeletons.gui.shared import IItemsCache
from new_year.helpers.server_settings import getNewYearObjectsConfig
from new_year_common.items.components.ny_constants import TOKEN_VARIADIC_DISCOUNT_PREFIX

def _getVariadicID(vCD):
    return TOKEN_VARIADIC_DISCOUNT_PREFIX + ':' + str(vCD)


@replace_none_kwargs(itemsCache=IItemsCache)
def getCurrentObjectLevel(objectName, itemsCache=None):
    config = getNewYearObjectsConfig()
    currentLevel = itemsCache.items.tokens.getTokenCount(config.getObjectToken(objectName))
    return currentLevel
