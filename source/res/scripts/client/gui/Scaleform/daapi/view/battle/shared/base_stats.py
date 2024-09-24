# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/base_stats.py
from gui.Scaleform.daapi.view.meta.StatsBaseMeta import StatsBaseMeta
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from uilogging.player_satisfaction_rating.loggers import InviteToPlatoonLogger

class StatsBase(StatsBaseMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(StatsBase, self).__init__()
        self._logger = InviteToPlatoonLogger()

    @property
    def hasTabs(self):
        return False

    def acceptSquad(self, sessionID):
        self.sessionProvider.invitations.accept(sessionID)

    def addToSquad(self, sessionID, source):
        self._logger.logPlatoonInvite(source)
        self.sessionProvider.invitations.send(sessionID)

    def onToggleVisibility(self, isVisible):
        self._onToggleVisibility(isVisible)

    def _populate(self):
        self.addListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        super(StatsBase, self)._populate()

    def _dispose(self):
        self.__invitations = None
        self.removeListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        super(StatsBase, self)._dispose()
        return

    def _onToggleVisibility(self, isVisible):
        pass

    def __handleShowCursor(self, _):
        self.as_setIsInteractiveS(True)

    def __handleHideCursor(self, _):
        self.as_setIsInteractiveS(False)
