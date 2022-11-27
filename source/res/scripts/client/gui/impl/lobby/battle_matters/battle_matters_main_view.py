# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_main_view.py
import logging
import typing
from account_helpers.AccountSettings import BATTLEMATTERS_SEEN
import BigWorld
import resource_helper
from account_helpers import AccountSettings
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from battle_matters_constants import QuestCardSections, CARDS_CONFIG_XML_PATH
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BattleMattersViewMeta import BattleMattersViewMeta
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_main_view_model import BattleMattersMainViewModel
from gui.impl.gen.view_models.views.lobby.battle_matters.intermediate_quest_model import IntermediateQuestModel
from gui.impl.gen.view_models.views.lobby.battle_matters.quest_view_model import QuestViewModel, State
from gui.impl.lobby.battle_matters.battle_matters_bonus_packer import getBattleMattersBonusPacker, bonusesSort
from gui.impl.lobby.battle_matters.battle_matters_main_reward_view import BattleMattersMainRewardView
from gui.impl.lobby.battle_matters.battle_matters_vehicle_selection_view import BattleMattersVehicleSelectionView
from gui.impl.lobby.battle_matters.battle_matters_paused_view import BattleMattersPausedView
from gui.impl.lobby.battle_matters.tooltips.battle_matters_token_tooltip_view import BattleMattersTokenTooltipView
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showBattleMatters, showBattleMattersMainReward
from gui.shared.event_dispatcher import showDelayedReward, showHangar
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from shared_utils import nextTick
from gui.shared.ClanCache import g_clanCache
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.game_control import IManualController, IBootcampController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import List, Union
    from gui.impl.gen.view_models.views.lobby.battle_matters.quest_progress_model import QuestProgressModel
    from gui.server_events.event_items import BattleMattersQuest, BattleMattersTokenQuest
_logger = logging.getLogger(__name__)

class BattleMattersMissionComponent(InjectComponentAdaptor, BattleMattersViewMeta):
    __slots__ = ()
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    @nextTick
    def updateState(self, openMainRewardView=False, openVehicleSelection=False, openMainView=False, **_):
        self.as_hideViewS()
        self._destroyInjected()
        self._createInjectView(openMainRewardView, openVehicleSelection, openMainView)

    def markVisited(self):
        pass

    def _addInjectContentListeners(self):
        if getattr(self._injectView.viewModel, 'onShowView', None):
            self._injectView.viewModel.onShowView += self._onViewReady
        else:
            self._injectView.onStatusChanged += self._onViewReady
        return

    def _removeInjectContentListeners(self):
        if getattr(self._injectView.viewModel, 'onShowView', None):
            self._injectView.viewModel.onShowView -= self._onViewReady
        else:
            self._injectView.onStatusChanged -= self._onViewReady
        return

    def _makeInjectView(self, openMainRewardView=False, openVehicleSelection=False, openMainView=False):
        if self.__battleMattersController.isPaused():
            return BattleMattersPausedView()
        if openMainView:
            return BattleMattersMainView()
        if openVehicleSelection or self.__battleMattersController.isFinished() and self.__battleMattersController.hasDelayedRewards():
            return BattleMattersVehicleSelectionView()
        return BattleMattersMainRewardView() if not AccountSettings.getCounters(BATTLEMATTERS_SEEN) or openMainRewardView else BattleMattersMainView()

    def _onPopulate(self):
        self.__battleMattersController.onStateChanged += self.__onStateChanged
        self.__checkHint()

    def _destroy(self):
        self.__battleMattersController.onStateChanged -= self.__onStateChanged
        super(BattleMattersMissionComponent, self)._destroy()

    def _onViewReady(self, *args):
        if not args or args[0] == ViewStatus.LOADED:
            self.as_showViewS()

    def __onStateChanged(self):
        controller = self.__battleMattersController
        if controller.isEnabled() and (not controller.isFinished() or controller.hasDelayedRewards()):
            self.updateState()
        else:
            showHangar()

    def __checkHint(self):
        entryPointHint = OnceOnlyHints.BATTLE_MATTERS_ENTRY_POINT_BUTTON_HINT
        hintShowed = self.__settingsCore.serverSettings.getOnceOnlyHintsSetting(entryPointHint, default=False)
        if not hintShowed:
            self.__settingsCore.serverSettings.setOnceOnlyHintsSettings({entryPointHint: True})


