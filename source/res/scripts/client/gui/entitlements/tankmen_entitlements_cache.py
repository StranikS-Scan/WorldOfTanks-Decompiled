# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/entitlements/tankmen_entitlements_cache.py
import BigWorld
import logging
from collections import namedtuple
import typing
from enum import Enum
from adisp import adisp_process
from functools import partial
from gui.wgcg.agate.contexts import AgateGetInventoryEntitlementsCtx
from helpers import dependency
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, List
_logger = logging.getLogger(__name__)
Entitlement = namedtuple('Entitlement', 'code, tags, amount')

class _FilterKeys(Enum):
    CODE = 'code'
    TAG = 'tag'


class _FilterOperators(Enum):
    IN = 'in'
    NOT_IN = 'not_in'
    EQ = 'eq'
    NEQ = 'neq'


_DELAY = 1

class TankmenEntitlementsCache(object):
    __slots__ = ('__balanceCache', '__isSyncing')
    __web = dependency.descriptor(IWebController)

    def __init__(self):
        self.__balanceCache = {}
        self.__isSyncing = False

    def getBalance(self):
        return self.__balanceCache

    def update(self, entitlementsFilter, onResponseCallback):
        self.__request(self.__createFilterByTags([entitlementsFilter]), onResponseCallback)

    def updateWithDelay(self, filter, onResponseCallback):
        BigWorld.callback(_DELAY, partial(self.__request, self.__createFilterByTags([filter]), onResponseCallback))

    def clear(self):
        self.__balanceCache.clear()
        self.__isSyncing = False

    @adisp_process
    def __request(self, entitlementsFilter, onResponseCallback):
        if self.__isSyncing:
            onResponseCallback(False, self.__isSyncing)
            return
        if self.__web.isAvailable():
            try:
                self.__isSyncing = True
                response = yield self.__web.sendRequest(ctx=AgateGetInventoryEntitlementsCtx(entitlementsFilter))
            finally:
                self.__isSyncing = False

            if response.isSuccess():
                result = response.data.get('balance', [])
                self.__balanceCache.update({entitlement['code']:self.__createEntitlementFromResponse(entitlement) for entitlement in result})
            else:
                _logger.warning('Failed to get entitlements data. Code: %s.', response.getCode())
            if callable(onResponseCallback):
                onResponseCallback(response.isSuccess(), self.__isSyncing)
        else:
            _logger.warning('Failed to get entitlements data. Web controller is unavailable')
            if callable(onResponseCallback):
                onResponseCallback(False, self.__isSyncing)

    def __createEntitlementFromResponse(self, response):
        return Entitlement(response.get('code', ''), response.get('tags', []), response.get('amount', 0))

    def __createFilterByTags(self, tags):
        tagsFilter = {'key': _FilterKeys.TAG.value,
         'operator': _FilterOperators.IN.value,
         'value': tags}
        return self.__createFilter([tagsFilter])

    def __createFilter(self, filters):
        return {'filter': filters}
