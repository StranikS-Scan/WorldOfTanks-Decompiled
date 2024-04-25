# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/notification/actions_handlers.py
from adisp import adisp_process
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE
from historical_battles.gui.shared.event_dispatcher import showHBFairplayDialog, showHBFairplayWarningDialog, showHBProgressionView
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.battle_results import RequestResultsContext
from skeletons.gui.battle_results import IBattleResultsService

class ShowHBBattleResultsHandler(NavigationDisabledActionHandler):
    __battleResults = dependency.descriptor(IBattleResultsService)

    @adisp_process
    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        yield self.__battleResults.requestResults(ctx=RequestResultsContext(arenaUniqueID=notification.getSavedData(), showImmediately=False, showIfPosted=True))

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass


class ShowHBFairPlayActionHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        showHBFairplayDialog(data=notification.getSavedData())

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass


class ShowHBWarningFairPlayActionHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        data = notification.getSavedData()
        showHBFairplayWarningDialog(data.get('reason', ''))

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass


class ShowHBProgressionActionHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        forceSelectHBAction()
        showHBProgressionView()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass


@dependency.replace_none_kwargs(controller=IGameEventController)
def forceSelectHBAction(controller=None):
    controller.switchPrb()


class ShowHBEventStartHandler(NavigationDisabledActionHandler):

    def doAction(self, model, entityID, action):
        forceSelectHBAction()

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass
