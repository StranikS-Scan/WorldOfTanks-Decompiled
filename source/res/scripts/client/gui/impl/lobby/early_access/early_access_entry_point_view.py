# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_entry_point_view.py
from operator import attrgetter
from account_helpers.AccountSettings import AccountSettings, EarlyAccess
from frameworks.wulf import ViewFlags, ViewSettings, ViewModel
from early_access_common import EARLY_ACCESS_POSTPR_KEY
from gui.impl.gen.view_models.views.lobby.early_access.early_access_entry_point_view_model import EarlyAccessEntryPointViewModel, ExtendedStates
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.early_access.early_access_state_enum import State
from gui.impl.lobby.early_access.early_access_window_events import showEarlyAccessQuestsView
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEarlyAccessController
from gui.impl.lobby.early_access.tooltips.early_access_entry_point_tooltip_view import EarlyAccessEntryPointTooltipView

class EarlyAccessEntryPointView(ViewImpl):
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.early_access.EarlyAccessEntryPointView(), flags=ViewFlags.VIEW, model=EarlyAccessEntryPointViewModel())
        super(EarlyAccessEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.early_access.tooltips.EarlyAccessEntryPointTooltipView():
            return EarlyAccessEntryPointTooltipView()
        if contentID == R.views.lobby.early_access.tooltips.EarlyAccessEntryPointPausedTooltip():
            return ViewImpl(ViewSettings(contentID, model=ViewModel()))
        return ViewImpl(ViewSettings(contentID, model=ViewModel())) if contentID == R.views.lobby.early_access.tooltips.EarlyAccessCommonDescriptionTooltip() else super(EarlyAccessEntryPointView, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.__earlyAccessCtrl.onQuestsUpdated, self.__updateModel), (self.__earlyAccessCtrl.onUpdated, self.__updateModel), (self.viewModel.onAction, self.__goToNextScreen))

    def __updateModel(self, *_):
        ctrl = self.__earlyAccessCtrl
        if not ctrl.isEnabled():
            return
        else:
            state = ctrl.getState()
            currProgressionLevel = self.__calculateProgressionLevel()
            currentTime = time_utils.getServerUTCTime()
            _, currFinishTime = ctrl.getCycleProgressionTimes()
            finishSeasonTime = ctrl.getCurrentSeason().getEndDate()
            remainTime = finishSeasonTime - currentTime
            if not ctrl.isQuestActive():
                state = ExtendedStates.DISABLED
            elif state == State.ACTIVE:
                remainProgrQuestsCount = self.__getTotalIncompleteQuestCount()
                currentCycleID = self.__getCurrentActiveCycleID()
                remainPostProgrQuestsCount = self.__getIncompleteQuestCountInCycle(EARLY_ACCESS_POSTPR_KEY)
                remainCurrCycleQuestsCount = self.__getIncompleteQuestCountInCycle(currentCycleID)
                if not remainProgrQuestsCount and remainPostProgrQuestsCount:
                    state = State.POSTPROGRESSION
                elif not remainCurrCycleQuestsCount and currentTime < currFinishTime:
                    state = ExtendedStates.WAITFORNEXTCHAPTER
            elif state == State.BUY:
                state = State.POSTPROGRESSION
            isFirstEnter = not AccountSettings.getEarlyAccess(EarlyAccess.INTRO_SEEN)
            with self.viewModel.transaction() as model:
                model.setState(state.value)
                model.setIsFirstEnter(isFirstEnter)
                if currProgressionLevel is not None:
                    model.setProgressionLevel(currProgressionLevel)
                if remainTime < time_utils.ONE_DAY:
                    model.setEndTimestamp(remainTime)
            return

    def __goToNextScreen(self):
        showEarlyAccessQuestsView()

    def __calculateProgressionLevel(self):
        currentSeason = self.__earlyAccessCtrl.getCurrentSeason()
        cycles = sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID'))
        return next((i for i, cycle in enumerate(cycles) if self.__getIncompleteQuestCountInCycle(str(cycle.ID)) > 0), None)

    def __getIncompleteQuestCountInCycle(self, cycleID):
        return sum((not quest.isCompleted() for quest in self.__earlyAccessCtrl.iterCycleProgressionQuests(cycleID)))

    def __getTotalIncompleteQuestCount(self):
        return sum((self.__getIncompleteQuestCountInCycle(cycleID) for cycleID, _ in self.__earlyAccessCtrl.iterAllCycles()))

    def __getCurrentActiveCycleID(self):
        currTime = time_utils.getServerUTCTime()
        currentSeason = self.__earlyAccessCtrl.getCurrentSeason()
        if currentSeason:
            currCycle = currentSeason.getLastActiveCycleInfo(currTime)
            return str(currCycle.ID)
