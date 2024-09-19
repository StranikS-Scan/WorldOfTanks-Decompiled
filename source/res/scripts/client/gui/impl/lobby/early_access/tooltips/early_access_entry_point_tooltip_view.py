# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/tooltips/early_access_entry_point_tooltip_view.py
from early_access_common import EARLY_ACCESS_POSTPR_KEY
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEarlyAccessController
from gui.impl.gen.view_models.views.lobby.early_access.tooltips.early_access_entry_point_tooltip_view_model import EarlyAccessEntryPointTooltipViewModel
from gui.impl.gen.view_models.views.lobby.early_access.tooltips.early_access_tooltip_chapter_model import EarlyAccessTooltipChapterModel, TooltipChapterState
from gui.impl.gen.view_models.views.lobby.early_access.early_access_state_enum import State
from nations import AVAILABLE_NAMES

class EarlyAccessEntryPointTooltipView(ViewImpl):
    __slots__ = ('__isHavePostprVehicle', '__isPostprActive', '__showOnlyPostProgression')
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)

    def __init__(self, showOnlyPostProgression=False):
        settings = ViewSettings(R.views.lobby.early_access.tooltips.EarlyAccessEntryPointTooltipView())
        settings.model = EarlyAccessEntryPointTooltipViewModel()
        self.__showOnlyPostProgression = showOnlyPostProgression
        self.__isHavePostprVehicle = False
        self.__isPostprActive = False
        super(EarlyAccessEntryPointTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessEntryPointTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessEntryPointTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    def __updateModel(self, model):
        ctrl = self.__earlyAccessController
        if not ctrl.isQuestActive():
            return
        _, endMainProgressionTime = ctrl.getProgressionTimes()
        _, endPostProgressionTime = ctrl.getPostprogressionTimes()
        earlyAccessState = ctrl.getState()
        self.__isHavePostprVehicle = ctrl.hasPostprogressionVehicle()
        self.__isPostprActive = self.__showOnlyPostProgression or earlyAccessState == State.POSTPROGRESSION or earlyAccessState == State.BUY
        endTimestamp = endMainProgressionTime if not self.__isPostprActive else endPostProgressionTime
        currentTime = time_utils.getServerUTCTime()
        totalTokens = self.__earlyAccessController.getTotalVehiclesPrice()
        receivedTokens = self.__earlyAccessController.getReceivedTokensCount()
        isPrevChapterFinished = True
        prevRemainQuests = 0
        chaptersArray = model.getChapters()
        chaptersArray.clear()
        if not self.__isPostprActive:
            for cycleID, _ in ctrl.iterAllCycles():
                isChapterFinished, prevRemainQuests = self.__updateChapter(chaptersArray, cycleID, isPrevChapterFinished, prevRemainQuests)
                isPrevChapterFinished = isChapterFinished

        isPrevChapterFinished = True
        self.__updateChapter(chaptersArray, EARLY_ACCESS_POSTPR_KEY, isPrevChapterFinished)
        chaptersArray.invalidate()
        model.setTotalTokens(totalTokens)
        model.setReceivedTokens(receivedTokens)
        model.setIsPaused(ctrl.isPaused())
        model.setIsPostprogression(self.__isPostprActive)
        model.setCurrentTimestamp(currentTime)
        model.setEndTimestamp(endTimestamp)

    def __updateChapter(self, chaptersArray, cycleID, isPrevChapterFinished, prevRemainQuests=0):
        ctrl = self.__earlyAccessController
        chapterModel = EarlyAccessTooltipChapterModel()
        completedQuests = sum(((quest.isCompleted() if quest is not None else False) for quest in ctrl.iterCycleProgressionQuests(cycleID)))
        totalQuests = sum(((1 if quest else 0) for quest in ctrl.iterCycleProgressionQuests(cycleID)))
        remainQuests = totalQuests - completedQuests
        isChapterFinished = bool(completedQuests == totalQuests)
        state = TooltipChapterState.ACTIVE
        if cycleID == EARLY_ACCESS_POSTPR_KEY:
            vehicleType, minLvl, maxLvl = ctrl.getRequiredVehicleTypeAndLevelsForQuest(None)
            nation = AVAILABLE_NAMES[self.__earlyAccessController.getNationID()]
            chapterModel.setMinVehicleLvl(minLvl)
            chapterModel.setMaxVehicleLvl(maxLvl)
            chapterModel.setVehicleType(vehicleType)
            chapterModel.setNation(backport.text(R.strings.nations.dyn(nation).genetiveCase()))
            if isChapterFinished:
                state = TooltipChapterState.COMPLETED
            elif self.__isHavePostprVehicle and not isChapterFinished:
                state = TooltipChapterState.ACTIVE
            else:
                state = TooltipChapterState.NOTAVAILABLE
        else:
            cycleStartTime, cycleEndTime = ctrl.getCycleProgressionTimes(cycleID)
            currentTime = time_utils.getServerUTCTime()
            if isChapterFinished:
                state = TooltipChapterState.COMPLETED
            elif not self.__isChapterAvailableByTime(currentTime, cycleStartTime, cycleEndTime):
                state = TooltipChapterState.NOTAVAILABLE
                chapterModel.setAnnouncementTimestamp(cycleStartTime)
            elif self.__isChapterAvailableByTime(currentTime, cycleStartTime, cycleEndTime) and not isPrevChapterFinished:
                state = TooltipChapterState.LOCKED
                chapterModel.setLockedUntilQuestsComplete(prevRemainQuests)
        chapterModel.setCompletedQuests(completedQuests)
        chapterModel.setTotalQuests(totalQuests)
        chapterModel.setState(state)
        chapterModel.setId(cycleID)
        chaptersArray.addViewModel(chapterModel)
        prevRemainQuests = remainQuests
        return (isChapterFinished, prevRemainQuests)

    def __isChapterAvailableByTime(self, currTime, cycleStartTime, cycleEndTime):
        return cycleStartTime <= currTime < cycleEndTime or currTime > cycleEndTime
