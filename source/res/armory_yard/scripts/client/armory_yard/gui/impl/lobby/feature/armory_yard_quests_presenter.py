# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_quests_presenter.py
import logging
from operator import attrgetter
from account_helpers.AccountSettings import ArmoryYard, AccountSettings
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.shared.missions.packers.events import BattleQuestUIDataPacker
from gui.shared.view_helpers.blur_manager import CachedBlur
from Event import SuspendableEventSubscriber
from helpers import dependency, time_utils
from skeletons.gui.game_control import IArmoryYardController
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_chapter_model import ArmoryYardChapterModel, ChapterState, ChapterTokenState
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_quest_model import ArmoryYardQuestModel
from armory_yard.gui.shared.bonus_packers import getArmoryYardBonusPacker
from armory_yard.gui.window_events import showArmoryYardInfoPage
_logger = logging.getLogger(__name__)
VEHICLE_TYPE_INDEX = 3

class _QuestsTabPresenter(object):
    __slots__ = ('__viewModel', '__tooltipData', '__closeCB', '__eventsSubscriber', '__blur', '__mainViewlayer', '__parent', '__isProgressCompleted')
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self, viewModel, closeCB, parentViewLayer):
        self.__viewModel = viewModel
        self.__tooltipData = {}
        self.__closeCB = closeCB
        self.__eventsSubscriber = SuspendableEventSubscriber()
        self.__mainViewlayer = parentViewLayer
        self.__parent = None
        self.__blur = CachedBlur(enabled=False, ownLayer=self.__mainViewlayer)
        self.__isProgressCompleted = False
        return

    def init(self, parent):
        self.__parent = parent
        self.__eventsSubscriber.subscribeToEvents((self.__armoryYardCtrl.serverSettings.onUpdated, self.__updateData), (self.__armoryYardCtrl.serverSettings.seasonProvider.onUpdated, self.__updateData), (self.__armoryYardCtrl.onProgressUpdated, self.__progressUpdate), (self.__armoryYardCtrl.onQuestsUpdated, self.__updateData), (self.__viewModel.onAboutEvent, self.__onAboutEvent), (self.__armoryYardCtrl.onStatusChange, self.__updateData), (self.__viewModel.onClose, self.__closeView))
        self.__eventsSubscriber.pause()

    def onLoad(self):
        self.__blur.enable()
        self.__eventsSubscriber.resume()
        self.__updateData()
        self.__isProgressCompleted = self.__armoryYardCtrl.isCompleted()

    def onUnload(self):
        self.__blur.disable()
        self.__eventsSubscriber.pause()

    def fini(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__blur.fini()
        self.__blur = None
        self.__parent = None
        return

    def getTooltipData(self, key, _):
        missionParams = key.rsplit(':', 1)
        if len(missionParams) != 2:
            return None
        else:
            questId, tooltipId = missionParams
            return self.__tooltipData.get(questId, {}).get(tooltipId)

    def __closeView(self, *args):
        self.__closeCB(*args)

    def __progressUpdate(self):
        if not self.__armoryYardCtrl.isQuestActive():
            self.__closeView()
            return
        progressIsCompleted = self.__armoryYardCtrl.isCompleted()
        if self.__isProgressCompleted != progressIsCompleted:
            self.__isProgressCompleted = progressIsCompleted
            self.__updateData()

    def __updateData(self):
        if not self.__armoryYardCtrl.isQuestActive():
            self.__closeView()
            return
        with self.__viewModel.transaction() as model:
            model.setCurrentLevel(self.__armoryYardCtrl.getCurrencyTokenCount())
            model.setViewedLevel(self.__armoryYardCtrl.getProgressionLevel())
            model.setState(self.__armoryYardCtrl.getState())
            startProgressionTime, endSeasonTime = self.__armoryYardCtrl.getProgressionTimes()
            model.setToTimestamp(endSeasonTime)
            model.setFromTimestamp(startProgressionTime)
            self.__updateChapters(model)

    def __updateChapters(self, model):
        ctrl = self.__armoryYardCtrl
        currentSeason = ctrl.serverSettings.getCurrentSeason()
        chaptersArray = model.getChapters()
        questsArray = model.getQuests()
        chaptersArray.clear()
        questsArray.clear()
        isPrevChapterFinished = True
        nowTime = time_utils.getServerUTCTime()
        isPostProgression = ctrl.isPostProgressionActive()
        subtrahendTokens = ctrl.subtrahendStageToken()
        for cycle in sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID')):
            chapter = ArmoryYardChapterModel()
            chapter.setId(cycle.ID)
            isChapterDisabled = not isPrevChapterFinished or cycle.startDate > nowTime
            self.__updateQuests(questsArray, cycle.ID, chapter, isChapterDisabled)
            state = ChapterState.ACTIVE
            if isChapterDisabled:
                state = ChapterState.DISABLED
            elif chapter.getCompletedQuestsAll() == chapter.getTotalQuests():
                state = ChapterState.COMPLETED
            chapter.setState(state)
            isPrevChapterFinished = ctrl.isChapterFinished(cycle.ID)
            totalChapterTokens = ctrl.totalTokensInChapter(cycle.ID)
            receivedTokens = totalChapterTokens if isPrevChapterFinished else ctrl.receivedTokensInChapter(cycle.ID)
            if state == ChapterState.ACTIVE and not isPrevChapterFinished:
                tokenState = ChapterTokenState.COINS if isPostProgression else ChapterTokenState.TOKENS
            else:
                tokenState = ChapterTokenState.LOCK if state == ChapterState.DISABLED else ChapterTokenState.HIDDEN
            if isPostProgression:
                if subtrahendTokens > receivedTokens:
                    subtrahendTokens -= receivedTokens
                    tokenState = ChapterTokenState.HIDDEN
                else:
                    totalChapterTokens -= subtrahendTokens
                    receivedTokens -= subtrahendTokens
                    subtrahendTokens = 0
            chapter.setReceivedTokens(receivedTokens)
            chapter.setTotalTokens(totalChapterTokens)
            chapter.setTokenState(tokenState)
            chaptersArray.addViewModel(chapter)

        chaptersArray.invalidate()

    def __updateQuests(self, questsModel, cycleID, chapter, isChapterDisabled):
        totalQuests = 0
        completedQuests = 0
        for quest in self.__armoryYardCtrl.iterCycleProgressionQuests(cycleID):
            totalQuests += 1
            packer = BattleQuestUIDataPacker(quest, bonusPackerGetter=getArmoryYardBonusPacker)
            questModel = packer.pack(model=ArmoryYardQuestModel())
            questModel.setChapterId(cycleID)
            questModel.setStatus(EventStatus.ACTIVE)
            if quest.isCompleted():
                completedQuests += 1
                questModel.setStatus(EventStatus.DONE)
            if isChapterDisabled:
                questModel.setStatus(EventStatus.LOCKED)
            conditions = quest.vehicleReqs.getConditions().find('vehicleDescr')
            if conditions:
                vehicleTypes = conditions.parseFilters()[VEHICLE_TYPE_INDEX]
                questModel.setVehicleType(vehicleTypes[0] if vehicleTypes else '')
            else:
                questModel.setVehicleType('')
            battleTypes = questModel.getBattleTypes()
            battleTypes.clear()
            battleConditions = quest.preBattleCond.getConditions().find('bonusTypes')
            if battleConditions is not None:
                for battleType in battleConditions.getValue():
                    battleTypes.addNumber(battleType)

            battleTypes.invalidate()
            self.__tooltipData[quest.getID()] = packer.getTooltipData()
            questsModel.addViewModel(questModel)

        questsModel.invalidate()
        previousCompletedQuests = chapter.getCompletedQuestsAll()
        if not previousCompletedQuests:
            previousCompletedQuests = AccountSettings.getArmoryYard(ArmoryYard.ARMORY_YARD_PREV_COMPLETED_QUESTS).get(cycleID, 0)
        settings = AccountSettings.getArmoryYard(ArmoryYard.ARMORY_YARD_PREV_COMPLETED_QUESTS)
        settings[cycleID] = completedQuests
        AccountSettings.setArmoryYard(ArmoryYard.ARMORY_YARD_PREV_COMPLETED_QUESTS, settings)
        chapter.setCompletedQuestsNew(previousCompletedQuests)
        chapter.setCompletedQuestsAll(completedQuests)
        chapter.setTotalQuests(totalQuests)
        return

    def __onAboutEvent(self):
        self.__blur.disable()
        showArmoryYardInfoPage(parent=self.__parent, closeCallback=lambda *_, **__: self.__blur.enable())
