# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/wgcg/providers/server_replays_provider.py
from copy import deepcopy
import typing
from server_side_replay.gui.wgcg.providers.base_provider import BaseProvider, RequestSettings, UpdatePeriodType
from server_side_replay.gui.wgcg.data_wrappers.server_replays import DataNames
from server_side_replay.gui.wgcg.providers.example_responses.server_replays import EXAMPLE_DATA
from server_side_replay.gui.wgcg.server_replays import contexts
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Any
    from data_structures import DictObj

class ServerReplaysProvider(BaseProvider):
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def getBestReplays(self, useFake=False, **kwargs):
        return self._getData(DataNames.BEST_REPLAYS, useFake, **kwargs)

    def getTopReplays(self, useFake=False):
        return self._getData(DataNames.TOP_REPLAYS, useFake)

    def getMyReplays(self, useFake=False, **kwargs):
        return self._getData(DataNames.MY_REPLAYS, useFake, account_id=self.__connectionMgr.databaseID, **kwargs)

    def getReplayLink(self, replayID, useFake=False):
        return self._getData(DataNames.REPLAY_LINK, useFake, replayID=replayID)

    def findReplay(self, replayName, useFake=False):
        return self._getData(DataNames.FIND_REPLAY, useFake, replayName=replayName)

    def saveLastShownReplay(self, value):
        self.__lastShownReplay = value

    @property
    def _dataNameContainer(self):
        return DataNames

    @property
    def _isEnabled(self):
        return True

    @property
    def _fakeDataStorage(self):
        return deepcopy(EXAMPLE_DATA)

    def _getSettings(self):
        return {DataNames.BEST_REPLAYS: RequestSettings(contextClazz=contexts.BestReplaysCtx, isCached=False, updatePeriodType=UpdatePeriodType.NONE, updateKwargs=None),
         DataNames.MY_REPLAYS: RequestSettings(contextClazz=contexts.BestReplaysCtx, isCached=False, updatePeriodType=UpdatePeriodType.NONE, updateKwargs=None),
         DataNames.TOP_REPLAYS: RequestSettings(contextClazz=contexts.TopReplaysCtx, isCached=True, updatePeriodType=UpdatePeriodType.AFTER_BATTLE, updateKwargs=None),
         DataNames.REPLAY_LINK: RequestSettings(contextClazz=contexts.ReplayLinkCtx, isCached=False, updatePeriodType=UpdatePeriodType.NONE, updateKwargs=None),
         DataNames.FIND_REPLAY: RequestSettings(contextClazz=contexts.FindReplayCtx, isCached=False, updatePeriodType=UpdatePeriodType.NONE, updateKwargs=None)}
