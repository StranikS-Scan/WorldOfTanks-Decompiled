# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/cache_providers/clan_supply_provider.py
from copy import deepcopy
import typing
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getClanSupplyEnabled
from gui.clans.cache_providers.base_provider import RequestSettings, UpdatePeriodType, BaseProvider
from gui.clans.cache_providers.example_responses.clan_supply import EXAMPLE_DATA
from gui.wgcg.clan_supply import contexts
from gui.clans.data_wrapper.clan_supply import DataNames, QuestStatus, Quest
from gui.wgnc import g_wgncEvents
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from helpers import time_utils
from shared_utils import findFirst, makeTupleByDict
if typing.TYPE_CHECKING:
    from typing import Optional, Dict
    from gui.wgnc import proxy_data
    from gui.clans.data_wrapper import clan_supply

class ClanSupplyProvider(BaseProvider):

    def start(self):
        super(ClanSupplyProvider, self).start()
        g_wgncEvents.onProxyDataItemShowByDefault += self.__onProxyDataItemShow

    def stop(self, withClear=False):
        g_wgncEvents.onProxyDataItemShowByDefault -= self.__onProxyDataItemShow
        super(ClanSupplyProvider, self).stop(withClear=withClear)

    def getProgressionSettings(self, useFake=False):
        return self._getData(DataNames.PROGRESSION_SETTINGS, useFake)

    def getProgressionProgress(self, useFake=False):
        return self._getData(DataNames.PROGRESSION_PROGRESS, useFake)

    def getQuestsInfo(self, useFake=False):
        return self._getData(DataNames.QUESTS_INFO, useFake)

    @property
    def _dataNameContainer(self):
        return DataNames

    @property
    def _isEnabled(self):
        return getClanSupplyEnabled()

    @property
    def _fakeDataStorage(self):
        return deepcopy(EXAMPLE_DATA)

    def _getSettings(self):
        return {DataNames.PROGRESSION_SETTINGS: RequestSettings(context=contexts.ProgressionSettingsCtx(), isCached=True, updatePeriodType=UpdatePeriodType.BY_TIME, updateKwargs={'updateTime': time_utils.HALF_HOUR}),
         DataNames.PROGRESSION_PROGRESS: RequestSettings(context=contexts.ProgressionProgressCtx(), isCached=False, updatePeriodType=UpdatePeriodType.NONE, updateKwargs=None),
         DataNames.QUESTS_INFO: RequestSettings(context=contexts.QuestsInfoCtx(), isCached=False, updatePeriodType=UpdatePeriodType.NONE, updateKwargs=None),
         DataNames.QUESTS_INFO_POST: RequestSettings(context=contexts.PostQuestsInfoCtx(), isCached=False, updatePeriodType=UpdatePeriodType.NONE, updateKwargs=None)}

    def _dataReceived(self, dataName, data):
        if dataName == DataNames.QUESTS_INFO and not data.quests:
            self._requestData(DataNames.QUESTS_INFO_POST)
            return
        self.onDataReceived(dataName, data)

    def __onProxyDataItemShow(self, _, item):
        if item.getType() != WGNC_DATA_PROXY_TYPE.CLAN_SUPPLY_QUEST_UPDATE:
            return
        self._updateDataCache(DataNames.QUESTS_INFO, lambda cachedData: self.__questInfoUpdater(cachedData, item))

    @staticmethod
    def __questInfoUpdater(cachedData, item):
        questForUpdate = findFirst(lambda q: q.name == item.getName(), cachedData.quests)
        if not questForUpdate:
            return False
        if item.getStatus() == QuestStatus.REWARD_PENDING:
            for idx, cachedQuest in enumerate(cachedData.quests):
                if cachedQuest.level > questForUpdate.level or cachedQuest.status == QuestStatus.COMPLETE:
                    continue
                questAsDict = cachedQuest._asdict()
                questAsDict.update({'current_progress': cachedQuest.required_progress,
                 'status': QuestStatus.REWARD_PENDING})
                cachedData.quests[idx] = makeTupleByDict(Quest, questAsDict)

        else:
            questIdx = cachedData.quests.index(questForUpdate)
            questAsDict = questForUpdate._asdict()
            questAsDict.update({'current_progress': item.getProgress(),
             'status': item.getStatus()})
            cachedData.quests[questIdx] = makeTupleByDict(Quest, questAsDict)
        return True
