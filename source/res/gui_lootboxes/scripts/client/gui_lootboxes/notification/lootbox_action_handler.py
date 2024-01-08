# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/notification/lootbox_action_handler.py
from notification.actions_handlers import NavigationDisabledActionHandler
from skeletons.gui.game_control import IGuiLootBoxesController
from helpers import dependency
from notification.settings import NOTIFICATION_TYPE

class _OpenEventLootBoxesShopHandler(NavigationDisabledActionHandler):
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        self.__guiLootBoxes.openShop()
