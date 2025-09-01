# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/notification/actions_handlers.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from comp7.gui.prb_control.entities import comp7_prb_helpers
from comp7.gui.shared.event_dispatcher import showComp7BanWindow
from comp7.gui.shared.event_dispatcher import showComp7MetaRootTab, showComp7AllRewardsSelectionWindow
from constants import PENALTY_TYPES, FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA, ARENA_BONUS_TYPE
from gui.shared import event_dispatcher as shared_events
from helpers import dependency
from notification.actions_handlers import NavigationDisabledActionHandler, _OpenPunishmentWindowHandler
from notification.settings import NOTIFICATION_TYPE
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller, IHangarSpaceSwitchController

class OpenComp7ShopHandler(NavigationDisabledActionHandler):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __customizationService = dependency.descriptor(ICustomizationService)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        if not self.__comp7Controller.isModePrbActive():
            self.__spaceSwitchController.onSpaceUpdated += self.__onSpaceUpdated
            comp7_prb_helpers.selectComp7()
            return
        elif self.__customizationService.getCtx() is not None:
            self.__customizationService.onVisibilityChanged += self.__onC11nVisibilityChanged
            shared_events.showHangar()
            return
        else:
            self.__goToShop()
            return

    def __onC11nVisibilityChanged(self, isC11nVisible):
        if not isC11nVisible:
            self.__customizationService.onVisibilityChanged -= self.__onC11nVisibilityChanged
            self.__goToShop()

    def __onSpaceUpdated(self):
        if not self.__comp7Controller.isModePrbActive():
            return
        self.__spaceSwitchController.onSpaceUpdated -= self.__onSpaceUpdated
        self.__goToShop()

    def __goToShop(self):
        showComp7MetaRootTab(tabId=MetaRootViews.SHOP)


class OpenBondEquipmentSelection(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.COMP7_OFFER_TOKENS

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showComp7AllRewardsSelectionWindow()


class Comp7OpenPunishmentWindowHandler(_OpenPunishmentWindowHandler):

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            penaltyType = savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.PENALTY_TYPE]
            if penaltyType == PENALTY_TYPES.BAN:
                if savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_BONUS_TYPE] == ARENA_BONUS_TYPE.COMP7:
                    showComp7BanWindow(savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_TYPE_ID], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.ARENA_TIME], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.BAN_DURATION], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.COMP7_PENALTY], savedData[FAIRPLAY_VIOLATION_SYS_MSG_SAVED_DATA.COMP7_IS_QUALIFICATION], force=True)
                    return
        super(Comp7OpenPunishmentWindowHandler, self).handleAction(model, entityID, action)
        return
