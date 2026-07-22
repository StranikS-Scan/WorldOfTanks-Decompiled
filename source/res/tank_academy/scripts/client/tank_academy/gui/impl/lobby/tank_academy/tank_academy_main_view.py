# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tank_academy_main_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from frameworks.wulf.gui_constants import WindowStatus
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.shared.event_dispatcher import showHangar, showBrowserOverlayView, selectVehicleInHangar, runTankAcademyChain
from tank_academy.gui.impl.lobby.tank_academy.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ITankAcademyController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.tutorial import ITutorialLoader
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_group_model import QuestGroupModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_progress_model import QuestProgressModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_main_view_model import TankAcademyMainViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_view_model import QuestViewModel, State
from tank_academy.gui.impl.lobby.tank_academy.tank_academy_rewards_view import TankAcademyRewardsViewWindow
from tank_academy.gui.impl.lobby.tank_academy.tank_academy_tutorials import getQuestTutorialChapterID, hasQuestTutorial
from tank_academy.gui.shared.bonus_packers import packBonusModelAndTooltipData
from tank_academy.gui.shared.event_dispatcher import showTankAcademyVehicleSelection
if typing.TYPE_CHECKING:
    from typing import List
    from gui.server_events.event_items import ITankAcademyQuest, ITankAcademyGroup
_logger = logging.getLogger(__name__)

