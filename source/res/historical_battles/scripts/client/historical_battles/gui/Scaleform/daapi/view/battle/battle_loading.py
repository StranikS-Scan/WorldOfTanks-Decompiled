# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/battle_loading.py
from typing import List, Dict
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.meta.HBLoadingMeta import HBLoadingMeta
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from historical_battles.gui.Scaleform.daapi.view.battle.slides import LoadingScreenSlidesCfg
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider

class HistoricalBattleLoading(HBLoadingMeta, IArenaLoadController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    appLoader = dependency.descriptor(IAppLoader)

    def _populate(self):
        super(HistoricalBattleLoading, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        g_playerEvents.onDisconnected += self._onDisconnected
        self.as_setDataS(self._getData())

    def _getData(self):
        arenaTypeName = self.sessionProvider.arenaVisitor.getArenaType().geometryName
        loadingScreenData = LoadingScreenSlidesCfg.instance().getLoadingScreen(arenaTypeName)
        slides = [ slide.getLoadingData() for slide in loadingScreenData.slides ]
        return slides

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        g_playerEvents.onDisconnected -= self._onDisconnected
        self.appLoader.detachCursor(APP_NAME_SPACE.SF_BATTLE)
        super(HistoricalBattleLoading, self)._dispose()

    def updateSpaceLoadProgress(self, progress):
        self.as_updateProgressS(progress)

    def _onDisconnected(self):
        self.destroy()
