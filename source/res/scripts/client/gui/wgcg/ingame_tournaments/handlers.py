# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/ingame_tournaments/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class IngameTournamentHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.INGAME_TOURNAMENT_GET_DATA: self.__getTournamentData}
        return handlers

    def __getTournamentData(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('tournaments', 'get_ingame_tournament'))
