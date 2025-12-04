# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/sys_msg/sys_msg_handler.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from helpers.events_handler import EventsHandler
from helpers.time_utils import ONE_MINUTE, getServerUTCTime
from messenger import MessengerEntry
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.gui.shared.formatters import formatPurchaseItems, formatPurchasedItems, formatActivatedItem, formatMailRewardsItems
from new_year.skeletons.new_year import ITamagotchiDataProvider
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_main_widget_model import State
from shared_utils import findFirst
from gui.SystemMessages import SM_TYPE
from gui import SystemMessages
MINUTES_TO_SHOW_NOTIF = (5, 15, 30, 60)
START_SHOW_LEADERBOARD_NOTIF_END = 60

class TamagotchiSysMsgHandler(EventsHandler):
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _systemMessages = MessengerEntry.g_instance.protos.BW.serviceChannel
    __slots__ = ('__isFirstEntry',)

    def __init__(self):
        self.__isFirstEntry = True

    def init(self):
        self._subscribe()

    def fini(self):
        self._unsubscribe()

    def _getEvents(self):
        return ((self._dataProvider.onItemsActivated, self._onItemsActivated),
         (self._dataProvider.onItemsPurchased, self._onItemsPurchased),
         (self._dataProvider.onGiftObtained, self.__onGiftObtained),
         (self._dataProvider.onMailRewards, self.__onMailRewards),
         (self._dataProvider.onSimulationEnd, self.__onLeaderboardUpdate),
         (self._dataProvider.onSimulationEnd, self.__onCheckTamagotchiState))

    @classmethod
    def pushClientSysMessage(cls, message, msgType, msgName, priority=None, messageData=None, savedData=None):
        return cls._systemMessages.pushClientMessage(message, msgType, isAlert=False, auxData=[msgName,
         priority,
         messageData,
         savedData])

    @classmethod
    def showSkipMsg(cls):
        cls.pushClientSysMessage(backport.text(R.strings.ny.notification.tamagotchi.tutor.skip.msg()), msgType=SCH_CLIENT_MSG_TYPE.NY_TAMAGOTCHI_TUTORIAL, msgName='NYTamagotchiTutorSkip', priority=NotificationPriorityLevel.LOW)

    def _onItemsActivated(self, isSuccess, itemId, count, isRecalculation):
        if isRecalculation:
            return
        if isSuccess:
            itemName, item = findFirst(lambda (name, indicator): indicator.item.id == itemId, self._dataProvider.config.indicators.iteritems())
            extraScalePoints = int(item.item.scalePoint * count)
            potentialLoyaltyPoints = 0 if self._dataProvider.isLeaderboardFinished else int(item.item.leaderboardPoint * count)
            self.pushClientSysMessage(formatActivatedItem(itemName, count, extraScalePoints, potentialLoyaltyPoints), msgType=SCH_CLIENT_MSG_TYPE.NY_TAMAGOTCHI_TUTORIAL, msgName='NYTamagotchiItemsActivated', priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.ny.notification.racoon.activated.header.dyn(itemName)())})
        else:
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.racoon.activated.error()), type=SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)
            if self._dataProvider.isOnboarding:
                self.pushClientSysMessage(backport.text(R.strings.ny.notification.tamagotchi.tutor.error.msg()), msgType=SCH_CLIENT_MSG_TYPE.NY_TAMAGOTCHI_TUTORIAL, msgName='NYTamagotchiTutorError', priority=NotificationPriorityLevel.MEDIUM)

    def _onItemsPurchased(self, isSuccess, itemsDict):
        if isSuccess:
            itemsDictByName = {}
            for name, indicator in self._dataProvider.config.indicators.iteritems():
                if indicator.item.id not in itemsDict:
                    continue
                itemsDictByName[name] = itemsDict[indicator.item.id]

            self.pushClientSysMessage(formatPurchasedItems(itemsDictByName), msgType=SCH_CLIENT_MSG_TYPE.NY_TAMAGOTCHI_TUTORIAL, msgName='NYTamagotchiPurchased', priority=NotificationPriorityLevel.MEDIUM)
        else:
            SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.racoon.purchased.error.text()), type=SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)

    def __onGiftObtained(self, isSuccess, initialCount, count, isSecret, isRecalculation):
        if not isSuccess and not isRecalculation:
            SystemMessages.pushMessage(backport.text(R.strings.ny.notification.racoon.gift.error()), type=SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)

    def __onMailRewards(self, rewards):
        self.pushClientSysMessage(formatMailRewardsItems(rewards), msgType=SCH_CLIENT_MSG_TYPE.SYS_MSG_TYPE, msgName='NYGiftReceived', priority=NotificationPriorityLevel.MEDIUM)

    def __onCheckTamagotchiState(self, isSuccess=False):
        self._dataProvider.onSimulationEnd -= self.__onCheckTamagotchiState
        petState = self._dataProvider.playerInfo.state
        if self._dataProvider.isOnboarding or petState == State.PAUSE:
            return
        if petState != State.FUN:
            self.pushClientSysMessage(backport.text(R.strings.ny.notification.tamagotchi.check_state.text()), msgType=SCH_CLIENT_MSG_TYPE.NY_TAMAGOTCHI_TUTORIAL, msgName='NYTamagotchiCheckState', priority=NotificationPriorityLevel.MEDIUM)

    def __onLeaderboardUpdate(self):
        if not self._dataProvider.isValidConfig:
            return
        else:
            currentSeason = self._dataProvider.config.currentSeason
            if currentSeason is None:
                return
            endTime = int(round((currentSeason.endTime - getServerUTCTime()) / ONE_MINUTE))
            seasonId = currentSeason.id
            if endTime > START_SHOW_LEADERBOARD_NOTIF_END:
                return
            if self.__isFirstEntry:
                self.pushEndTimeMessage(seasonId, endTime)
                self.__isFirstEntry = False
                return
            for time in MINUTES_TO_SHOW_NOTIF:
                if endTime == time:
                    self.pushEndTimeMessage(seasonId, endTime)

            return

    @classmethod
    def pushEndTimeMessage(cls, seasonId, endTime):
        SystemMessages.pushMessage(backport.text(R.strings.ny.notification.leaderboard.timeLeft(), seasonId=seasonId, minutes=endTime), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.ny.notification.leaderboard.header())})

    @classmethod
    def sendRewardNotification(cls, rewards, seasonId):
        rewardsText = formatPurchaseItems(rewards)
        SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.leaderboard.reward.description(), seasonId=seasonId, rewards=rewardsText), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.ny.notification.leaderboard.reward.title())})

    @classmethod
    def sendNotifWithoutReward(cls, seasonId):
        SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.leaderboard.seasonId.end(), seasonId=seasonId), type=SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.ny.notification.header())})

    @classmethod
    def sendLeaderboardNotAvailableMessage(cls):
        SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.leaderboard.unavailable()), type=SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.ny.notification.leaderboard.header())})