class BattleMattersMainView(ViewImpl):
    __slots__ = ('__tooltips', '__questCardsDescriptions')
    __appLoader = dependency.descriptor(IAppLoader)
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __bootcampController = dependency.descriptor(IBootcampController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __manualController = dependency.descriptor(IManualController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_matters.BattleMattersMainView(), flags=ViewFlags.COMPONENT, model=BattleMattersMainViewModel())
        self.__tooltips = {}
        self.__questCardsDescriptions = {}
        super(BattleMattersMainView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersMainView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattleMattersMainView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument('showCount'))
            questIdx = int(event.getArgument(BattleMattersMainViewModel.ARG_QUEST_ID, 1))
            quest = self.__battleMattersController.getQuestByIdx(questIdx - 1)
            bonuses = sorted(quest.getBonuses(), cmp=bonusesSort)
            packer = getBattleMattersBonusPacker()
            packed = []
            for bonus in bonuses[showCount + 1:]:
                packed.extend(packer.pack(bonus))

            return AdditionalRewardsTooltip(packed)
        return BattleMattersTokenTooltipView() if contentID == R.views.lobby.battle_matters.tooltips.BattleMattersTokenTooltipView() else super(BattleMattersMainView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(BattleMattersMainView, self)._initialize(*args, **kwargs)
        self.__readXML()
        self.__update()

    def _getEvents(self):
        return ((self.viewModel.onShowManual, self.__onShowManual),
         (self.viewModel.onRunBootcamp, self.__onRunBootcamp),
         (self.viewModel.onShowMainReward, self.__onShowMainReward),
         (self.viewModel.onShowManualForQuest, self.__onShowManualForQuest),
         (self.viewModel.onShowAnimForQuest, self.__onAnimForQuest),
         (self.viewModel.onSelectDelayedReward, self.__onSelectDelayedReward),
         (self.viewModel.onClose, showHangar),
         (self.__eventsCache.onSyncCompleted, self.__onSyncCompleted))

    @classmethod
    def __getMissionPage(cls):
        return cls.__appLoader.getApp().containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_MISSIONS))

    @staticmethod
    def __onSelectDelayedReward():
        showDelayedReward()

    @staticmethod
    def __onShowMainReward():
        showBattleMattersMainReward()

    def __readXML(self):
        ctx, root = resource_helper.getRoot(CARDS_CONFIG_XML_PATH)
        for ctx, subSection in resource_helper.getIterator(ctx, root):
            cardConfig = {}
            lessonId = subSection.readInt(QuestCardSections.LESSON_ID.value, -1)
            if lessonId >= 0:
                cardConfig[QuestCardSections.LESSON_ID] = lessonId
            swfPath = subSection.readString(QuestCardSections.SWF_PATH.value)
            if swfPath:
                cardConfig[QuestCardSections.SWF_PATH] = swfPath
            self.__questCardsDescriptions[subSection.readInt(QuestCardSections.ID.value)] = cardConfig

    def __onAnimForQuest(self, args):
        questID = args.get(BattleMattersMainViewModel.ARG_QUEST_ID)
        if questID is not None:
            swfName = self.__questCardsDescriptions.get(questID, {}).get(QuestCardSections.SWF_PATH)
            if swfName:
                missionsPage = self.__getMissionPage()
                if missionsPage:
                    missionsPage.as_showBattleMattersAnimationS(swfName, self.__getBattleMattersData())
            else:
                _logger.warning('Quest id=%s does not have swfPath', questID)
        else:
            _logger.warning('__onAnimForQuest: Invalid argument questID')
        return

    def __getBattleMattersData(self):
        name = BigWorld.player().name
        return {'nickName': self.__lobbyContext.getPlayerFullName(name, clanInfo=g_clanCache.clanInfo)}

    def __update(self):
        with self.viewModel.transaction() as model:
            regularQuests = self.__battleMattersController.getRegularBattleMattersQuests()
            self.__updateQuests(model, regularQuests)
            self.__updateQuestProgress(model.questProgress, regularQuests)
            model.setBootcampIsAvailable(self.__bootcampController.canRun())
            model.setIsBootcampCompleted(self.__bootcampController.hasFinishedBootcampBefore())

    def __updateQuestProgress(self, questProgressModel, regularQuests):
        totalQuests = len(regularQuests)
        countCompletedQuests = len(self.__battleMattersController.getCompletedBattleMattersQuests())
        questProgressModel.setTotalQuests(totalQuests)
        questProgressModel.setCountCompleted(countCompletedQuests)
        questProgressModel.setMainRewardReceived(self.__battleMattersController.getFinalQuest().isCompleted())
        questProgressModel.setLastSeenProgress(self.__settingsCore.serverSettings.getBattleMattersQuestWasShowed())
        quests = self.__battleMattersController.getIntermediateQuests()[:-1]
        intermediateQuests = questProgressModel.getIntermediateQuests()
        intermediateQuests.clear()
        for intermediateQuest in quests:
            intermediateQuests.addViewModel(self.__createQuestProgressModel(intermediateQuest))

        intermediateQuests.invalidate()
        self.__settingsCore.serverSettings.setBattleMattersQuestWasShowed(countCompletedQuests)

    def __createQuestProgressModel(self, quest):
        intermediateQuestModel = IntermediateQuestModel()
        intermediateQuestModel.setQuestIdx(quest.getOrder())
        rewardsModel = intermediateQuestModel.getRewards()
        packBonusModelAndTooltipData(quest.getBonuses(), rewardsModel, self.__tooltips, packer=getBattleMattersBonusPacker())
        return intermediateQuestModel

    def __updateQuests(self, model, quests):
        questsModel = model.getQuests()
        questsModel.clear()
        currentQuest = self.__battleMattersController.getCurrentQuest()
        for quest in quests:
            questsModel.addViewModel(self.__createQuestModel(quest, currentQuest))

        questsModel.invalidate()

    def __createQuestModel(self, quest, currentQuest):
        questModel = QuestViewModel()
        idx = quest.getOrder()
        questModel.setIdx(idx)
        questModel.setTitle(quest.getUserName())
        questModel.setDescription(quest.getDescription())
        questModel.setCondition(quest.getConditionLbl())
        questState = State.UNAVAILABLE
        if quest.isCompleted():
            questState = State.DONE
        elif quest.isAvailable().isValid and quest.getOrder() == currentQuest.getOrder():
            questState = State.INPROGRESS
        questModel.setState(questState)
        cardConfig = self.__questCardsDescriptions.get(idx, {})
        questModel.setHasManualPage(cardConfig.get(QuestCardSections.LESSON_ID) is not None)
        questModel.setHasAnimation(cardConfig.get(QuestCardSections.SWF_PATH) is not None)
        currentProgress, maxProgress = self.__battleMattersController.getQuestProgress(quest)
        questModel.setCurrentProgress(currentProgress)
        questModel.setMaxProgress(maxProgress)
        bonuses = sorted(quest.getBonuses(), cmp=bonusesSort)
        packBonusModelAndTooltipData(bonuses, questModel.getRewards(), self.__tooltips, packer=getBattleMattersBonusPacker())
        return questModel

    def __onShowManual(self):
        self.__manualController.show(backCallback=showBattleMatters)

    def __onRunBootcamp(self):
        if self.__bootcampController.canRun():
            self.__bootcampController.runBootcamp()

    def __onShowManualForQuest(self, args):
        questID = args.get(BattleMattersMainViewModel.ARG_QUEST_ID)
        if questID is not None:
            lessonID = self.__questCardsDescriptions.get(questID, {}).get(QuestCardSections.LESSON_ID)
            if lessonID is not None:
                self.__manualController.show(lessonID, backCallback=showBattleMatters)
            else:
                _logger.warning('Quest id=%s does not have lessonId for manual', questID)
        else:
            _logger.warning('__onShowManualForQuest: Invalid argument questID')
        return

    def __onSyncCompleted(self):
        self.__update()
