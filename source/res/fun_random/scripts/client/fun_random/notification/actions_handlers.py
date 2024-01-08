# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/notification/actions_handlers.py
from adisp import adisp_process
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher, FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasMultipleSubModes
from helpers import dependency
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE
from skeletons.gui.lobby_context import ILobbyContext

class SelectFunRandomMode(NavigationDisabledActionHandler, FunSubModesWatcher):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    @hasMultipleSubModes(defReturn=True)
    def checkHeaderNavigation(self):
        return False

    @adisp_process
    def doAction(self, model, entityID, action):
        navigationPossible = True
        if self.checkHeaderNavigation():
            navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if navigationPossible:
            yield self.selectFunRandomBattle()


class ShowFunRandomProgression(NavigationDisabledActionHandler, FunProgressionWatcher):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self.showActiveProgressionPage()
