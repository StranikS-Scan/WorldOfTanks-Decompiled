# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/promo_code_reward_screen/promo_code_reward_screen_view.py
import logging
from collections import deque
from copy import copy
from functools import partial
import typing
from BWUtil import AsyncReturn
from adisp import adisp_process
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.lobby.promo_code_reward_screen.bonuses_sorter import sortBonuses
from gui.server_events.formatters import parseComplexToken
from helpers import dependency
from frameworks.wulf import ViewSettings, WindowFlags, ViewModel
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.promo_code_reward_screen.promo_code_reward_screen_view_model import PromoCodeRewardScreenViewModel
from gui.impl.lobby.collection.tooltips.collection_item_tooltip_view import CollectionItemTooltipView
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.promo_code_reward_screen import parseToken, isLootboxesExtensionAvailable, isPromoCodeToken, REWARDS_SOURCE_INVOICE
from gui.impl.lobby.promo_code_reward_screen.bonuses import getRewardsBonusPacker, splitBonuses, QUESTS_BUNUS_NAME
from gui.impl.lobby.promo_code_reward_screen.metadata_fetcher import MetadataFetcher
from gui.impl.lobby.promo_code_reward_screen.quest_conditions_tooltip import QuestConditionsTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, getMergedBonusesFromDicts, SimpleBonus
from gui.server_events.events_dispatcher import showMissions
from gui.shared.bonuses_sorter import bonusesSortKeyFunc
from shared_utils import awaitNextFrame
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, AsyncEvent, AsyncScope, wg_await, TimeoutError
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
_logger = logging.getLogger(__name__)
_SHOW_TO_TASKS_BUTTON_TAG = 'show_to_tasks_button'

