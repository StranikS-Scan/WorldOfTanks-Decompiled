# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_quests_view.py
from operator import attrgetter
from enum import Enum
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EarlyAccess
from early_access_common import EARLY_ACCESS_POSTPR_KEY
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.view.lobby.techtree.sound_constants import TECHTREE_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.early_access.early_access_quests_view_model import EarlyAccessQuestsViewModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_chapter_model import EarlyAccessChapterModel, ChapterState
from gui.impl.gen.view_models.views.lobby.early_access.early_access_quest_model import EarlyAccessQuestModel, VehicleModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_state_enum import State
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.early_access.shared.bonus_packers import getEarlyAccessBonusPacker
from gui.impl.lobby.early_access.tooltips.early_access_currency_tooltip_view import EarlyAccessCurrencyTooltipView
from gui.impl.lobby.early_access.tooltips.early_access_state_tooltip import EarlyAccessStateTooltipView
from gui.impl.lobby.early_access.early_access_window_events import showEarlyAccessVehicleView, showEarlyAccessInfoPage
from gui.shared.missions.packers.events import BattleQuestUIDataPacker
from gui.shared.event_dispatcher import showHangar
from gui.server_events.bonuses import CreditsBonus
from gui.shared.missions.packers.events import packQuestBonusModelAndTooltipData
from gui.shared.missions.packers.bonus import SimpleBonusUIPacker
from gui.shared.money import Currency
from items.vehicles import getVehicleType, getVehicleClassFromVehicleType
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEarlyAccessController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from typing import Callable
    from frameworks.wulf import ViewEvent, Window, Array

class EarlyAccessQuestsView(ViewImpl):
    __slots__ = ('__tooltipData', '__currQuestsInProgressID', '__isPostprActive', '__isHavePostprVehicle', '__remainTokensCount', '__receivedTokensForQuests')
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = TECHTREE_SOUND_SPACE

    class QuestsViewState(Enum):
        POSTPROGRESSION = 0
        CYCLE = 1

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = EarlyAccessQuestsViewModel()
        super(EarlyAccessQuestsView, self).__init__(settings)
        self.__tooltipData = {}
        self.__currQuestsInProgressID = dict()
        self.__isPostprActive = False
        self.__isHavePostprVehicle = False
        self.__remainTokensCount = 0
        self.__receivedTokensForQuests = 0

    @property
    def viewModel(self):
        return super(EarlyAccessQuestsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(EarlyAccessQuestsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        missionParams = tooltipId.rsplit(':', 1)
        if len(missionParams) != 2:
            return None
        else:
            questId, id = missionParams
            return self.__tooltipData.get(questId, {}).get(id)

    def createToolTipContent(self, event, contentID):
        lootBoxRes = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes').dyn('tooltips').dyn('LootboxTooltip')
        if lootBoxRes.exists() and contentID == lootBoxRes():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            lootBoxID = self.getTooltipData(event)['lootBoxID']
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        if contentID == R.views.lobby.early_access.tooltips.EarlyAccessCurrencyTooltipView():
            return EarlyAccessCurrencyTooltipView()
        return EarlyAccessStateTooltipView(event.getArgument('state'), event.getArgument('id')) if contentID == R.views.lobby.early_access.tooltips.EarlyAccessSimpleTooltipView() else super(EarlyAccessQuestsView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(EarlyAccessQuestsView, self)._initialize(*args, **kwargs)
        self.__earlyAccessCtrl.hangarFeatureState.enter(self.layoutID)

    def _finalize(self):
        self.__earlyAccessCtrl.hangarFeatureState.exit(self.layoutID)
        super(EarlyAccessQuestsView, self)._finalize()

    def _getEvents(self):
        return ((self.__earlyAccessCtrl.onUpdated, self.__onUpdated),
         (self.__earlyAccessCtrl.onQuestsUpdated, self.__updateData),
         (self.__earlyAccessCtrl.onBalanceUpdated, self.__onBalanceUpdated),
         (self.viewModel.onClose, self.__closeView),
         (self.viewModel.goToVehicle, self.__goToVehicle),
         (self.viewModel.goToInfo, self.__goToInfo))

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessQuestsView, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __closeView(self):
        self.destroy()
        showHangar()

    def __goToVehicle(self):
        self.__earlyAccessCtrl.hangarFeatureState.enter(R.views.lobby.early_access.EarlyAccessVehicleView(), activateVehicleState=True)
        self.destroy()
        showEarlyAccessVehicleView()

    def __goToInfo(self):
        showEarlyAccessInfoPage()

    def __getKeyByCycleID(self, cycleID):
        return self.QuestsViewState.POSTPROGRESSION if cycleID == EARLY_ACCESS_POSTPR_KEY else self.QuestsViewState.CYCLE

    def __onUpdated(self):
        ctrl = self.__earlyAccessCtrl
        if not ctrl.isQuestActive():
            self.__closeView()
            return
        self.__updateData(isNeedSettingsUpdate=False)

    def __onBalanceUpdated(self):
        self.__updateData(isNeedSettingsUpdate=False)

    def __updateData(self, isNeedSettingsUpdate=True):
        ctrl = self.__earlyAccessCtrl
        earlyAccessState = ctrl.getState()
        self.__isPostprActive = earlyAccessState == State.POSTPROGRESSION
        self.__isHavePostprVehicle = ctrl.hasPostprogressionVehicle()
        self.__calculateUserBuyQuestTokens()
        self.__receivedTokensForQuests = ctrl.getReceivedTokensForQuests()
        with self.getViewModel().transaction() as model:
            model.setState(earlyAccessState.value)
            startProgressionTime, endProgressionTime = ctrl.getProgressionTimes()
            _, endSeasonTime = ctrl.getSeasonInterval()
            model.setToTimestamp(endProgressionTime if earlyAccessState == State.ACTIVE else endSeasonTime)
            model.setFromTimestamp(startProgressionTime)
            self.__updateChapters(model, isNeedSettingsUpdate)

    def __updateChapters(self, model, isNeedSettingsUpdate):
        ctrl = self.__earlyAccessCtrl
        currentSeason = ctrl.getCurrentSeason()
        chaptersArray = model.getChapters()
        questsArray = model.getQuests()
        chaptersArray.clear()
        questsArray.clear()
        self.__currQuestsInProgressID.update({self.QuestsViewState.POSTPROGRESSION: set(),
         self.QuestsViewState.CYCLE: set()})
        isPrevChapterFinished = True
        cycles = sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID')) if currentSeason else []
        for cycle in cycles[:-1]:
            isChapterFinished = self.__updateChapter(chaptersArray, questsArray, str(cycle.ID), cycle.startDate, isPrevChapterFinished, isNeedSettingsUpdate)
            isPrevChapterFinished = isChapterFinished

        isPrevChapterFinished = True
        postprStartTime = self.__getPostprogressionQuestsStartTime()
        if postprStartTime is not None:
            self.__updateChapter(chaptersArray, questsArray, EARLY_ACCESS_POSTPR_KEY, postprStartTime, isPrevChapterFinished, isNeedSettingsUpdate)
        chaptersArray.invalidate()
        return

    def __updateChapter(self, chaptersArray, questsArray, cycleID, startDate, isPrevChapterFinished, isNeedSettingsUpdate):
        chapter = EarlyAccessChapterModel()
        isChapterFinished = self.__updateQuests(questsArray, cycleID, chapter, startDate, isPrevChapterFinished, isNeedSettingsUpdate)
        chapter.setId(cycleID)
        chaptersArray.addViewModel(chapter)
        return isChapterFinished

    def __updateQuests(self, questsArray, cycleID, chapter, startDate, isPrevChapterFinished, isNeedSettingsUpdate):
        isShowTokens = cycleID != EARLY_ACCESS_POSTPR_KEY
        ctrl = self.__earlyAccessCtrl
        nowTime = time_utils.getServerUTCTime()
        totalChapterTokens = self.__performChapterCalculations(self.__totalChapterTokensCounter, cycleID)
        completedQuests = self.__performChapterCalculations(self.__completedQuestsCounter, cycleID)
        totalQuests = sum((1 for _ in ctrl.iterCycleProgressionQuests(cycleID)))
        receivedChapterShowTokens = min(max(self.__receivedTokensForQuests - totalChapterTokens, self.__receivedTokensForQuests), totalChapterTokens)
        chapterLeftTokens = totalChapterTokens - receivedChapterShowTokens
        totalChapterShowTokens = totalChapterTokens
        if self.__remainTokensCount < chapterLeftTokens:
            totalChapterShowTokens = receivedChapterShowTokens + self.__remainTokensCount
        isChapterFinished = False
        if self.__isPostprogressionFlowStates(cycleID):
            if completedQuests == totalQuests:
                state = ChapterState.COMPLETED
            else:
                state = ChapterState.DISABLED
        else:
            isChapterFinished = bool(completedQuests == totalQuests)
            isChapterDisabled = not isPrevChapterFinished or startDate > nowTime
            state = ChapterState.ACTIVE
            if isChapterDisabled:
                state = ChapterState.DISABLED
            elif isChapterFinished:
                state = ChapterState.COMPLETED
        buf = totalChapterShowTokens
        for quest in ctrl.iterCycleProgressionQuests(cycleID):
            tokensForQuest = ctrl.getTokensForQuest(quest.getID())
            compensateTokensCount = max(tokensForQuest - buf, 0)
            buf = max(buf - tokensForQuest, 0)
            self.__fillQuestModel(questsArray, quest, cycleID, compensateTokensCount, state)

        questsArray.invalidate()
        if totalChapterShowTokens <= 0 or self.__remainTokensCount <= 0:
            isShowTokens = False
        chapter.setState(state)
        chapter.setTotalQuests(totalQuests)
        chapter.setShowTokens(isShowTokens)
        chapter.setTotalTokens(totalChapterShowTokens)
        chapter.setReceivedTokens(receivedChapterShowTokens)
        prevCompletedQuests = self.__getCompletedQuests(cycleID)
        chapter.setCompletedQuestsNew(prevCompletedQuests)
        chapter.setCompletedQuestsAll(completedQuests)
        if isNeedSettingsUpdate:
            self.__saveCompletedQuests(cycleID, completedQuests)
        self.__remainTokensCount = max(0, self.__remainTokensCount - chapterLeftTokens)
        self.__receivedTokensForQuests -= receivedChapterShowTokens
        return isChapterFinished

    def __completedQuestsCounter(self, quest):
        return quest.isCompleted()

    def __totalChapterTokensCounter(self, quest):
        ctrl = self.__earlyAccessCtrl
        return ctrl.getTokensForQuest(quest.getID())

    def __recievedChapterTokensCounter(self, quest):
        ctrl = self.__earlyAccessCtrl
        return ctrl.getTokensForQuest(quest.getID()) if quest.isCompleted() else 0

    def __performChapterCalculations(self, func, cycleID):
        ctrl = self.__earlyAccessCtrl
        return sum(map(func, ctrl.iterCycleProgressionQuests(cycleID)))

    def __isPostprogressionFlowStates(self, cycleID):
        nowTime = time_utils.getServerUTCTime()
        _, endProgressTime = self.__earlyAccessCtrl.getProgressionTimes()
        return cycleID != EARLY_ACCESS_POSTPR_KEY and (self.__isPostprActive or nowTime > endProgressTime) or cycleID == EARLY_ACCESS_POSTPR_KEY and not self.__isHavePostprVehicle

    def __calculateUserBuyQuestTokens(self):
        ctrl = self.__earlyAccessCtrl
        onlyBuyTokensCount = ctrl.getTotalVehiclesPrice() - ctrl.getReceivedTokensCount()
        self.__remainTokensCount = max(onlyBuyTokensCount, 0)

    def __addCompensationBonus(self, questModel, quest, packer, compensateTokensCount):
        compensationCredits = self.__earlyAccessCtrl.getTokenCompensation(Currency.CREDITS).credits * compensateTokensCount
        packQuestBonusModelAndTooltipData(SimpleBonusUIPacker(), questModel.getBonuses(), quest, tooltipData=packer.getTooltipData(), questBonuses=[CreditsBonus(Currency.CREDITS, compensationCredits, isCompensation=True)])

    def __fillQuestModel(self, questsArray, quest, cycleID, compensateTokensCount, chapterState):
        ctrl = self.__earlyAccessCtrl
        questGroupKey = self.__getKeyByCycleID(cycleID)
        questsInProgress = self.__currQuestsInProgressID.get(questGroupKey)
        tokensForQuest = ctrl.getTokensForQuest(quest.getID())
        vehicleType, minLvl, maxLvl = ctrl.getRequiredVehicleTypeAndLevelsForQuest(quest.getID())
        packer = BattleQuestUIDataPacker(quest, bonusPackerGetter=getEarlyAccessBonusPacker)
        questModel = packer.pack(model=EarlyAccessQuestModel())
        if compensateTokensCount > 0 and compensateTokensCount == tokensForQuest:
            self.__addCompensationBonus(questModel, quest, packer, compensateTokensCount)
        questModel.setChapterId(cycleID)
        questModel.setTokensForCompletion(tokensForQuest - compensateTokensCount)
        questModel.setVehicleType(vehicleType)
        questModel.setMinVehicleLvl(minLvl)
        questModel.setMaxVehicleLvl(maxLvl)
        if cycleID == EARLY_ACCESS_POSTPR_KEY:
            self.__fillRequiredPostprogressionVehicles(questModel)
        if self.__isPostprogressionFlowStates(cycleID):
            if quest.isCompleted():
                questModel.setStatus(EventStatus.DONE)
            else:
                questModel.setStatus(EventStatus.LOCKED)
        else:
            if not questsInProgress:
                questsInProgress.add(quest.getID())
            if quest.isCompleted() and quest.getID() in questsInProgress:
                questModel.setStatus(EventStatus.DONE)
                questsInProgress.remove(quest.getID())
            if quest.getID() in questsInProgress and chapterState != ChapterState.DISABLED:
                questModel.setStatus(EventStatus.ACTIVE)
            elif not quest.isCompleted():
                questModel.setStatus(EventStatus.LOCKED)
        self.__tooltipData[quest.getID()] = packer.getTooltipData()
        questsArray.addViewModel(questModel)

    def __fillRequiredPostprogressionVehicles(self, questModel):
        requiredVehiclesArray = questModel.getRequiredVehicles()
        for vehicleCD in self.__earlyAccessCtrl.getPostProgressionVehicles():
            vehicleModel = VehicleModel()
            vehicle = getVehicleType(vehicleCD)
            vName = vehicle.shortUserString
            vClass = getVehicleClassFromVehicleType(vehicle)
            vehicleModel.setName(vName)
            vehicleModel.setType(vClass)
            requiredVehiclesArray.addViewModel(vehicleModel)

        requiredVehiclesArray.invalidate()

    def __saveCompletedQuests(self, cycleID, completedQuests):
        settings = AccountSettings.getEarlyAccess(EarlyAccess.PREV_COMPLETED_QUESTS)
        settings[cycleID] = completedQuests
        AccountSettings.setEarlyAccess(EarlyAccess.PREV_COMPLETED_QUESTS, settings)

    def __getCompletedQuests(self, cycleID):
        settings = AccountSettings.getEarlyAccess(EarlyAccess.PREV_COMPLETED_QUESTS)
        return settings.get(cycleID, 0)

    def __getPostprogressionQuestsStartTime(self):
        questIter = self.__earlyAccessCtrl.iterCycleProgressionQuests(EARLY_ACCESS_POSTPR_KEY)
        quest = next(questIter, None)
        return None if not quest else quest.getStartTime()
