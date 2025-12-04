# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/entry_point_active_tooltip_view.py
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.armory_yard_tooltip_chapter_model import ArmoryYardTooltipChapterModel, TooltipChapterState
from armory_yard.gui.server_events.events_helpers import getQuestsCompletedFunc
from frameworks.wulf import ViewSettings, Array
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.entry_point_active_tooltip_view_model import EntryPointActiveTooltipViewModel
from helpers import dependency, time_utils
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IArmoryYardController

class EntryPointActiveTooltipView(ViewImpl):
    __slots__ = ()
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.EntryPointActiveTooltipView())
        settings.model = EntryPointActiveTooltipViewModel()
        super(EntryPointActiveTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointActiveTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointActiveTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    def __updateModel(self, model):
        ctrl = self.__armoryYardCtrl
        chapters = model.getChapters()
        chapters.clear()
        isPrevChapterFinished = True
        prevChapterQuests = 0
        nowTime = time_utils.getServerUTCTime()
        activeQuests = 0
        if not ctrl.isEnabled():
            return
        completedFunc = getQuestsCompletedFunc()
        for cycle in sorted(ctrl.serverSettings.getCurrentSeason().getAllCycles().values(), key=lambda item: item.ID):
            chapter = ArmoryYardTooltipChapterModel()
            totalQuests = 0
            completedQuests = 0
            for quests in self.__armoryYardCtrl.iterCycleProgressionQuests(cycle.ID):
                totalQuests += 1
                if completedFunc(quests):
                    completedQuests += 1

            state = TooltipChapterState.ACTIVE
            if cycle.startDate > nowTime:
                deltaTime = cycle.startDate - nowTime
                if deltaTime < time_utils.ONE_DAY:
                    state = TooltipChapterState.JUSTBEFORESTART
                    chapter.setJustBeforeStartTimestamp(deltaTime)
                else:
                    state = TooltipChapterState.ANNOUNCEMENT
                    chapter.setAnnouncementTimestamp(cycle.startDate)
            elif not isPrevChapterFinished:
                state = TooltipChapterState.LOCKED
                chapter.setLockedUntilQuestsComplete(prevChapterQuests)
            elif totalQuests == completedQuests:
                state = TooltipChapterState.COMPLETED
            if state == TooltipChapterState.ACTIVE:
                activeQuests += totalQuests - completedQuests
            isPrevChapterFinished = ctrl.isChapterFinished(cycle.ID)
            prevChapterQuests = ctrl.totalTokensInChapter(cycle.ID) - ctrl.receivedTokensInChapter(cycle.ID)
            chapter.setId(cycle.ID)
            chapter.setState(state)
            chapter.setCompletedQuests(completedQuests)
            chapter.setTotalQuests(totalQuests)
            chapters.addViewModel(chapter)

        ppCycleID = max([ x.ID for x in ctrl.serverSettings.getCurrentSeason().getAllCycles().values() ]) + 1
        ppActiveQuests = self.__updatePostProgression(chapters, ppCycleID)
        activeQuests += ppActiveQuests
        chapters.invalidate()
        totalTokens, receivedTokens = ctrl.getTokensInfoMainProgression()
        _, finishProgressionTime = ctrl.getProgressionTimes()
        deltaFinishProgressionTime = finishProgressionTime - nowTime
        if deltaFinishProgressionTime < time_utils.ONE_DAY:
            model.setEndTimestamp(deltaFinishProgressionTime)
        model.setQuestsInProgress(activeQuests)
        model.setReceivedTokens(receivedTokens)
        model.setTotalTokens(totalTokens)

    def __updatePostProgression(self, chapters, cycleID):
        ctrl = self.__armoryYardCtrl
        postProgression = ctrl.serverSettings.getPostProgressionData()
        availableQuestAtOneTime = postProgression.get('availableQuestAtOneTime', 1)
        chapter = ArmoryYardTooltipChapterModel()
        chapter.setId(cycleID)
        activeQuests = 0
        totalQuests = 0
        completedQuests = 0
        completedFunc = getQuestsCompletedFunc()
        for quests in self.__armoryYardCtrl.iterCyclePostProgressionQuests():
            totalQuests += 1
            if completedFunc(quests):
                completedQuests += 1

        state = TooltipChapterState.ACTIVE
        if not ctrl.isPostProgressionState:
            state = TooltipChapterState.LOCKED
            chapter.setLockedUntilQuestsComplete(ctrl.startStepOfPostProgression - ctrl.getProgressionTokenCount())
        elif totalQuests == completedQuests:
            state = TooltipChapterState.COMPLETED
        if state == TooltipChapterState.ACTIVE:
            activeQuests = totalQuests - completedQuests
        chapter.setState(state)
        chapter.setCompletedQuests(completedQuests)
        chapter.setTotalQuests(totalQuests)
        chapter.setIsPostProgression(True)
        chapters.addViewModel(chapter)
        return min(activeQuests, availableQuestAtOneTime)