class PromoCodeRewardScreenView(ViewImpl):

    def __init__(self, token, rewardsData, rewardsSource):
        settings = ViewSettings(R.views.lobby.promo_code_reward_screen.PromoCodeRewardScreenView())
        settings.model = PromoCodeRewardScreenViewModel()
        self.__tooltipData = {}
        self.__token = token
        self.__rewardsData = copy(rewardsData)
        self.__rewardsSource = rewardsSource
        super(PromoCodeRewardScreenView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PromoCodeRewardScreenView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PromoCodeRewardScreenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.getTooltipData(event)
        if isLootboxesExtensionAvailable():
            if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip() and tooltipData:
                from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
                lootBoxID = self.getTooltipData(event)['lootBoxID']
                itemsCache = dependency.instance(IItemsCache)
                lootBox = itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
                return LootboxTooltip(lootBox)
            if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.CompensationTooltip() and tooltipData:
                from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.compensation_tooltip import LootBoxesCompensationTooltip
                return LootBoxesCompensationTooltip(*tooltipData.specialArgs)
        if contentID == R.views.lobby.collection.tooltips.CollectionItemTooltipView() and tooltipData:
            return CollectionItemTooltipView(*tooltipData.specialArgs)
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            rewardListName = event.getArgument('rewardListName')
            if rewardListName == PromoCodeRewardScreenViewModel.QUEST_REWARDS_NAME:
                inBoxCount = int(event.getArgument('inBoxCount', 0))
                totalRewards = len(self.viewModel.getQuestRewards())
                packedBonuses = self.viewModel.getQuestRewards()[totalRewards - inBoxCount:]
            else:
                packedBonuses = self.viewModel.getRewards()[PromoCodeRewardScreenViewModel.MAX_REWARDS:]
            return AdditionalRewardsTooltip(packedBonuses)
        if contentID == R.views.lobby.tooltips.QuestConditionsTooltip():
            codeDescr = self.__getPromocodeDescr()
            quests = self.__getQuestsInfo(codeDescr.quests)
            return QuestConditionsTooltip(quests)
        return super(PromoCodeRewardScreenView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        index = event.getArgument(PromoCodeRewardScreenViewModel.ARG_REWARD_INDEX)
        return self.__tooltipData.get(index, None)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.navigateToQuests, self.__navigateToQuests))

    @adisp_process
    def _onLoading(self, *args, **kwargs):
        super(PromoCodeRewardScreenView, self)._onLoading(*args, **kwargs)
        _logger.debug('RewardsData=%s', self.__rewardsData)
        tokenDescr = parseToken(self.__token)
        codeDescr = self.__getPromocodeDescr()
        if codeDescr is None or codeDescr.id != tokenDescr.codeId:
            _logger.error('Problem with reward screen %s description! Can not open reward screen!', tokenDescr.codeId)
            return
        else:
            preparedRewards = self.__prepareRewards(self.__rewardsData, self.__rewardsSource)
            rewards = []
            for bonusType, bonusValue in preparedRewards.items():
                bonus = getNonQuestBonuses(bonusType, bonusValue)
                rewards.extend(bonus)

            quests = self.__getQuestsInfo(codeDescr.quests)
            if quests:
                rewards.append(SimpleBonus(QUESTS_BUNUS_NAME, ''))
            rewards = splitBonuses(mergeBonuses(rewards))
            rewards = sortBonuses(rewards)
            if not rewards:
                yield awaitNextFrame()
                self.destroyWindow()
                return
            with self.viewModel.transaction() as model:
                model.setDescription(codeDescr.description)
                model.setTitle(codeDescr.title or backport.text(R.strings.awards.promoCodeRewardScreen.title))
                model.setSubtitle(codeDescr.subtitle)
                model.setBackgroundImage(codeDescr.background or '')
                model.setQuestsDescription(codeDescr.questsDescription)
                showToTasksButton = False
                if codeDescr.tags and _SHOW_TO_TASKS_BUTTON_TAG in codeDescr.tags:
                    showToTasksButton = True
                model.setHasQuests(bool(quests))
                model.setShowToTasksButton(showToTasksButton)
                self.__fillRewardsModel(rewards, model, self.__tooltipData, self.viewModel.MAX_MAIN_REWARDS)
                self.__fillQuestsData(model, quests)
            return

    @staticmethod
    def __filterRewards(rewards):
        for bonuses in rewards:
            bonuses.pop('version', None)
            tokens = bonuses.get('tokens', {})
            filteredTokens = {token:val for token, val in tokens.iteritems() if not (isPromoCodeToken(token) or parseComplexToken(token).isDisplayable)}
            bonuses['tokens'] = filteredTokens

        return rewards

    @staticmethod
    def __prepareRewards(rawRewards, rewardsSource):
        rawRewards = PromoCodeRewardScreenView.__filterRewards(rawRewards)
        rewards = getMergedBonusesFromDicts(rawRewards)
        if isLootboxesExtensionAvailable():
            from gui_lootboxes.gui.bonuses.bonuses_helpers import preformatCompensationValue, preformatStyle
            if rewardsSource == REWARDS_SOURCE_INVOICE:
                preformatCompensationValue(rewards)
            preformatStyle(rewards)
        return rewards

    def __fillRewardsModel(self, rewards, model, tooltipData, maxMainRewards):
        mainRewardsPacker = rewardsPacker = getRewardsBonusPacker()
        tooltipIndex = 0 if tooltipData is None else len(tooltipData)
        mainRewardModels = []
        rewardModels = []
        packer = mainRewardsPacker
        modelsList = mainRewardModels
        counter = 0
        for bonus in (b for b in rewards if b.isShowInGUI()):
            startPos = 0
            changeListFlag = False
            while True:
                bonusList = packer.pack(bonus)
                withTooltips = bonusList and tooltipData is not None
                bTooltipList = packer.getToolTip(bonus) if withTooltips else []
                bContentIdList = packer.getContentId(bonus) if withTooltips else []
                for bIndex in range(startPos, len(bonusList)):
                    bModel = bonusList[bIndex]
                    if counter == maxMainRewards and not changeListFlag:
                        packer = rewardsPacker
                        modelsList = rewardModels
                        startPos = bIndex
                        changeListFlag = True
                        break
                    bModel.setIndex(0)
                    if withTooltips:
                        tooltipIndex = self.__packBonusTooltip(bModel, bIndex, bTooltipList, bContentIdList, tooltipData, tooltipIndex)
                    modelsList.append(bModel)
                    counter += 1
                else:
                    break

        mainRewardModelsArray = model.getMainRewards()
        self.__reorderMainRewards(mainRewardModels, mainRewardModelsArray)
        mainRewardModelsArray.invalidate()
        rewardModelsArray = model.getRewards()
        rewardModelsArray.clear()
        fillViewModelsArray(rewardModels, rewardModelsArray)
        rewardModelsArray.invalidate()
        return

    @staticmethod
    def __packBonusTooltip(bonusModel, bonusIndex, bonusTooltipList, bonusContentIdList, tooltipData, tooltipIndex):
        if tooltipData is None or not bonusTooltipList and not bonusContentIdList:
            return tooltipIndex
        else:
            tooltipIdx = str(tooltipIndex)
            bonusModel.setTooltipId(tooltipIdx)
            if bonusTooltipList:
                tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
            if bonusContentIdList:
                bonusModel.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
            return tooltipIndex + 1

    @staticmethod
    def __reorderMainRewards(modelsList, modelsArray):
        modelsArray.clear()
        if not modelsList:
            return
        orderedList = deque([modelsList[0]])
        leftRewards = modelsList[1:(len(modelsList) - 1) // 2 + 1]
        rightRewards = modelsList[(len(modelsList) - 1) // 2 + 1:]
        for i in leftRewards:
            orderedList.appendleft(i)

        for i in rightRewards:
            orderedList.append(i)

        modelsArray.reserve(len(modelsList))
        for m in orderedList:
            modelsArray.addViewModel(m)

    def __onClose(self):
        self.destroyWindow()

    def __navigateToQuests(self):
        codeDescr = self.__getPromocodeDescr()
        missionID = codeDescr.quests[0] if codeDescr is not None and codeDescr.quests else None
        showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, missionID=missionID)
        self.destroyWindow()
        return

    def __getPromocodeDescr(self):
        parentWindow = self.getWindow()
        return parentWindow.getPromocodeDescr()

    def __fillQuestsData(self, model, quests):
        questsBonuses = []
        for quest in quests:
            questsBonuses.append(quest.getRawBonuses())

        questsBonuses = PromoCodeRewardScreenView.__filterRewards(questsBonuses)
        mergedBonuses = getMergedBonusesFromDicts(questsBonuses)
        rewards = []
        for bonusType, bonusValue in mergedBonuses.items():
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            rewards.extend(bonus)

        rewards = splitBonuses(mergeBonuses(rewards))
        rewards.sort(key=bonusesSortKeyFunc)
        packer = getRewardsBonusPacker()
        questRewards = model.getQuestRewards()
        questRewards.clear()
        packBonusModelAndTooltipData(rewards, questRewards, self.__tooltipData, packer)
        questRewards.invalidate()

    def __getQuestsInfo(self, questsIds):
        eventsCache = dependency.instance(IEventsCache)
        quests = []
        if not questsIds:
            return quests
        else:
            for questsId in questsIds:
                quest = eventsCache.getQuestByID(questsId)
                if quest is None:
                    _logger.error('Quests %s not found!', questsId)
                isAvailable, _ = quest.isAvailable()
                if isAvailable and not quest.isCompleted():
                    quests.append(quest)

            return quests


class PromoCodeRewardScreenViewWindow(LobbyNotificationWindow):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, token, rewardsData, rewardsSource, parent=None):
        super(PromoCodeRewardScreenViewWindow, self).__init__(content=PromoCodeRewardScreenView(token, rewardsData, rewardsSource), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, parent=parent, decorator=None)
        self.__scope = AsyncScope()
        self.__questsDataReadyEvent = AsyncEvent(scope=self.__scope)
        self.__token = token
        self.__codeDescr = None
        return

    @wg_async
    def waitData(self, timeout):
        tokenDescr = parseToken(self.__token)
        if tokenDescr is None:
            _logger.error('Error of parsing token %s', self.__token)
            raise AsyncReturn(False)
        try:
            try:
                self.__codeDescr = None
                yield wg_await(self.__waitData(tokenDescr.codeId), timeout)
            except TimeoutError:
                _logger.warning('TimeoutError due to waiting data for reward screen token %s', self.__token)
                if self.__codeDescr is None:
                    raise AsyncReturn(False)

        finally:
            self._eventsCache.onSyncCompleted -= self.__onSyncCompleted

        raise AsyncReturn(bool(self.__codeDescr))
        return

    def getPromocodeDescr(self):
        return self.__codeDescr

    @wg_async
    def __waitData(self, codeId):
        self.__codeDescr = yield wg_await(MetadataFetcher.fetch(codeId))
        if self.__codeDescr is None:
            raise AsyncReturn(None)
        if not self.__codeDescr.title:
            _logger.error('Field title is not defined for reward screen %s! Can not open reward screen!', codeId)
            self.__codeDescr = None
        if self.__codeDescr is not None and not self.__isQuestsDataReady(self.__codeDescr.quests):
            self._eventsCache.onSyncCompleted += partial(self.__onSyncCompleted, self.__codeDescr.quests)
            self.__questsDataReadyEvent.clear()
            yield wg_await(self.__questsDataReadyEvent.wait())
        return

    def __onSyncCompleted(self, quests):
        if not self.__isQuestsDataReady(quests):
            return
        self.__questsDataReadyEvent.set()

    def __isQuestsDataReady(self, questsIds):
        if not questsIds:
            return True
        quests = self._eventsCache.getAllQuests(lambda q: q.getID() in questsIds)
        return len(quests) == len(questsIds)
