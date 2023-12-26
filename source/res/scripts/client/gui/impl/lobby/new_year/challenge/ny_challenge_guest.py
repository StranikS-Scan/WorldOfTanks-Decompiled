# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_guest.py
import typing
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.economic_bonus_model import EconomicBonusModel
from gui.impl.lobby.new_year.dialogs.challenge.guest_quest_purchase_confirm import GuestQuestPurchaseDialogView
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import getNYCelebrityGuestRewardBonuses, guestQuestBonusSortOrder
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, getRewardKitsCount
from gui.shared import event_dispatcher, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showStylePreview, showLootBoxBuyWindow, showLootBoxEntry
from gui.shared.events import NyCelebrityAnimationEvent, NyCelebrityStoriesEvent
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.utils import decorators
from gui.impl.gen import R
from gui.shared.view_helpers.blur_manager import CachedBlur
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.ny_bonuses import EconomicBonusHelper, toPrettyCumulativeBonusValue, CREDITS_BONUS
from new_year.ny_preview import getVehiclePreviewID
from new_year.ny_processor import BuyCelebrityQuestProcessor
from gui import SystemMessages
from gui.shared.event_dispatcher import pushNYQuestRewardsMessage
from gui.shared.notifications import NotificationPriorityLevel
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quest_card_model import NewYearQuestCardModel, CardState
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.tooltips.ny_economic_bonus_tooltip import NyEconomicBonusTooltip
from gui.impl.lobby.new_year.tooltips.ny_market_lack_the_res_tooltip import NyMarketLackTheResTooltip
from helpers import dependency, server_settings
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper, isCatPageVisited
from new_year.ny_constants import NyTabBarChallengeView, NYObjects, GuestsQuestsTokens, CHALLENGE_TAB_TO_CAMERA_OBJ
from ny_common.settings import NY_CONFIG_NAME, NYLootBoxConsts
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import ICelebrityController
from account_helpers.AccountSettings import AccountSettings, NY_CAT_PAGE_VISITED, NY_GUEST_ACTIVITY_SHOWN
if typing.TYPE_CHECKING:
    from ny_common.GuestsQuestsConfig import GuestQuest
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quests_celebrity_model import NewYearQuestsCelebrityModel
_TAB_NAME_TO_SERVER_GUEST_ID = {NyTabBarChallengeView.GUEST_A: GuestsQuestsTokens.GUEST_A,
 NyTabBarChallengeView.GUEST_CAT: GuestsQuestsTokens.GUEST_C}
_SERVER_GUEST_ID_TO_TAB_NAME = {v:k for k, v in _TAB_NAME_TO_SERVER_GUEST_ID.iteritems()}
_WAITING_NAME = 'newYear/openActivity'

def tooltipDataExtractor(data):
    return data[0]


class NewYearChallengeGuest(NyHistoryPresenter):
    __slots__ = ('_tooltips', '__guestName', '__questIndex', '__questIdToIdx', '__lastAvailableQuestID', '__blur')
    __celebrityController = dependency.descriptor(ICelebrityController)
    __service = dependency.descriptor(ICustomizationService)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NewYearChallengeGuest, self).__init__(viewModel, parentView, soundConfig)
        self._tooltips = {}
        self.__guestName = None
        self.__questIndex = None
        self.__questIdToIdx = {}
        self.__lastAvailableQuestID = None
        self.__blur = None
        return

    @property
    def viewModel(self):
        model = self.getViewModel()
        return model.questsCelebrityModel

    def initialize(self, *args, **kwargs):
        super(NewYearChallengeGuest, self).initialize(self, *args, **kwargs)
        ctx = kwargs.get('ctx', {})
        tabName = ctx.get('tabName')
        self.__guestName = _TAB_NAME_TO_SERVER_GUEST_ID.get(tabName, GuestsQuestsTokens.GUEST_A)
        self.__blur = CachedBlur(blurRadius=0.3)
        isCatTokenReceived = self._nyController.isCatTokenReceived()
        if tabName == NyTabBarChallengeView.GUEST_CAT and isCatTokenReceived and not isCatPageVisited():
            AccountSettings.setUIFlag(NY_CAT_PAGE_VISITED, True)
        self._tooltips.clear()
        self.__questIdToIdx.clear()
        self.__lastAvailableQuestID = None
        self.__fillModel()
        self.__updateBonus()
        self.__updateBlur()
        return

    def finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(NewYearChallengeGuest, self).finalize()
        return

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
        if contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip():
            return NyGiftMachineTokenTooltip()
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationTooltip(toyID)
        return NyMarketLackTheResTooltip(str(event.getArgument('resourceType')), int(event.getArgument('price'))) if contentID == R.views.lobby.new_year.tooltips.NyMarketLackTheResTooltip() else super(NewYearChallengeGuest, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator(dataExtractor=tooltipDataExtractor)
    def createToolTip(self, event):
        return super(NewYearChallengeGuest, self).createToolTip(event)

    def _getListeners(self):
        listeners = super(NewYearChallengeGuest, self)._getListeners()
        return listeners + ((NyCelebrityStoriesEvent.STORIES_VIEW_CLOSED, self.__onActionViewClosed, EVENT_BUS_SCOPE.DEFAULT),
         (NyCelebrityAnimationEvent.ANIMATION_VIEW_CLOSED, self.__onActionViewClosed, EVENT_BUS_SCOPE.DEFAULT),
         (NyCelebrityStoriesEvent.STORIES_VIEW_OPENED, self.__onActionViewOpened, EVENT_BUS_SCOPE.DEFAULT),
         (NyCelebrityAnimationEvent.ANIMATION_VIEW_OPENED, self.__onActionViewOpened, EVENT_BUS_SCOPE.DEFAULT))

    def _getEvents(self):
        events = super(NewYearChallengeGuest, self)._getEvents()
        serverSettings = self.__lobbyContext.getServerSettings()
        return events + ((self.viewModel.onBuyQuest, self.__onBuyQuest),
         (self.viewModel.onOpenActivity, self.__onOpenActivity),
         (self.viewModel.onShowStylePreview, self.__onShowStylePreview),
         (self.viewModel.onGoToBoxes, self.__onGoToBoxes),
         (self.viewModel.onUpdateBonus, self.__updateBonus),
         (self._nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated),
         (serverSettings.onServerSettingsChange, self.__onServerSettingsChange),
         (self.__celebrityController.onCelebCompletedTokensUpdated, self.__onCompletedTokensChanged))

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(self.__guestName)
            quests = questsHolder.getQuests()
            completedIdx = self.__celebrityController.getCompletedGuestQuestsCount(self.__guestName)
            isExternal = self.__getShopSource() != NYLootBoxConsts.IGB
            lootBoxes = self.__itemsCache.items.tokens.getLootBoxesCountByType()
            if NewYearLootBoxes.PREMIUM in lootBoxes:
                hasBigBoxes = lootBoxes[NewYearLootBoxes.PREMIUM]['total']
            else:
                hasBigBoxes = False
            model.setHasGuestC(self._nyController.isCatTokenReceived())
            model.setCompletedQuestsQuantity(completedIdx)
            model.setTotalQuestsQuantity(len(quests))
            model.setIsWalletAvailable(self.__wallet.isAvailable)
            model.setIsExternal(isExternal and not hasBigBoxes)
            self.__fillCards(model, quests)
            self.__updateBoxesAvailability()

    def __fillCards(self, model, quests):
        cards = model.getQuestsCelebrity()
        cards.clear()
        for idx, quest in enumerate(quests):
            questID = quest.getQuestID()
            if questID is None:
                continue
            currency, price = GuestsQuestsConfigHelper.getQuestPrice(quest)
            resourceBalance = self._nyController.currencies.getResouceBalance(currency)
            self.__questIdToIdx[questID] = idx
            card = NewYearQuestCardModel()
            card.setId(questID)
            card.setPrice(price)
            card.setResource(currency)
            card.setIsNotEnough(price > resourceBalance)
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

    def __getShopSource(self):
        shopConfig = self.__lobbyContext.getServerSettings().getLootBoxShop()
        return shopConfig.get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.IGB)

    def __updateBoxesAvailability(self):
        self.viewModel.setIsBoxesAvailable(self.__lobbyContext.getServerSettings().isLootBoxesEnabled())

    def __updateBlur(self):
        if self.__guestName == GuestsQuestsTokens.GUEST_C and not self._nyController.isCatTokenReceived():
            self.__blur.enable()
        else:
            self.__blur.disable()

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
            Waiting.show(_WAITING_NAME, softStart=True)
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
            backBtnDescrLabel = backport.text(R.strings.ny.celebrityChallenge.backLabel())

            def _backCallback():
                if not self._nyController.isEnabled():
                    event_dispatcher.showHangar()
                else:
                    NewYearNavigation.switchFromStyle(viewAlias=ViewAliases.CELEBRITY_VIEW, objectName=CHALLENGE_TAB_TO_CAMERA_OBJ.get(guestID, NYObjects.CELEBRITY), tabName=guestID, forceShowMainView=True)

            showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=_backCallback, backBtnDescrLabel=backBtnDescrLabel)
            return

    @staticmethod
    def __onGoToBoxes():
        if getRewardKitsCount():
            showLootBoxEntry()
        else:
            showLootBoxBuyWindow()

    def __onBalanceUpdated(self):
        self.__updateCards()

    @server_settings.serverSettingsChangeListener(NY_CONFIG_NAME)
    def __onServerSettingsChange(self, diff):
        self.__updateCards()
        self.__updateBoxesAvailability()

    def __onCompletedTokensChanged(self):
        self.__fillModel()
        self.__updateBlur()

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
            self.__questIndex = questIndex
        elif result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)

    def __onActionViewClosed(self, event):
        if event.ctx['justReceived']:
            self.viewModel.setIsBonusAnimated(True)
            if self.__questIndex in self.__getStyleIdxFromRewards(self.__guestName):
                questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(self.__guestName)
                quests = questsHolder.getQuests()
                quest = questsHolder.getQuestByQuestIndex(self.__questIndex)
                pushNYQuestRewardsMessage({'guestName': self.__guestName,
                 'bonuses': quest.getQuestRewards(),
                 'completedQuestsQuantity': self.__questIndex + 1,
                 'questIndex': self.__questIndex,
                 'totalQuestsQuantity': len(quests)})

    def __onActionViewOpened(self, event):
        Waiting.hide(_WAITING_NAME)

    def __getStyleIdxFromRewards(self, guestName):
        questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(guestName)
        quests = questsHolder.getQuests()
        styleIndexes = []
        for idx, quest in enumerate(quests):
            customizations = quest.getQuestRewards().get('customizations')
            if customizations and customizations[0].get('custType') == 'style':
                styleIndexes.append(idx)

        return styleIndexes

    def __updateBonus(self):
        with self.viewModel.transaction() as model:
            bonusesData = EconomicBonusHelper.getBonusesDataInventory()
            bonusesDataMax = EconomicBonusHelper.getMaxBonuses()
            bonuses = {k:(v, bonusesDataMax[k]) for k, v in bonusesData.iteritems() if k != CREDITS_BONUS}
            activeBonus = bonusesData[CREDITS_BONUS]
            maxActiveBonus = bonusesDataMax[CREDITS_BONUS]
            model.setCurrentActiveBonus(toPrettyCumulativeBonusValue(activeBonus))
            model.setMaxActiveBonus(toPrettyCumulativeBonusValue(maxActiveBonus))
            model.setIsBonusAnimated(False)
            eBonuses = model.getEconomicBonuses()
            eBonuses.clear()
            for bonusName, (value, maxValue) in bonuses.iteritems():
                eBonus = EconomicBonusModel()
                eBonus.setBonusName(bonusName)
                eBonus.setBonusValue(toPrettyCumulativeBonusValue(value))
                eBonus.setMaxBonus(toPrettyCumulativeBonusValue(maxValue))
                eBonuses.addViewModel(eBonus)

            eBonuses.invalidate()
