# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/__init__.py
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.decorators import sf_lobby

class BattleResultsOpenMixin(object):

    @property
    def isBattleResultsOpen(self):
        if self.__app is not None:
            if self.__app.containerManager is not None:
                lobbySubContainer = self.__app.containerManager.getContainer(ViewTypes.LOBBY_TOP_SUB)
                if lobbySubContainer is not None:
                    if lobbySubContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.EVENT_BATTLE_RESULTS}):
                        return True
        return False

    @sf_lobby
    def __app(self):
        return None
