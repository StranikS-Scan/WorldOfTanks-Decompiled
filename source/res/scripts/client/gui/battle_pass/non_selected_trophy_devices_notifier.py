# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/non_selected_trophy_devices_notifier.py
import weakref
import typing
from gui import SystemMessages
from gui.battle_pass.battle_pass_bonuses_helper import TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME
from gui.battle_pass.battle_pass_helpers import getNotificationStorageKey
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.notifications import NotificationPriorityLevel, NotificationGuiSettings
from helpers import dependency
from messenger import g_settings
from notification.decorators import ChoosingDevicesMessageDecorator
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from skeletons.gui.game_control import IBattlePassController

class NonSelectedOldTrophyDeviceNotifier(object):
    __slots__ = ('__battlePassController', '__isStarted')
    TROPHY_DEVICES_MSG_ID = 0
    NEW_DEVICES_MSG_ID = 1
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, battlePassController):
        super(NonSelectedOldTrophyDeviceNotifier, self).__init__()
        self.__battlePassController = weakref.proxy(battlePassController)
        self.__isStarted = False

    def start(self):
        if not self.__isStarted:
            self.__isStarted = True
            self.__battlePassController.onDeviceSelectChange += self.__tryNotify
            self.__battlePassController.onSeasonStateChange += self.__tryNotify
            self.__battlePassController.onBattlePassSettingsChange += self.__onServerSettingChanged
            self.__tryNotify()

    def stop(self):
        self.__isStarted = False
        self.__battlePassController.onDeviceSelectChange -= self.__tryNotify
        self.__battlePassController.onSeasonStateChange -= self.__tryNotify
        self.__battlePassController.onBattlePassSettingsChange -= self.__onServerSettingChanged

    def __onServerSettingChanged(self, *_):
        self.__tryNotify()

    def __notify(self, bonusName):
        message = backport.text(R.strings.messenger.serviceChannelMessages.nonSelectedDevices.text.dyn(bonusName)(), count=self.__getTokensCount(bonusName))
        msgPrLevel = NotificationPriorityLevel.MEDIUM
        if self.__isNotificationShown(bonusName):
            msgPrLevel = NotificationPriorityLevel.LOW
        else:
            self.__saveNotificationShown(bonusName)
        savedData = {'bonusName': bonusName,
         'count': self.__getTokensCount(bonusName)}
        g_eventBus.handleEvent(events.ChoosingDevicesEvent(events.ChoosingDevicesEvent.DEVICE_ADDED, ctx={'notifacation': ChoosingDevicesMessageDecorator(self.__getMassageID(bonusName), g_settings.msgTemplates.format(SystemMessages.SM_TYPE.NotSelectedDevicesReminder.name(), ctx={'text': message}, data={'savedData': savedData}), NotificationGuiSettings(isNotify=True, priorityLevel=msgPrLevel))}), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __tryNotify(self):
        seasonNotActive = self.__battlePassController.isSeasonFinished() or self.__battlePassController.isDisabled()
        for bonusName in (TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME):
            if not bool(self.__getTokensCount(bonusName)):
                self.__resetNotificationShown(bonusName)
                self.__removeNotification(bonusName)
                continue
            if (self.__hasTokensFromPrevSeason(bonusName) or seasonNotActive) and self.__battlePassController.isOfferEnabled():
                self.__notify(bonusName)

    def __removeNotification(self, bonusName):
        g_eventBus.handleEvent(events.ChoosingDevicesEvent(events.ChoosingDevicesEvent.DEVICE_REMOVED, ctx={'entityID': self.__getMassageID(bonusName)}), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __hasTokensFromPrevSeason(self, bonusName):
        totalCount = self.__getTokensCount(bonusName)
        return totalCount > 0

    def __isNotificationShown(self, bonusName):
        return self.__settingsCore.serverSettings.getBPStorage().get(getNotificationStorageKey(bonusName))

    def __saveNotificationShown(self, bonusName):
        self.__settingsCore.serverSettings.saveInBPStorage({getNotificationStorageKey(bonusName): 1})

    def __resetNotificationShown(self, bonusName):
        self.__settingsCore.serverSettings.saveInBPStorage({getNotificationStorageKey(bonusName): 0})

    def __getTokensCount(self, bonusName):
        if bonusName == TROPHY_GIFT_TOKEN_BONUS_NAME:
            return self.__battlePassController.getOldTrophySelectTokensCount()
        return self.__battlePassController.getOldNewDeviceSelectTokensCount() if bonusName == NEW_DEVICE_GIFT_TOKEN_BONUS_NAME else 0

    @classmethod
    def __getMassageID(cls, bonusName):
        if bonusName == TROPHY_GIFT_TOKEN_BONUS_NAME:
            return cls.TROPHY_DEVICES_MSG_ID
        else:
            return cls.NEW_DEVICES_MSG_ID if bonusName == NEW_DEVICE_GIFT_TOKEN_BONUS_NAME else None
