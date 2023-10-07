# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/event_banner_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from halloween.gui.halloween_gui_constants import PREBATTLE_ACTION_NAME
from gui.shared.utils import SelectorBattleTypesUtils
from gui.shared.utils.performance_analyzer import PerformanceGroup
from halloween.gui.impl.gen.view_models.views.lobby.event_banner_view_model import EventBannerViewModel, PerformanceRiskEnum
from halloween.gui.impl.lobby.tooltips.event_banner_tooltip import EventBannerTooltip
from halloween.gui.shared.event_dispatcher import showHalloweenShop
from halloween.hw_constants import PhaseType
from helpers import dependency
from skeletons.gui.game_control import IHalloweenController
from skeletons.gui.server_events import IEventsCache
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

class EventBannerView(ViewImpl):
    _eventsCache = dependency.descriptor(IEventsCache)
    _hwController = dependency.descriptor(IHalloweenController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.halloween.lobby.EventBannerView())
        settings.flags = flags
        settings.model = EventBannerViewModel()
        super(EventBannerView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventBannerView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.lobby.tooltips.EventBannerTooltip():
            currentPerformanceGroup = self._hwController.getPerformanceGroup()
            phase = self._hwController.phases
            return EventBannerTooltip(PERFORMANCE_MAP.get(currentPerformanceGroup, PerformanceRiskEnum.LOWRISK), phase.getActivePhase(PhaseType.POST) is not None)
        else:
            return super(EventBannerView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(EventBannerView, self)._onLoading(*args, **kwargs)
        self.viewModel.onClick += self.__onClick
        self._eventsCache.onSyncCompleted += self.__updateViewModel
        self._hwController.onChangeActivePhase += self.__onChangeActivePhase
        self._hwController.onQuestsUpdated += self.__onQuestUpdated
        self.__updateViewModel()

    def _finalize(self):
        self.viewModel.onClick -= self.__onClick
        self._eventsCache.onSyncCompleted -= self.__updateViewModel
        self._hwController.onChangeActivePhase -= self.__onChangeActivePhase
        self._hwController.onQuestsUpdated -= self.__onQuestUpdated
        super(EventBannerView, self)._finalize()

    def __onChangeActivePhase(self, _):
        self.__updateViewModel()

    def __onQuestUpdated(self):
        self.__updateViewModel()

    def __updateViewModel(self):
        with self.viewModel.transaction() as model:
            phases = self._hwController.phases
            activePhaseIndex = phases.getActivePhaseIndex()
            activePhase = phases.getPhaseByIndex(activePhaseIndex)
            if activePhase is None:
                return
            model.setPhase(activePhaseIndex)
            numberOfRegular = len(phases.getPhasesByType(phaseType=PhaseType.REGULAR))
            model.setPhases(numberOfRegular)
            model.setPhaseTime(activePhase.getTimeLeftToFinish())
            lastRegularPhase = phases.getPhaseByIndex(numberOfRegular)
            postPhase = phases.getPhaseByIndex(phases.getCountPhases())
            model.setEventPostStartDate(postPhase.getStartTime())
            if self._hwController.isPostPhase():
                model.setEventEndDate(postPhase.getFinishTime())
            else:
                model.setEventEndDate(lastRegularPhase.getTimeLeftToFinish())
            currentPerformanceGroup = self._hwController.getPerformanceGroup()
            model.setPerformanceRisk(PERFORMANCE_MAP.get(currentPerformanceGroup, PerformanceRiskEnum.LOWRISK))
            model.setIsPost(phases.getActivePhase(PhaseType.POST) is not None)
            savedPhase = phases.getPrevPhase()
            isKnownBattleType = SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE)
            model.setIsNew(not isKnownBattleType or savedPhase != activePhaseIndex)
        return

    def __onClick(self):
        if not self._hwController.phases.getActivePhase() or self._hwController.isPostPhase() or not self._hwController.isEnabled():
            showHalloweenShop()
        else:
            self._hwController.selectEventBattle()
