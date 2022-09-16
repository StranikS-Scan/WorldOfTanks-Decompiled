# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/notification/actions_handlers.py
from adisp import adisp_process
from helpers import dependency
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.lobby_context import ILobbyContext

class SelectFunRandomMode(NavigationDisabledActionHandler):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @adisp_process
    def doAction(self, model, entityID, action):
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if navigationPossible:
            self.__funRandomCtrl.selectFunRandomBattle()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass
