# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_guest.py
import typing
from account_helpers.AccountSettings import AccountSettings, NY_CAT_PAGE_VISITED, NY_GUEST_ACTIVITY_SHOWN
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.economic_bonus_model import EconomicBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quest_card_model import NewYearQuestCardModel, CardState
from gui.impl.lobby.new_year.dialogs.challenge.guest_quest_purchase_confirm import GuestQuestPurchaseDialogView
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.tooltips.ny_economic_bonus_tooltip import NyEconomicBonusTooltip
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import getNYCelebrityGuestRewardBonuses, guestQuestBonusSortOrder
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from helpers import dependency, server_settings, uniprof
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from new_year.ny_bonuses import EconomicBonusHelper, toPrettyCumulativeBonusValue, CREDITS_BONUS
from new_year.ny_constants import NyTabBarChallengeView, AdditionalCameraObject, GuestsQuestsTokens, CHALLENGE_TAB_TO_CAMERA_OBJ
from new_year.ny_preview import getVehiclePreviewID
from new_year.ny_processor import BuyCelebrityQuestProcessor
from ny_common.settings import NY_CONFIG_NAME
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import ICelebrityController
if typing.TYPE_CHECKING:
    from ny_common.GuestsQuestsConfig import GuestQuest
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quests_celebrity_model import NewYearQuestsCelebrityModel
_TAB_NAME_TO_SERVER_GUEST_ID = {NyTabBarChallengeView.GUEST_A: GuestsQuestsTokens.GUEST_A,
 NyTabBarChallengeView.GUEST_M: GuestsQuestsTokens.GUEST_M,
 NyTabBarChallengeView.GUEST_CAT: GuestsQuestsTokens.GUEST_C}
_SERVER_GUEST_ID_TO_TAB_NAME = {v:k for k, v in _TAB_NAME_TO_SERVER_GUEST_ID.iteritems()}

def tooltipDataExtractor(data):
    return data[0]


class NewYearChallengeGuest(NyHistoryPresenter):
    __slots__ = ('_tooltips', '__guestName', '__questIdToIdx', '__lastAvailableQuestID')
    __celebrityController = dependency.descriptor(ICelebrityController)
    __service = dependency.descriptor(ICustomizationService)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NewYearChallengeGuest, self).__init__(viewModel, parentView, soundConfig)
        self._tooltips = {}
        self.__guestName = None
        self.__questIdToIdx = {}
        self.__lastAvailableQuestID = None
        return

    @property
    def viewModel(self):
        model = self.getViewModel()
        return model.questsCelebrityModel

    @uniprof.regionDecorator(label='ny_challenge_guest', scope='enter')
    def initialize(self, *args, **kwargs):
        super(NewYearChallengeGuest, self).initialize(self, *args, **kwargs)
        ctx = kwargs.get('ctx', {})
        tabName = ctx.get('tabName')
        self.__guestName = _TAB_NAME_TO_SERVER_GUEST_ID.get(tabName, GuestsQuestsTokens.GUEST_A)
        if tabName == NyTabBarChallengeView.GUEST_CAT and not AccountSettings.getUIFlag(NY_CAT_PAGE_VISITED):
            AccountSettings.setUIFlag(NY_CAT_PAGE_VISITED, True)
        self._tooltips.clear()
        self.__questIdToIdx.clear()
        self.__lastAvailableQuestID = None
        self.__fillModel()
        return

    @uniprof.regionDecorator(label='ny_challenge_guest', scope='exit')
    def finalize(self):
        super(NewYearChallengeGuest, self).finalize()

    def clear(self):
        super(NewYearChallengeGuest, self).clear()
        self.__guestName = None
        self._tooltips.clear()
        self.__questIdToIdx.clear()
        self.__lastAvailableQuestID = None
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyEconomicBonusTooltip():
            isMaxBonus = event.getArgument('isMaxBonus', False)
            tooltipID = event.getArgument('tooltipId', ':')
            if tooltipID in self._tooltips:
                _, index = self._tooltips[tooltipID]
            else:
                index = -1
            if isMaxBonus or index > -1:
                return NyEconomicBonusTooltip(isMaxBonus, index, self.__guestName)
        return NyGiftMachineTokenTooltip() if contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip() else super(NewYearChallengeGuest, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator(dataExtractor=tooltipDataExtractor)
    def createToolTip(self, event):
        return super(NewYearChallengeGuest, self).createToolTip(event)

    def _getEvents(self):
        events = super(NewYearChallengeGuest, self)._getEvents()
        serverSettings = self.__lobbyContext.getServerSettings()
        return events + ((self.viewModel.onBuyQuest, self.__onBuyQuest),
         (self.viewModel.onOpenActivity, self.__onOpenActivity),
         (self.viewModel.onShowStylePreview, self.__onShowStylePreview),
         (self._nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated),
         (serverSettings.onServerSettingsChange, self.__onServerSettingsChange),
         (self.__celebrityController.onCelebCompletedTokensUpdated, self.__onCompletedTokensChanged))

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(self.__guestName)
            quests = questsHolder.getQuests()
            completedIdx = self.__celebrityController.getCompletedGuestQuestsCount(self.__guestName)
            model.setCompletedQuestsQuantity(completedIdx)
            model.setTotalQuestsQuantity(len(quests))
            model.setIsWalletAvailable(self.__wallet.isAvailable)
            self.__fillCards(model, quests)
            self.__updateBonus(model)

    def __fillCards(self, model, quests):
        cards = model.getQuestsCelebrity()
        cards.clear()
        for idx, quest in enumerate(quests):
            questID = quest.getQuestID()
            if questID is None:
                continue
            currency, price = GuestsQuestsConfigHelper.getQuestPrice(quest)
            resourceBalenace = self._nyController.currencies.getResouceBalance(currency)
            requiredAmount = price - resourceBalenace if price > resourceBalenace else 0
            self.__questIdToIdx[questID] = idx
            card = NewYearQuestCardModel()
            card.setId(questID)
            card.setPrice(price)
            card.setResource(currency)
            card.setRequiredAmount(requiredAmount)
            card.setState(self.__getQuestStatus(quest))
            rewardsModel = card.getRewards()
            rewardsModel.clear()
            bonuses = quest.getQuestRewards()
            rewards = getNYCelebrityGuestRewardBonuses(bonuses, sortKey=lambda b: guestQuestBonusSortOrder(*b))
            for index, (bonus, tooltip) in enumerate(rewards):
                tooltipId = '{}:{}'.format(questID, index)
                bonus.setTooltipId(tooltipId)
                bonus.setIndex(index)
                rewardsModel.addViewModel(bonus)
                self._tooltips[tooltipId] = (tooltip, idx)

            cards.addViewModel(card)
            rewardsModel.invalidate()

        cards.invalidate()
        return

    def __onBuyQuest(self, args):
        questID = str(args.get('id'))
        questIndex = self.__questIdToIdx.get(questID)
        if self.__guestName is not None and questIndex is not None:
            self.__buySelebQuest(self.__guestName, questIndex)
        return

    def __onOpenActivity(self, args):
        questID = str(args.get('id'))
        if questID is None:
            return
        else:
            quest = GuestsQuestsConfigHelper.getGuestQuestByQuestID(questID)
            tokenID = GuestsQuestsConfigHelper.getQuestActionToken(quest)
            self.__celebrityController.doActionByCelebActionToken(tokenID)
            if not AccountSettings.getUIFlag(NY_GUEST_ACTIVITY_SHOWN):
                AccountSettings.setUIFlag(NY_GUEST_ACTIVITY_SHOWN, True)
                with self.viewModel.transaction() as model:
                    questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(self.__guestName)
                    quests = questsHolder.getQuests()
                    self.__fillCards(model, quests)
            return

    def __onShowStylePreview(self, args):
        styleIntCD = int(args.get('intCD'))
        styleItem = self._itemsCache.items.getItemByCD(styleIntCD)
        if styleItem is None:
            return
        else:
            guestID = _SERVER_GUEST_ID_TO_TAB_NAME.get(self.__guestName)
            NewYearNavigation.switchTo(None, True)
            backBtnDescrLabel = backport.text(R.strings.ny.celebrityChallenge.dyn(guestID).backLabel())

            def _backCallback():
                if not self._nyController.isEnabled():
                    event_dispatcher.showHangar()
                else:
                    NewYearNavigation.switchFromStyle(viewAlias=ViewAliases.CELEBRITY_VIEW, objectName=CHALLENGE_TAB_TO_CAMERA_OBJ.get(guestID, AdditionalCameraObject.CELEBRITY), tabName=guestID, forceShowMainView=True)

            showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=_backCallback, backBtnDescrLabel=backBtnDescrLabel)
            return

    def __onBalanceUpdated(self):
        self.__updateCards()

    @server_settings.serverSettingsChangeListener(NY_CONFIG_NAME)
    def __onServerSettingsChange(self, diff):
        self.__updateCards()

    def __onCompletedTokensChanged(self):
        self.__fillModel()

    def __updateCards(self):
        with self.viewModel.transaction() as model:
            questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(self.__guestName)
            quests = questsHolder.getQuests()
            self.__fillCards(model, quests)

    def __getQuestStatus(self, quest):
        if self.__celebrityController.isGuestQuestCompleted(quest):
            if self.__lastAvailableQuestID == quest.getQuestID():
                return CardState.JUSTCOMPLETED
            return CardState.COMPLETED
        if GuestsQuestsConfigHelper.isQuestAvailable(quest):
            self.__lastAvailableQuestID = quest.getQuestID()
            return CardState.ACTIVE
        return CardState.LOCKED

    @decorators.adisp_process('newYear/buyCelebrityQuest')
    def __buySelebQuest(self, guestName, questIndex):
        dialog = GuestQuestPurchaseDialogView(guestName, questIndex)
        result = yield BuyCelebrityQuestProcessor(guestName, questIndex, dialog).request()
        if result.success:
            serviceChannel = self.__systemMessages.proto.serviceChannel
            serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_GUEST_QUEST_COMPLETED_MESSAGE, auxData=result.auxData)
        elif result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)

    def __updateBonus(self, model):
        bonusesData = EconomicBonusHelper.getBonusesDataInventory()
        bonusesDataMax = EconomicBonusHelper.getMaxBonuses()
        bonuses = {k:(v, bonusesDataMax[k]) for k, v in bonusesData.iteritems() if k != CREDITS_BONUS}
        selectedValue = bonusesData[CREDITS_BONUS]
        selectedMaxValue = bonusesDataMax[CREDITS_BONUS]
        model.setCurrentActiveBonus(toPrettyCumulativeBonusValue(selectedValue))
        model.setMaxActiveBonus(toPrettyCumulativeBonusValue(selectedMaxValue))
        eBonuses = model.getEconomicBonuses()
        eBonuses.clear()
        for bonusName, (value, maxValue) in bonuses.iteritems():
            eBonus = EconomicBonusModel()
            eBonus.setBonusName(bonusName)
            eBonus.setBonusValue(toPrettyCumulativeBonusValue(value))
            eBonus.setMaxBonus(toPrettyCumulativeBonusValue(maxValue))
            eBonuses.addViewModel(eBonus)

        eBonuses.invalidate()
