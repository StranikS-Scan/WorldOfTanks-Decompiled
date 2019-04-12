# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/premium_info.py
from constants import PREMIUM_TYPE

class PremiumInfo(object):

    def __init__(self):
        self._rawPremiumInfo = {p:0 for p in PREMIUM_TYPE.TYPES_SORTED}
        self._rawPremiumInfo['premMask'] = 0

    def update(self, rawPremiumInfo):
        self._rawPremiumInfo.update(rawPremiumInfo)

    def isActivePremium(self, checkPremiumType):
        return self.activePremiumType >= checkPremiumType

    @property
    def isPremium(self):
        return self.activePremiumType != PREMIUM_TYPE.NONE

    @property
    def totalPremiumExpiryTime(self):
        premiumMask = self._rawPremiumInfo['premMask']
        return max(tuple((self._rawPremiumInfo[p] for p in PREMIUM_TYPE.TYPES_SORTED if bool(premiumMask & p))) + (0,))

    @property
    def activePremiumExpiryTime(self):
        activePremiumType = self.activePremiumType
        return self._rawPremiumInfo[activePremiumType] if activePremiumType != PREMIUM_TYPE.NONE else 0

    @property
    def activePremiumType(self):
        return PREMIUM_TYPE.activePremium(self._rawPremiumInfo['premMask'])

    @property
    def data(self):
        premiumMask = self._rawPremiumInfo['premMask']
        return {pType:{'active': bool(premiumMask & pType),
         'expiryTime': self._rawPremiumInfo[pType]} for pType in PREMIUM_TYPE.TYPES_SORTED}
