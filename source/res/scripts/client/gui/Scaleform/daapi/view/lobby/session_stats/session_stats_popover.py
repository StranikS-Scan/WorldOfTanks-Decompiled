# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/session_stats_popover.py
from gui.Scaleform.daapi.view.meta.SessionStatsPopoverMeta import SessionStatsPopoverMeta
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_settings import SessionStatsSettings
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_overview import SessionStatsOverview

class SessionStatsPopover(SessionStatsPopoverMeta):

    def __init__(self, ctx=None):
        super(SessionStatsPopover, self).__init__(ctx)
        self.__sessionBattleStats = None
        self.__sessionSettings = None
        return

    def _populate(self):
        super(SessionStatsPopover, self)._populate()
        data = {'alias': SESSION_STATS_CONSTANTS.SESSION_STATS_OVERVIEW_PY_ALIAS,
         'linkage': SESSION_STATS_CONSTANTS.SESSION_STATS_OVERVIEW_VIEW_LINKAGE}
        self.as_setDataS(data)

    def _dispose(self):
        super(SessionStatsPopover, self)._dispose()
        if self.__sessionBattleStats:
            self.__sessionBattleStats.onShowSettings -= self.onShowSettings
        if self.__sessionSettings:
            self.__sessionSettings.onShowStats -= self.onShowStats

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(SessionStatsPopover, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, SessionStatsOverview):
            self.__sessionBattleStats = viewPy
            self.__sessionBattleStats.onShowSettings += self.onShowSettings
        if isinstance(viewPy, SessionStatsSettings):
            self.__sessionSettings = viewPy
            self.__sessionSettings.onShowStats += self.onShowStats

    def onShowSettings(self):
        data = {'alias': SESSION_STATS_CONSTANTS.SESSION_STATS_SETTINGS_PY_ALIAS,
         'linkage': SESSION_STATS_CONSTANTS.SESSION_STATS_SETTINGS_VIEW_LINKAGE}
        self.as_setDataS(data)

    def onShowStats(self):
        data = {'alias': SESSION_STATS_CONSTANTS.SESSION_STATS_OVERVIEW_PY_ALIAS,
         'linkage': SESSION_STATS_CONSTANTS.SESSION_STATS_OVERVIEW_VIEW_LINKAGE}
        if self.__sessionBattleStats is not None:
            self.__sessionBattleStats.updateData()
        self.as_setDataS(data)
        return
