# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/session_stats_presenter.py
from __future__ import absolute_import
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
from gui.impl.gen.view_models.views.lobby.page.footer.session_stats_model import SessionStatsModel
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class SessionStatsPresenter(ViewComponent[SessionStatsModel], IGlobalListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(SessionStatsPresenter, self).__init__(model=SessionStatsModel)
        self._supportedModes = tuple()

    def onPrbEntitySwitched(self):
        super(SessionStatsPresenter, self).onPrbEntitySwitched()
        self.__updateSessionStats()

    def _onLoading(self, *args, **kwargs):
        super(SessionStatsPresenter, self)._onLoading(*args, **kwargs)
        self._supportedModes = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.MAPBOX)
        self.__updateSessionStats()

    def _onLoaded(self, *args, **kwargs):
        self.startGlobalListening()
        super(SessionStatsPresenter, self)._onLoaded(*args, **kwargs)

    def _getEvents(self):
        return ((self.__itemsCache.onSyncCompleted, self.__onCacheResync), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingChanged))

    def _finalize(self):
        super(SessionStatsPresenter, self)._finalize()
        self.stopGlobalListening()

    def __onCacheResync(self, reason, _):
        if reason not in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            return
        self.__updateBattleCount(self.getViewModel())

    def __onServerSettingChanged(self, diff):
        if 'sessionStats' in diff or ('sessionStats', '_r') in diff:
            self.__updateSessionStats()

    def __updateSessionStats(self):
        with self.getViewModel().transaction() as model:
            sessionStatsEnabled = self.__lobbyContext.getServerSettings().isSessionStatsEnabled()
            model.setSessionStatsEnabled(sessionStatsEnabled)
            if self.prbDispatcher is not None:
                queueType = self.prbDispatcher.getEntity().getQueueType()
                isInSupportedMode = queueType in self._supportedModes
            else:
                isInSupportedMode = False
            enabled = isInSupportedMode and sessionStatsEnabled
            model.setEnabled(enabled)
            state = self.prbDispatcher.getFunctionalState()
            winback = state.isInPreQueue() and state.entityTypeID == QUEUE_TYPE.WINBACK
            model.setWinback(winback)
            self.__updateBattleCount(model)
        return

    def __updateBattleCount(self, model):
        battleCount = self.__itemsCache.items.sessionStats.getAccountStats(ARENA_BONUS_TYPE.REGULAR).battleCnt
        if battleCount is not None:
            model.setBattleCount(battleCount)
        else:
            model.setBattleCount(0)
        return
