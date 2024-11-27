# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/common/new_year_common/machine_config.py
from new_year_common.settings import MachineConsts

class MachineConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config=None):
        self._config = config or {}

    def isEnabled(self):
        return self._config.get(MachineConsts.ENABLED, False)

    def getLootboxID(self):
        return self._config.get(MachineConsts.COIN_LOOTBOX_ID)

    def getCoinPrice(self):
        return self._config.get(MachineConsts.COIN_PRICE)
