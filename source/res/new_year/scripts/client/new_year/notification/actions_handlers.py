# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/notification/actions_handlers.py
import BigWorld
from gui.server_events.bonuses import getAllNonQuestBonuses
from gui.shared import g_eventBus, events
from gui.shop import showIngameShop
from gui.shared.system_factory import registerNotificationsActionsHandlers
from helpers import dependency
from skeletons.gui.impl import INewYearNavigation
from new_year.gui.shared.event_dispatcher import showNYLevelUpWindow
from new_year.gui.shared.ny_machine_helper import isMachineEnabled
from new_year.ny_constants import ViewAliases
from new_year.ny_constants import AnchorNames
from new_year.gui.game_control.ny_navigation_helper import switchNewYearView, showLootBox
from new_year.skeletons.new_year import INewYearController
from new_year_common.items import new_year
from new_year.gui.shared.shop_helpers import newYearOldCollectionRewardUrl
from notification.actions_handlers import ActionHandler, NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE

class _NewYearOpenRewardsScreenHandler(NavigationDisabledActionHandler):
    _nyController = dependency.descriptor(INewYearController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        switchNewYearView(AnchorNames.TREE, ViewAliases.REWARDS_VIEW)

    def _canNavigate(self):
        if not self._nyController.isEnabled():
            BigWorld.callback(0.0, self.__showMessage)
            return False
        return super(_NewYearOpenRewardsScreenHandler, self)._canNavigate()

    def __showMessage(self):
        self._nyController.showStateMessage()


class _NewYearOpenPremShopHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.PREM_SHOP))


class _NewYearCollectionCompleteHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None and savedData.get('completedQuestID'):
            questID = savedData.get('completedQuestID')
            collectionStrID = new_year.g_cache.collectionIDByCollectionRewards[questID]
            collectionRewards = {collectionStrID: getAllNonQuestBonuses(savedData.get('rewards', {}))}
            showNYLevelUpWindow(collectionRewards=collectionRewards)
        return


class _OpenLootBoxesHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            showLootBox(lootBoxType=savedData)
        return


class _NewYearPreviousStylesHandler(ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        showIngameShop(newYearOldCollectionRewardUrl())


class _NewYearMachineHandler(ActionHandler):
    _newYearNavigation = dependency.descriptor(INewYearNavigation)
    _newYearController = dependency.descriptor(INewYearController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        if self._newYearController.isEnabled() and isMachineEnabled():
            self._newYearNavigation.showNavigationView(ViewAliases.SURPRISE_MACHINE_VIEW)


def registerNewYearActionHandlers():
    registerNotificationsActionsHandlers((_NewYearOpenRewardsScreenHandler,
     _NewYearOpenPremShopHandler,
     _NewYearCollectionCompleteHandler,
     _NewYearPreviousStylesHandler,
     _NewYearMachineHandler,
     _OpenLootBoxesHandler))
