# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/balance_content_with_ny_shards.py
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent
from helpers import dependency
from new_year.ny_constants import SyncDataKeys
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_CURRENCY_SHARDS = 'shards'

class BalanceContentWithShards(CommonBalanceContent):
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)

    def _initialize(self, *args, **kwargs):
        self._addCurrency(_CURRENCY_SHARDS, self.gui.systemLocale.getNumberFormat(self.__getShardsCount()))
        super(BalanceContentWithShards, self)._initialize(*args, **kwargs)
        self.__nyController.onDataUpdated += self.__onDataUpdated

    def _finalize(self):
        super(BalanceContentWithShards, self)._finalize()
        self.__nyController.onDataUpdated -= self.__onDataUpdated

    def __onDataUpdated(self, keys):
        fragmentsChanged = SyncDataKeys.TOY_FRAGMENTS in keys
        if fragmentsChanged:
            self._onCurrencyUpdated(_CURRENCY_SHARDS, self.__getShardsCount())

    def __getShardsCount(self):
        return self.__itemsCache.items.festivity.getShardsCount()
