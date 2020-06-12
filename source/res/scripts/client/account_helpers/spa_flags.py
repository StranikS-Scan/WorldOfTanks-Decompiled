# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/spa_flags.py
from external_strings_utils import strtobool, InvalidStringValueException
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from constants import SPA_ATTRS

class SPAFlags(object):

    def __init__(self, syncData):
        super(SPAFlags, self).__init__()
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, diff):
        cacheDiff = diff.get('cache', None)
        spaCache = cacheDiff.get('SPA', None) if cacheDiff else None
        itemDiff = {}
        if spaCache:
            for key in SPA_ATTRS.toClientAttrs():
                value = spaCache.get(key, None)
                if value:
                    try:
                        itemDiff[key] = strtobool(value)
                    except InvalidStringValueException:
                        itemDiff[key] = value

        synchronizeDicts(itemDiff, self.__cache.setdefault('spaFlags', {}))
        return

    def getFlag(self, flagName):
        return self.__cache['spaFlags'].get(flagName, None) if self.__cache and 'spaFlags' in self.__cache else None
