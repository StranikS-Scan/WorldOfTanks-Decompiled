# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/entitlements_cache.py
import logging
from collections import namedtuple
from functools import partial
import typing
from enum import Enum
import BigWorld
from adisp import adisp_process
from gui.wgcg.agate.contexts import AgateGetInventoryEntitlementsCtx
from helpers import dependency
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, List
_logger = logging.getLogger(__name__)
Entitlement = namedtuple('Entitlement', 'code, tags, amount')
COLLECTIONS_TAG = 'collections'
COLLECTIONS_TAG_PREFIX = 'collections_{}'

class _FilterKeys(Enum):
    CODE = 'code'
    TAG = 'tag'


class _FilterOperators(Enum):
    IN = 'in'
    NOT_IN = 'not_in'
    EQ = 'eq'
    NEQ = 'neq'


_MAX_RETRY_ATTEMPTS = 5
_INITIAL_ATTEMPTS_COUNT = 0
_RETRY_DELAY = 1

class EntitlementsCache(object):
    __slots__ = ('__balanceCache', '__isSyncing', '__pendingEntitlementAttempts', '__isInited', '__retryCallback')
    __web = dependency.descriptor(IWebController)

    def __init__(self):
        self.__balanceCache = {}
        self.__pendingEntitlementAttempts = {}
        self.__isSyncing = False
        self.__isInited = False
        self.__retryCallback = None
        return

    def getBalance(self):
        return self.__balanceCache

    def getCollectionBalance(self, collectionId):
        collectionTag = COLLECTIONS_TAG_PREFIX.format(collectionId)
        return {code:entitlement for code, entitlement in self.__balanceCache.iteritems() if collectionTag in entitlement.tags}

    def updateAll(self, onResponseCallback):
        if not self.__isInited:
            self.__request(self.__createFilterByTags([COLLECTIONS_TAG]), onResponseCallback)

    def update(self, entitlementCode, onResponseCallback):
        if entitlementCode not in self.__balanceCache and entitlementCode not in self.__pendingEntitlementAttempts:
            self.__pendingEntitlementAttempts.update({entitlementCode: _INITIAL_ATTEMPTS_COUNT})
        self.__processPendingEntitlements(onResponseCallback)

    def clear(self):
        self.__balanceCache.clear()
        self.__pendingEntitlementAttempts.clear()
        self.__isSyncing = False
        self.__isInited = False
        if self.__retryCallback is not None:
            BigWorld.cancelCallback(self.__retryCallback)
            self.__retryCallback = None
        return

    @adisp_process
    def __request(self, entitlementsFilter, onResponseCallback):
        if self.__isSyncing:
            onResponseCallback(False, self.__isSyncing)
            return
        else:
            if self.__web.isAvailable():
                try:
                    self.__isSyncing = True
                    response = yield self.__web.sendRequest(ctx=AgateGetInventoryEntitlementsCtx(entitlementsFilter))
                finally:
                    self.__isSyncing = False

                if response.isSuccess():
                    result = response.data.get('balance', [])
                    self.__balanceCache.update({entitlement['code']:self.__createEntitlementFromResponse(entitlement) for entitlement in result if entitlement.get('amount', 0) > 0})
                    self.__clearAbsentEntitlements()
                    for code in self.__balanceCache.iterkeys():
                        self.__pendingEntitlementAttempts.pop(code, None)

                else:
                    _logger.warning('Failed to get entitlements data. Code: %s.', response.getCode())
                if callable(onResponseCallback):
                    onResponseCallback(response.isSuccess(), self.__isSyncing)
            else:
                _logger.warning('Failed to get entitlements data. Web controller is unavailable')
                if callable(onResponseCallback):
                    onResponseCallback(False, self.__isSyncing)
            self.__isInited = True
            return

    def __processPendingEntitlements(self, onResponseCallback):

        def onPendingProcessedCallback(isSuccess, isSyncing):
            if callable(onResponseCallback):
                onResponseCallback(isSuccess, isSyncing)
            if not isSyncing:
                for entitlement in self.__pendingEntitlementAttempts.iterkeys():
                    self.__pendingEntitlementAttempts[entitlement] += 1

            self.__clearPendingEntitlements()
            if self.__pendingEntitlementAttempts:
                self.__retryCallback = BigWorld.callback(_RETRY_DELAY, partial(self.__processPendingEntitlements, onResponseCallback))

        self.__retryCallback = None
        if self.__pendingEntitlementAttempts:
            self.__request(self.__createFilterByTags(self.__getPendingEntitlementTags()), onPendingProcessedCallback)
        return

    def __clearPendingEntitlements(self):
        entitlementsToRemove = [ entitlement for entitlement, attempts in self.__pendingEntitlementAttempts.iteritems() if attempts >= _MAX_RETRY_ATTEMPTS ]
        for entitlement in entitlementsToRemove:
            self.__pendingEntitlementAttempts.pop(entitlement)

        if self.__retryCallback is not None:
            BigWorld.cancelCallback(self.__retryCallback)
            self.__retryCallback = None
        return

    def __createEntitlementFromResponse(self, response):
        return Entitlement(response.get('code', ''), response.get('tags', []), response.get('amount', 0))

    def __createFilterByTags(self, tags):
        tagsFilter = {'key': _FilterKeys.TAG.value,
         'operator': _FilterOperators.IN.value,
         'value': tags}
        return self.__createFilter([tagsFilter])

    def __createFilter(self, filters):
        return {'filter': filters}

    def __getPendingEntitlementTags(self):
        collectionIds = set()
        for code in self.__pendingEntitlementAttempts.iterkeys():
            _, _, collectionId, _ = code.split('_')
            collectionIds.add(collectionId)

        return [ COLLECTIONS_TAG_PREFIX.format(collectionId) for collectionId in collectionIds ]

    def __clearAbsentEntitlements(self):
        entitlementsToRemove = [ code for code, entitlement in self.__balanceCache.iteritems() if entitlement.amount <= 0 ]
        for code in entitlementsToRemove:
            self.__balanceCache.pop(code)
