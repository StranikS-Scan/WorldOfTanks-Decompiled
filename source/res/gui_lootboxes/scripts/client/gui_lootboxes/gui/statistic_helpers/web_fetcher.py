# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/statistic_helpers/web_fetcher.py
import logging
from adisp import adisp_async, adisp_process
from gui.clientgw.statbox.contexts import StatBoxGetInfoCtx
from gui_lootboxes.gui.statistic_helpers.statistic_data_provider import LootBoxStatFetcher
from gui_lootboxes.skeletons.statistic_lootbox_controller import IStatisticLootBoxController
from helpers import dependency
from lootboxes_common import unpackLootboxStatistic
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)

class LBWebFetcher(LootBoxStatFetcher):
    __webController = dependency.descriptor(IWebController)
    __guiLootBoxesStatisticCtrl = dependency.descriptor(IStatisticLootBoxController)

    def onAccountBecomePlayer(self):
        pass

    def onAccountBecomeNonPlayer(self):
        pass

    def onServerSettingsChanged(self, diff):
        pass

    @adisp_process
    def requestData(self, callback):
        result = yield self._request()
        callback(result)

    def processResult(self, data):
        if data:
            result = {}
            for lbID, statData in data.iteritems():
                expires, ver, stat = statData
                if ver <= self.__guiLootBoxesStatisticCtrl.getLootBoxesVersionInfo(lbID):
                    continue
                try:
                    unpackData = unpackLootboxStatistic(stat)
                except Exception:
                    _logger.exception('Fail to unpack statistics for LootBox: %s', lbID)
                    continue

                result[int(lbID)] = (expires, ver, unpackData)

            self._storage.fillCache(result)

    @adisp_async
    @adisp_process
    def _request(self, callback=None):
        requestCtx = StatBoxGetInfoCtx()
        result = yield self.__webController.sendRequest(ctx=requestCtx)
        callback(result.data if result.isSuccess() else {})