class TankAcademyMainView(ViewImpl):
    __slots__ = ('__tooltips', '__currentQuestIdx')
    __tankAcademyController = dependency.descriptor(ITankAcademyController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __tutorialLoader = dependency.descriptor(ITutorialLoader)

    def __init__(self):
        settings = ViewSettings(R.views.tank_academy.lobby.tank_academy.TankAcademyMainView(), flags=ViewFlags.VIEW, model=TankAcademyMainViewModel())
        self.__tooltips = {}
        self.__currentQuestIdx = 0
        super(TankAcademyMainView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankAcademyMainView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(TankAcademyMainView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument(TankAcademyMainViewModel.BOX_TOOLTIP_ARG_SHOW_COUNT, 0))
            questGroupIdx = int(event.getArgument(TankAcademyMainViewModel.BOX_TOOLTIP_ARG_QUEST_GROUP_INDEX, 0))
            questIdx = int(event.getArgument(TankAcademyMainViewModel.BOX_TOOLTIP_ARG_QUEST_INDEX, 0))
            groups = self.getViewModel().getQuest_groups()
            if questGroupIdx < len(groups):
                quests = groups[questGroupIdx].getQuests()
                if questIdx < len(quests):
                    quest = quests[questIdx]
                    return AdditionalRewardsTooltip(quest.getRewards()[showCount:])
        return super(TankAcademyMainView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(TankAcademyMainView, self)._initialize(*args, **kwargs)
        if self.__tutorialLoader.isRunning:
            self.__tutorialLoader.stopTutorial()
        self.__currentQuestIdx = self.__getCurrentQuestIdx()
        self.__update()

    def _finalize(self):
        self.soundManager.playSound(backport.sound(R.sounds.ta_progress_bar_stop()))
        super(TankAcademyMainView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, showHangar),
         (self.viewModel.onShowInfoPage, self.__onShowInfoPage),
         (self.viewModel.onShowQuestTutorial, self.__onShowQuestTutorial),
         (self.viewModel.onShowQuestVehicle, self.__onShowQuestVehicle),
         (self.viewModel.onUseQuestToken, self.__onUseQuestToken),
         (self.viewModel.onViewVehicles, self.__onViewVehicles),
         (self.viewModel.onSeenAnimation, self.__onSeenAnimation),
         (self.__eventsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.gui.windowsManager.onWindowStatusChanged, self.__onWindowStatusChanged),
         (self.__tankAcademyController.onStateChanged, self.__onStateChanged))

    def __getCurrentQuestIdx(self):
        currentQuest = self.__tankAcademyController.getCurrentQuest()
        return currentQuest.getOrder() if currentQuest else len(self.__tankAcademyController.getCompletedTankAcademyQuests())

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        window = self.gui.windowsManager.getWindow(uniqueID)
        isTARewardView = isinstance(window, TankAcademyRewardsViewWindow)
        if isTARewardView:
            if newStatus == WindowStatus.LOADING:
                self.viewModel.setIsRewardsViewOpen(True)
            elif newStatus == WindowStatus.DESTROYING:
                self.viewModel.setIsRewardsViewOpen(False)

    def __update(self):
        self.__tooltips.clear()
        with self.viewModel.transaction() as model:
            currentQuestIdx = self.__getCurrentQuestIdx()
            model.setIsRewardsViewOpen(self.__currentQuestIdx != currentQuestIdx)
            model.setUnobtainedVehiclesCount(len(self.__tankAcademyController.getDelayedRewardCurrencyTokens()))
            self.__currentQuestIdx = currentQuestIdx
            questGroups = self.__tankAcademyController.getTankAcademyQuestGroups()
            currentQuest = self.__tankAcademyController.getCurrentQuest()
            lastSeenQuestIdx = self.__getLastSeenQuestIdx()
            self.__fillQuestGroups(model, questGroups, currentQuest, lastSeenQuestIdx)
            totalQuestsCount = self.__tankAcademyController.getCountTankAcademyQuests()
            completedQuestsCount = self.__tankAcademyController.getCompletedTankAcademyQuestsCount()
            self.__fillQuestProgress(model.questProgress, totalQuestsCount, completedQuestsCount, lastSeenQuestIdx)
            currentQuestProgress, _ = self.__tankAcademyController.getQuestProgress(currentQuest)
            self.__updateLastSeenQuestProgress(currentQuestProgress)

    def __fillQuestGroups(self, model, questGroups, currentQuest, lastSeenQuestIdx):
        questGroupModelArray = model.getQuest_groups()
        questGroupModelArray.clear()
        questIdx = 0
        for questGroup in questGroups:
            questGroupModel = QuestGroupModel()
            quests = self.__tankAcademyController.getTankAcademyQuestsByGroup(questGroup)
            totalQuestsCount = len(quests)
            completedQuestsCount = len([ quest for quest in quests if quest.isCompleted() ])
            lastSeenProgress = lastSeenQuestIdx - questIdx
            if lastSeenProgress > totalQuestsCount:
                lastSeenProgress = totalQuestsCount
            elif lastSeenProgress < 0:
                lastSeenProgress = 0
            self.__fillQuestProgress(questGroupModel.questProgress, totalQuestsCount, completedQuestsCount, lastSeenProgress)
            questModelArray = questGroupModel.getQuests()
            for quest in quests:
                questModelArray.addViewModel(self.__createQuestViewModel(quest, currentQuest, questIdx, lastSeenQuestIdx))
                questIdx += 1

            questGroupModelArray.addViewModel(questGroupModel)

        questGroupModelArray.invalidate()

    def __fillQuestProgress(self, model, totalQuestsCount, completedQuestsCount, lastSeenProgress):
        model.setTotalQuests(totalQuestsCount if totalQuestsCount > 0 else 0)
        model.setCountCompleted(completedQuestsCount if completedQuestsCount > 0 else 0)
        model.setLastSeenProgress(lastSeenProgress)

    def __createQuestViewModel(self, quest, currentQuest, questIdx, lastSeenQuestIdx):
        questModel = QuestViewModel()
        number = quest.getOrder()
        questModel.setNumber(number)
        questModel.setTitle(quest.getUserName())
        questModel.setDescription(quest.getDescription())
        questModel.setCondition(quest.getConditionLbl())
        questModel.setHasTutorial(hasQuestTutorial(quest))
        questState = State.UNAVAILABLE
        currentQuestNumber = currentQuest.getOrder() if currentQuest else None
        if quest.isCompleted() and (currentQuestNumber is None or number < currentQuestNumber):
            questState = State.DONE
        elif number == currentQuestNumber:
            questState = State.INPROGRESS
        questModel.setState(questState)
        currentProgress, maxProgress = self.__tankAcademyController.getQuestProgress(quest)
        if questIdx < lastSeenQuestIdx and quest.isCompleted():
            questModel.setLastSeenProgress(maxProgress)
        elif questIdx == lastSeenQuestIdx:
            questModel.setLastSeenProgress(self.__getLastSeenQuestProgress())
        questModel.setCurrentProgress(currentProgress)
        questModel.setMaxProgress(maxProgress)
        packBonusModelAndTooltipData(quest.getBonuses(), questModel.getRewards(), self.__tooltips)
        return questModel

    def __getOfferTokenByQuestNumber(self, questNumber):
        quest = self.__tankAcademyController.getQuestByIdx(questNumber)
        if quest is None:
            _logger.error('There is no quest for idx %d', questNumber)
            return
        bonuses = quest.getBonuses()
        selectableBonus = first((bonus for bonus in bonuses if bonus.getName() == SELECTABLE_BONUS_NAME))
        if selectableBonus is None:
            _logger.error('There is no selectable bonus for questId %s', quest.getID())
            return
        else:
            return first(selectableBonus.getValue().iterkeys())

    def __onShowInfoPage(self):
        showBrowserOverlayView(GUI_SETTINGS.tankAcademyInfoPageURL, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def __onShowQuestTutorial(self, args):
        questNumber = args.get(TankAcademyMainViewModel.ARG_SHOW_QUEST_TUTORIAL)
        if questNumber is None:
            _logger.error('questNumber is missing')
            return
        else:
            quest = self.__tankAcademyController.getQuestByIdx(int(questNumber) - 1)
            if quest is None:
                _logger.error('There is no quest for idx %d', int(questNumber) - 1)
                return
            chapterID = getQuestTutorialChapterID(quest)
            if chapterID is None:
                _logger.error('There is no tutorial chapter for questId %s', quest.getID())
                return
            runTankAcademyChain(chapterID, reloadIfRun=True, restoreIfRun=False, isStopForced=True, showWaiting=False)
            return

    def __onShowQuestVehicle(self, args):
        questNumber = args.get(TankAcademyMainViewModel.ARG_SHOW_QUEST_VEHICLE)
        if questNumber is None:
            _logger.error('questNumber is missing')
            return
        else:
            tokenID = self.__getOfferTokenByQuestNumber(int(questNumber) - 1)
            if tokenID is None:
                _logger.error('There is no token for questNumber %s', questNumber)
                return
            vehicle = self.__tankAcademyController.getSelectedVehicle(tokenID)
            if vehicle is None:
                _logger.error('There is no vehicle for offerToken %s', tokenID)
                return
            selectVehicleInHangar(vehicle.intCD)
            return

    def __onUseQuestToken(self, args):
        questNumber = args.get(TankAcademyMainViewModel.ARG_USE_QUEST_TOKEN)
        if questNumber is None:
            _logger.error('questNumber is missing')
            return
        else:
            tokenID = self.__getOfferTokenByQuestNumber(int(questNumber) - 1)
            if tokenID is None:
                _logger.error('There is no token for questNumber %s', questNumber)
                return
            showTankAcademyVehicleSelection(tokenID)
            return

    def __onViewVehicles(self):
        showTankAcademyVehicleSelection()

    def __onSeenAnimation(self):
        completedQuestsCount = self.__tankAcademyController.getCompletedTankAcademyQuestsCount()
        self.__updateLastSeenQuestIdx(completedQuestsCount)

    def __onSyncCompleted(self):
        self.__update()

    def __onStateChanged(self, *_, **__):
        self.__update()

    def __updateLastSeenQuestIdx(self, idx):
        self.__settingsCore.serverSettings.setBattleMattersQuestWasShowed(idx)

    def __getLastSeenQuestIdx(self):
        return self.__settingsCore.serverSettings.getBattleMattersQuestWasShowed()

    def __updateLastSeenQuestProgress(self, progress):
        self.__settingsCore.serverSettings.setBattleMattersQuestProgress(progress)

    def __getLastSeenQuestProgress(self):
        return self.__settingsCore.serverSettings.getBattleMattersQuestProgress()
