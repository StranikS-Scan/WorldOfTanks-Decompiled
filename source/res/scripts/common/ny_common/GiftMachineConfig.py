# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/GiftMachineConfig.py
from typing import Optional, Dict, Callable
from ny_common.settings import GiftMachineConsts

class GiftMachineConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getCoinID(self):
        return self._config.get(GiftMachineConsts.GIFT_MACHINE_COIN_ID)

    def getCoinPrice(self):
        return self._config.get(GiftMachineConsts.GIFT_MACHINE_COIN_PRICE, 0)

    def getCoinType(self):
        return self._config.get(GiftMachineConsts.GIFT_MACHINE_COIN_TYPE, '')

    def getDependencies(self):
        return self._config.get(GiftMachineConsts.GIFT_MACHINE_DEPENDENCIES, {})

    def checkDependencies(self, currenctLevel, tokensCountGetter):
        for dependencyName, dependencyValue in self.getDependencies().iteritems():
            if dependencyName == GiftMachineConsts.LEVEL_DEPENDENCY:
                if currenctLevel < dependencyValue:
                    return False
            if dependencyName == GiftMachineConsts.TOKENS_DEPENDENCY:
                if any((tokensCountGetter(tokenID) < tokenCount for tokenID, tokenCount in dependencyValue.iteritems())):
                    return False

        return True
