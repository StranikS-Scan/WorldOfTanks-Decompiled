# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/event_banner_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from halloween.hw_constants import PhaseType
from halloween.gui.impl.gen.view_models.views.lobby.common.phase_item_model import PhaseStatus
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.event_banner_tooltip_model import EventBannerTooltipModel
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.phase_tooltip_item_model import PhaseTooltipItemModel
from halloween.gui.impl.lobby.base_event_view import STATUS_MAP
from halloween.hw_constants import HALLOWEEN_QUEST_TANKMAN_PASSED_TOKEN
from skeletons.gui.game_control import IHalloweenController
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class EventBannerTooltip(ViewImpl):
    __slots__ = ('__performanceRisk', '__isPost')
    _hwController = dependency.descriptor(IHalloweenController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, performanceRisk, isPost):
        settings = ViewSettings(R.views.halloween.lobby.tooltips.EventBannerTooltip())
        settings.model = EventBannerTooltipModel()
        super(EventBannerTooltip, self).__init__(settings)
        self.__performanceRisk = performanceRisk
        self.__isPost = isPost

    @property
    def viewModel(self):
        return super(EventBannerTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EventBannerTooltip, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setIsPost(self.__isPost)
            model.setPerformanceRisk(self.__performanceRisk)
            phases = self._hwController.phases
            if self.__isPost:
                lastPhase = phases.getPhaseByIndex(phases.getCountPhases())
                timeStart = lastPhase.getStartTime()
                timeEnd = lastPhase.getFinishTime()
            else:
                numberOfRegular = len(phases.getPhasesByType(phaseType=PhaseType.REGULAR))
                firstRegularPhase = phases.getPhaseByIndex(1)
                lastRegularPhase = phases.getPhaseByIndex(numberOfRegular)
                timeStart = firstRegularPhase.getStartTime()
                timeEnd = lastRegularPhase.getFinishTime()
            model.setStartDate(timeStart)
            model.setEndDate(timeEnd)
            phases = model.getPhases()
            phases.clear()
            for ph in self._hwController.phases.getPhasesByType(PhaseType.REGULAR):
                phItem = PhaseTooltipItemModel()
                phItem.setPhase(ph.phaseIndex)
                time = int(ph.getStartTime() if ph.isLock() else ph.getTimeLeftToFinish())
                phItem.setDate(time)
                phItem.setStartDate(ph.getStartTime())
                phItem.setEndDate(ph.getFinishTime())
                passedToken = self._eventsCache.questsProgress.getTokenCount(HALLOWEEN_QUEST_TANKMAN_PASSED_TOKEN.format(index=ph.phaseIndex))
                status = STATUS_MAP.get(ph.getState(), PhaseStatus.LOCKED)
                if passedToken > 0:
                    status = PhaseStatus.COMPLETED
                phItem.setStatus(status)
                phases.addViewModel(phItem)
