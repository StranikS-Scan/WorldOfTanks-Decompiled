# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/notification/lootbox_listener.py
from helpers.server_settings import GUI_LOOT_BOXES_CONFIG
from notification.listeners import _NotificationListener
from helpers.events_handler import EventsHandler
from skeletons.gui.game_control import IGuiLootBoxesController
from helpers import dependency
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from skeletons.gui.lobby_context import ILobbyContext

class EventLootBoxesListener(_NotificationListener, EventsHandler):
    __slots__ = ('__isActive',)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __START_ENTITY_ID = 0

    def __init__(self):
        super(EventLootBoxesListener, self).__init__()
        self.__isActive = False

    def start(self, model):
        super(EventLootBoxesListener, self).start(model)
        self._subscribe()
        self.__isActive = self.__guiLootBoxes.isEnabled()
        return True

    def stop(self):
        self._unsubscribe()
        super(EventLootBoxesListener, self).stop()

    def _getEvents(self):
        return ((self.__guiLootBoxes.onStatusChange, self.__onStatusChange), (self.__guiLootBoxes.onBoxInfoUpdated, self.__onStatusChange), (self.__guiLootBoxes.onAvailabilityChange, self.__onAvailabilityChange))

    def __onStatusChange(self):
        self.__isActive = self.__guiLootBoxes.isEnabled()

    def __onAvailabilityChange(self, previous, current):
        if previous is not None and previous != current and self.__isActive:
            if current:
                self.__pushLootBoxesEnabled()
            else:
                self.__pushLootBoxesDisabled()
        return

    @staticmethod
    def __pushLootBoxesEnabled():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.notification.lootBoxesIsEnabled.text()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.EventLootBoxEnabled, messageData={'title': backport.text(R.strings.lootboxes.notification.lootBoxesIsEnabled.title())})

    @staticmethod
    def __pushLootBoxesDisabled():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.notification.lootBoxesIsDisabled.text()), priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.EventLootBoxDisabled, messageData={'title': backport.text(R.strings.lootboxes.notification.lootBoxesIsDisabled.title())})


class LootBoxesBuyAvailableListener(_NotificationListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self):
        super(LootBoxesBuyAvailableListener, self).__init__()
        self.__isBuyAvailable = self.__guiLootBoxes.isBuyAvailable()

    def start(self, model):
        result = super(LootBoxesBuyAvailableListener, self).start(model)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        return result

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        super(LootBoxesBuyAvailableListener, self).stop()

    def __onServerSettingsChange(self, diff):
        self.__processSettings(diff, True)

    def __processSettings(self, diff, isNeedNotification=False):
        if GUI_LOOT_BOXES_CONFIG in diff and isNeedNotification:
            changedAvailable = self.__guiLootBoxes.isBuyAvailable()
            if not self.__isBuyAvailable and changedAvailable:
                self.__pushBuyAvailable()
            if self.__isBuyAvailable and not changedAvailable:
                self.__pushBuyDisabled()
            self.__isBuyAvailable = changedAvailable

    @staticmethod
    def __pushBuyAvailable():
        SystemMessages.pushMessage(priority=NotificationPriorityLevel.MEDIUM, text=backport.text(R.strings.lootboxes.notification.lootBoxesBuy.resume.body()), type=SystemMessages.SM_TYPE.Information)

    @staticmethod
    def __pushBuyDisabled():
        SystemMessages.pushMessage(priority=NotificationPriorityLevel.HIGH, text=backport.text(R.strings.lootboxes.notification.lootBoxesBuy.suspend.body()), type=SystemMessages.SM_TYPE.LootBoxesSuspendSale, messageData={'header': backport.text(R.strings.lootboxes.notification.lootBoxesBuy.suspend.header())})
