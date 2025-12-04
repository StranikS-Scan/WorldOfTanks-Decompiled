# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/messenger/listeners.py
import typing
from notification.listeners import _NotificationListener
from helpers import dependency, time_utils
from skeletons.gui.game_control import ILimitedUIController, IArmoryYardController, IArmoryYardShopController
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
from skeletons.gui.system_messages import ISystemMessages
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ArmoryYard
from messenger.formatters import TimeFormatter
from gui.impl import backport
from gui.impl.gen import R
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.shared.money import Currency
from gui.shared.notifications import NotificationPriorityLevel
from gui.limited_ui.lui_rules_storage import LuiRules
from armory_yard_constants import State
from armory_yard.gui.shared.formatters import formatSpentCurrencies, formatPurchaseItems, formatBundlePurchase
if typing.TYPE_CHECKING:
    from typing import List, Dict, Tuple

class ArmoryYardListener(_NotificationListener):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __armoryYardShopCtrl = dependency.descriptor(IArmoryYardShopController)
    __armoryYardRerollCtrl = dependency.descriptor(IArmoryYardRerollController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __armoryYardText = R.strings.armory_yard.notifications
    __systemMessages = dependency.descriptor(ISystemMessages)
    __lastTimeErrorShown = 0
    __timeDelay = 2
    ARMORY_YARD_TEXT = R.strings.armory_yard.notifications
    ARMORY_YARD_SHOP_TEXT = R.strings.armory_shop.notifications
    CURRENCY_TYPE_MAP = {Currency.GOLD: (SM_TYPE.FinancialTransactionWithGold, ARMORY_YARD_TEXT.payed.priceGold, ARMORY_YARD_TEXT.refund.priceGold),
     Currency.CRYSTAL: (SM_TYPE.FinancialTransactionWithCrystal, ARMORY_YARD_TEXT.payed.priceCrystal, ARMORY_YARD_TEXT.refund.priceCrystal),
     None: (SM_TYPE.ArmoryYardRerollTransactionForFreeReroll, ARMORY_YARD_TEXT.payed.freeReroll, ARMORY_YARD_TEXT.refund.freeReroll)}

    def start(self, model):
        super(ArmoryYardListener, self).start(model)
        if not self.__limitedUIController.isRuleCompleted(LuiRules.ARMORY_YARD_ENTRY_POINT):
            self.__limitedUIController.startObserve(LuiRules.ARMORY_YARD_ENTRY_POINT, self.__onLuiRuleCompleted)
        else:
            self.__subscribe()
        if self.__armoryYardCtrl.isEnabled() and self.__armoryYardCtrl.getState() != State.PURCHASESTAGE:
            self.__checkIncompleteRerolls()
        return True

    def stop(self):
        if not self.__limitedUIController.isRuleCompleted(LuiRules.ARMORY_YARD_ENTRY_POINT):
            self.__limitedUIController.stopObserve(LuiRules.ARMORY_YARD_ENTRY_POINT, self.__onLuiRuleCompleted)
        else:
            self.__unsubscribe()
        super(ArmoryYardListener, self).stop()

    def __onLuiRuleCompleted(self, *_):
        self.__limitedUIController.stopObserve(LuiRules.ARMORY_YARD_ENTRY_POINT, self.__onLuiRuleCompleted)
        self.__subscribe()

    def __subscribe(self):
        self.__armoryYardCtrl.onCheckNotify += self.__onCheckNotify
        self.__armoryYardCtrl.onAnnouncement += self.__announcement
        self.__armoryYardCtrl.onPayed += self.__payed
        self.__armoryYardCtrl.onServerSwitchChange += self.__switchChange
        self.__armoryYardCtrl.onStyleQuestEnds += self.__onStyleQuestEnds
        self.__armoryYardCtrl.onProgressUpdated += self.__checkChapter
        self.__armoryYardCtrl.onQuestsUpdated += self.__checkChapter
        self.__armoryYardCtrl.onCollectReward += self.__collectReward
        self.__armoryYardCtrl.onPayedError += self.__paymentError
        self.__armoryYardCtrl.onBundleOutTime += self.__bundleOutTime
        self.__armoryYardShopCtrl.onPurchaseComplete += self.__onShopPurchaseComplete
        self.__armoryYardShopCtrl.onPurchaseError += self.__paymentError
        self.__armoryYardRerollCtrl.onRerollQuest += self.__rerollQuest
        self.__armoryYardRerollCtrl.onAcceptReroll += self.__acceptReroll
        self.__lastTimeErrorShown = 0
        self.__onCheckNotify()

    def __unsubscribe(self):
        self.__armoryYardCtrl.onCheckNotify -= self.__onCheckNotify
        self.__armoryYardCtrl.onAnnouncement -= self.__announcement
        self.__armoryYardCtrl.onPayed -= self.__payed
        self.__armoryYardCtrl.onServerSwitchChange -= self.__switchChange
        self.__armoryYardCtrl.onStyleQuestEnds -= self.__onStyleQuestEnds
        self.__armoryYardCtrl.onProgressUpdated -= self.__checkChapter
        self.__armoryYardCtrl.onQuestsUpdated -= self.__checkChapter
        self.__armoryYardCtrl.onCollectReward -= self.__collectReward
        self.__armoryYardCtrl.onPayedError -= self.__paymentError
        self.__armoryYardCtrl.onBundleOutTime -= self.__bundleOutTime
        self.__armoryYardShopCtrl.onPurchaseComplete -= self.__onShopPurchaseComplete
        self.__armoryYardShopCtrl.onPurchaseError -= self.__paymentError
        self.__armoryYardRerollCtrl.onRerollQuest -= self.__rerollQuest
        self.__armoryYardRerollCtrl.onAcceptReroll -= self.__acceptReroll
        self.__lastTimeErrorShown = 0

    def __getHeader(self):
        return backport.text(self.ARMORY_YARD_TEXT.title())

    def __getShopHeader(self):
        return backport.text(self.ARMORY_YARD_SHOP_TEXT.title())

    def __collectReward(self):
        if not self.__armoryYardCtrl.isPaused and self.__armoryYardCtrl.isActive():
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.collectRewards()), type=SystemMessages.SM_TYPE.ArmoryYardMain, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(self.ARMORY_YARD_TEXT.rewards.title())})

    def __switchChange(self):
        if self.__armoryYardCtrl.getState() != State.DISABLED:
            _, endDate = self.__armoryYardCtrl.getSeasonInterval()
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.switcher.enabled(), endDate=backport.getDateTimeFormat(endDate)), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
        else:
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.switcher.disabled()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': self.__getHeader()})

    def __announcement(self, startDate, chapterInfo=None):
        if chapterInfo is None and not AccountSettings.getArmoryYard(ArmoryYard.EVENT_ANNOUNCEMENT):
            vehicle = self.__armoryYardCtrl.getFinalRewardVehicle()
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.announcement.event(), startDate=backport.getDateTimeFormat(startDate), tankName=vehicle.userName), type=SystemMessages.SM_TYPE.ArmoryYardInformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
            AccountSettings.setArmoryYard(ArmoryYard.EVENT_ANNOUNCEMENT, True)
        elif chapterInfo is not None:
            key = '%s_%s' % (ArmoryYard.ANNOUNCEMENT_CHAPTER_PREFIX, chapterInfo.ID)
            if not AccountSettings.getArmoryYard(key):
                AccountSettings.setArmoryYard(key, True)
                SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.announcement.chapter(), count=chapterInfo.ordinalNumber, chapter_name=backport.text(R.strings.armory_yard.mainView.chapter.index.dyn('c_%d' % chapterInfo.ordinalNumber)()), startDate=backport.getDateTimeFormat(startDate)), type=SystemMessages.SM_TYPE.ArmoryYardInformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
        return

    def __getShopPurchaseSMType(self, currencies):
        currencies = dict(currencies)
        isGold, isCoins = currencies.get(Currency.GOLD, 0) > 0, currencies.get(Currency.AYCOIN, 0) > 0
        if isGold and isCoins:
            return SystemMessages.SM_TYPE.FinancialTransactionWithGoldAndArmoryCoinsHeader
        return SystemMessages.SM_TYPE.FinancialTransactionWithArmoryCoinsHeader if isCoins else SystemMessages.SM_TYPE.FinancialTransactionWithGoldHeader

    def __onShopPurchaseComplete(self, productId, currencies, rewards, isBundle):
        SystemMessages.pushMessage(text=backport.text(R.strings.armory_shop.notifications.financialTransaction(), date=TimeFormatter.getLongDatetimeFormat(time_utils.getServerUTCTime()), currencies=formatSpentCurrencies(currencies)), type=self.__getShopPurchaseSMType(currencies), priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.messenger.serviceChannelMessages.currencyUpdate.financial_transaction())})
        text = formatBundlePurchase(productId, rewards) if isBundle else formatPurchaseItems(rewards)
        smType = SystemMessages.SM_TYPE.ArmoryYardBundlePurchase if isBundle else SystemMessages.SM_TYPE.ArmoryYardInformationHeader
        SystemMessages.pushMessage(text=text, type=smType, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.titles.purchase())})

    def __payed(self, isPostProgression, count, price=None, currency=Currency.GOLD):
        bodySection = self.ARMORY_YARD_TEXT.postPayed if isPostProgression else self.ARMORY_YARD_TEXT.payed
        messageType = SystemMessages.SM_TYPE.FinancialTransactionBuyAYFreeCoins if isPostProgression else SystemMessages.SM_TYPE.FinancialTransactionBuyAYCoins
        messageResID = bodySection.single() if count == 1 else bodySection.multiple()
        SystemMessages.pushMessage(text=backport.text(messageResID, count=count), type=messageType, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
        if price is None or currency not in self.CURRENCY_TYPE_MAP:
            return
        else:
            systemMessageType, _, _ = self.CURRENCY_TYPE_MAP[currency]
            SystemMessages.pushMessage(text=backport.text(R.strings.armory_shop.notifications.financialTransaction(), date=TimeFormatter.getLongDatetimeFormat(time_utils.getServerUTCTime()), currencies=formatSpentCurrencies([(currency, price.getSignValue(currency))])), type=systemMessageType, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.messenger.serviceChannelMessages.currencyUpdate.financial_transaction())})
            return

    def __paymentError(self):
        currentTime = time_utils.getServerUTCTime()
        if currentTime - self.__lastTimeErrorShown < self.__timeDelay:
            return
        self.__lastTimeErrorShown = currentTime
        SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.payed.error()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': self.__getHeader()})

    def __bundleOutTime(self):
        SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.bundleOutTime()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': self.__getHeader()})

    def __checkState(self):
        state = self.__armoryYardCtrl.getState()
        armoryIsActiveMessageWasShown = AccountSettings.getArmoryYard(State.ACTIVE.value)
        currentStateMessageWasShown = AccountSettings.getArmoryYard(state.value)
        if not self.__armoryYardCtrl.isActive() or currentStateMessageWasShown and armoryIsActiveMessageWasShown:
            return
        AccountSettings.setArmoryYard(state.value, True)
        if not armoryIsActiveMessageWasShown:
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.active()), type=SystemMessages.SM_TYPE.ArmoryYardMain, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
            AccountSettings.setArmoryYard(State.ACTIVE.value, True)
        if state == State.PURCHASESTAGE and not currentStateMessageWasShown and not self.__armoryYardCtrl.isCompleted():
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.purchaseStage()), type=SystemMessages.SM_TYPE.ArmoryYardPostprogression, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})

    def __checkChapter(self):
        if self.__armoryYardCtrl.getState() != State.ACTIVE:
            return
        nowTime = time_utils.getServerUTCTime()
        currentSeason = self.__armoryYardCtrl.serverSettings.getCurrentSeason()
        if not currentSeason:
            return
        for cycle in currentSeason.getAllCycles().values():
            key = '%s_%s' % (ArmoryYard.START_CHAPTER_PREFIX, cycle.ID)
            if cycle.startDate <= nowTime < cycle.endDate and not AccountSettings.getArmoryYard(key):
                AccountSettings.setArmoryYard(key, True)
                SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.started.chapter(), count=cycle.ordinalNumber, chapter_name=backport.text(R.strings.armory_yard.mainView.chapter.index.dyn('c_%d' % cycle.ordinalNumber)())), type=SystemMessages.SM_TYPE.ArmoryYardOpenChapter, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})

    def __onCheckNotify(self):
        if not self.__armoryYardCtrl.isEnabled():
            return
        self.__armoryYardCtrl.checkAnnouncement()
        self.__checkState()
        self.__checkChapter()

    def __onStyleQuestEnds(self, endDate):
        if not AccountSettings.getArmoryYard(ArmoryYard.STYLE_QUEST_ENDS):
            AccountSettings.setArmoryYard(ArmoryYard.STYLE_QUEST_ENDS, True)
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.styleQuest(), endDate=backport.getDateTimeFormat(endDate)), type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})

    def __checkIncompleteRerolls(self):
        questID = self.__armoryYardRerollCtrl.getReplacedTokenQuestID()
        if questID is not None:
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.task.replacementNotCompleted.body()), type=SystemMessages.SM_TYPE.ArmoryYardRerollNotCompleted, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(self.ARMORY_YARD_TEXT.task.replacementNotCompleted.header())})
        return

    def __rerollQuest(self, rerollCurrency):
        _, payedText, _ = self.CURRENCY_TYPE_MAP.get(rerollCurrency, self.CURRENCY_TYPE_MAP[None])
        price = max(self.__armoryYardRerollCtrl.getRerollCost(rerollCurrency), 1)
        msgType = {Currency.CRYSTAL: SM_TYPE.ArmoryYardRerollTransactionForCrystal,
         Currency.GOLD: SM_TYPE.ArmoryYardRerollTransactionForGold}.get(rerollCurrency, SM_TYPE.ArmoryYardRerollTransactionForFreeReroll)
        SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.task.paymentForReplacement()), type=msgType, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader(),
         'paymentText': backport.text(payedText(), price=price)})
        return

    def __acceptReroll(self, lastConditionID, conditionID):
        if lastConditionID != conditionID:
            SystemMessages.pushMessage(text=backport.text(self.ARMORY_YARD_TEXT.task.successfullyReplaced()), type=SM_TYPE.ArmoryYardInformationHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': self.__getHeader()})
