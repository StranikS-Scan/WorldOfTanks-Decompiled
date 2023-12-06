# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_listeners.py
from helpers import dependency
from notification.base_listener import NotificationListener
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IGuiLootBoxesController
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers.server_settings import GUI_LOOT_BOXES_CONFIG

class NYGuiLootBoxConfigListener(NotificationListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self):
        super(NYGuiLootBoxConfigListener, self).__init__()
        self.__isBuyAvailable = self.__guiLootBoxes.isBuyAvailable()

    def start(self, model):
        result = super(NYGuiLootBoxConfigListener, self).start(model)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        return result

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        super(NYGuiLootBoxConfigListener, self).stop()

    def __onServerSettingsChange(self, diff):
        self.__processSettings(diff, True)

    def __processSettings(self, diff, isNeedNotification=False):
        if GUI_LOOT_BOXES_CONFIG in diff and isNeedNotification:
            changedAvailable = self.__guiLootBoxes.isBuyAvailable()
            if not self.__isBuyAvailable and changedAvailable:
                rKey = R.strings.ny.notification.lootBox.resume
                SystemMessages.pushMessage(priority=NotificationPriorityLevel.MEDIUM, text=backport.text(rKey.body()), type=SystemMessages.SM_TYPE.Information)
            if self.__isBuyAvailable and not changedAvailable:
                rKey = R.strings.ny.notification.lootBox.suspend
                SystemMessages.pushMessage(priority=NotificationPriorityLevel.HIGH, text=backport.text(rKey.body()), type=SystemMessages.SM_TYPE.LootBoxesSuspendSail, messageData={'header': backport.text(rKey.header())})
            self.__isBuyAvailable = changedAvailable
