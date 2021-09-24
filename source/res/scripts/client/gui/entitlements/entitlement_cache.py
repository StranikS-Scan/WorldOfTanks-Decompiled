# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/entitlements/entitlement_cache.py
from helpers import time_utils

class ShopEntitlement(object):
    __slots__ = ('__name', '__amount', '__expiresAt', '__isOnHold')

    def __init__(self, name, amount, expiresAt=None, onHold=False):
        super(ShopEntitlement, self).__init__()
        self.__name = name
        self.__amount = amount
        self.__expiresAt = expiresAt
        self.__isOnHold = onHold

    @property
    def name(self):
        return self.__name

    @property
    def amount(self):
        return self.__amount

    @property
    def expiresAt(self):
        return self.__expiresAt

    @property
    def expiresAtTimestamp(self):
        return time_utils.getTimestampFromISO(self.__expiresAt) if self.__expiresAt is not None else 0

    @property
    def isExpired(self):
        return not self.__isOnHold and self.expiresAtTimestamp <= time_utils.getServerUTCTime()

    @property
    def isOnHold(self):
        return self.__isOnHold

    @classmethod
    def createFromResponseData(cls, data, onHold=False):
        return ShopEntitlement(data.get('code', ''), data.get('amount', 0), expiresAt=data.get('expires_at', None), onHold=onHold)

    def __repr__(self):
        return '<{}(name={}, amount={}, expiresAt={}, onHold={})>'.format(self.__class__.__name__, self.__name, self.__amount, self.__expiresAt, self.__isOnHold)


class ShopEntitlementsCache(object):
    __slots__ = ('__balance', '__onHoldConsumed', '__onHoldGranted')

    def __init__(self, responseData):
        self.__balance, self.__onHoldConsumed, self.__onHoldGranted = self.__parseResponseData(responseData)

    def __parseResponseData(self, responseData):
        balance = self.__getDictFromResponseList(responseData.get('balance', []))
        onHoldConsumed = self.__getDictFromResponseList(responseData.get('on_hold', {}).get('consumed', []), True)
        onHoldGranted = self.__getDictFromResponseList(responseData.get('on_hold', {}).get('granted', []), True)
        return (balance, onHoldConsumed, onHoldGranted)

    def update(self, requestCodes, responseData):
        newBalance, newHoldConsumed, newHoldGranted = self.__parseResponseData(responseData)
        for code in requestCodes:
            self.__updateData(self.__balance, newBalance, code)
            self.__updateData(self.__onHoldConsumed, newHoldConsumed, code)
            self.__updateData(self.__onHoldGranted, newHoldGranted, code)

    def clear(self):
        self.__balance.clear()
        self.__onHoldConsumed.clear()
        self.__onHoldGranted.clear()

    def getEntitlementsBalance(self):
        return [ entitlement for entitlement in self.__balance.values() ]

    def getHoldGrantedEntitlements(self):
        return [ entitlement for entitlement in self.__onHoldGranted.values() ]

    def getHoldConsumedEntitlements(self):
        return [ entitlement for entitlement in self.__onHoldConsumed.values() ]

    def getEntitlementBalance(self, code):
        return self.__balance.get(code, None)

    def getHoldGrantedEntitlement(self, code):
        return self.__onHoldGranted.get(code, None)

    def getHoldConsumedEntitlement(self, code):
        return self.__onHoldConsumed.get(code, None)

    def __getDictFromResponseList(self, responseList, onHold=False):
        return {balanceEntitlement.get('code', ''):ShopEntitlement.createFromResponseData(balanceEntitlement, onHold) for balanceEntitlement in responseList}

    def __updateData(self, old, new, code):
        entitlement = new.get(code, None)
        if entitlement is not None:
            old[code] = entitlement
        else:
            old.pop(code, None)
        return
