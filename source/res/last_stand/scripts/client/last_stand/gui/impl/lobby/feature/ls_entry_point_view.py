# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/feature/ls_entry_point_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from last_stand.gui.ls_account_settings import AccountSettingsKeys, getSettings
from last_stand.gui.impl.lobby.tooltips.event_banner_tooltip import EventBannerTooltipView
from last_stand.gui.shared.utils.performance_analyzer import PerformanceGroup
from last_stand.gui.impl.gen.view_models.views.lobby.event_banner_view_model import EventBannerViewModel, PerformanceRiskEnum
from helpers import dependency, time_utils
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
PERFORMANCE_MAP = {PerformanceGroup.LOW_RISK: PerformanceRiskEnum.LOWRISK,
 PerformanceGroup.MEDIUM_RISK: PerformanceRiskEnum.MEDIUMRISK,
 PerformanceGroup.HIGH_RISK: PerformanceRiskEnum.HIGHRISK}

@dependency.replace_none_kwargs(ctrl=ILSController)
def isLSEntryPointAvailable(ctrl=None):
    return ctrl.isAvailable()


class LSEntryPointView(ViewImpl):
    lsCtrl = dependency.descriptor(ILSController)
    lsArtefactCtrl = dependency.descriptor(ILSArtefactsController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.last_stand.mono.lobby.banner_view())
        settings.flags = flags
        settings.model = EventBannerViewModel()
        super(LSEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LSEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.banner_tooltip():
            performance = PERFORMANCE_MAP.get(self.lsCtrl.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK)
            return EventBannerTooltipView(performanceRisk=performance)
        return super(LSEntryPointView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(LSEntryPointView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        return [(self.viewModel.onClick, self.__onClick),
         (self.lsCtrl.onEventDisabled, self.__update),
         (self.lsCtrl.onSettingsUpdate, self.__update),
         (self.lsArtefactCtrl.onArtefactStatusUpdated, self.__update)]

    def __onClick(self):
        self.lsCtrl.selectBattle()

    def __update(self, *args, **kwargs):
        if not isLSEntryPointAvailable():
            self.destroyWindow()
            return
        with self.viewModel.transaction() as model:
            model.setDate(time_utils.getServerUTCTime())
            model.setEndDate(self.lsCtrl.getModeSettings().endDate)
            model.setPerformanceRisk(PERFORMANCE_MAP.get(self.lsCtrl.getPerformanceGroup(), PerformanceRiskEnum.LOWRISK))
            model.setIsNew(getSettings(AccountSettingsKeys.IS_EVENT_NEW))
            artefact = self.lsArtefactCtrl.getKingRewardArtefact()
            model.setIsKingRewardReceive(self.lsArtefactCtrl.isArtefactOpened(artefact.artefactID) if artefact else False)
