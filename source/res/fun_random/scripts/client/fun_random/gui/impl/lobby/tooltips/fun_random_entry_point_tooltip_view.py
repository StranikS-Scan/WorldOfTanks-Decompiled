# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_entry_point_tooltip_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from fun_random.gui.feature.fun_constants import FunSubModesState
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_entry_point_tooltip_view_model import FunRandomEntryPointTooltipViewModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import packPerformanceAlertInfo, getFunRandomEventState
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import time_utils

class FunRandomEntryPointTooltipView(ViewImpl, FunAssetPacksMixin, FunSubModesWatcher):

    def __init__(self):
        settings = ViewSettings(R.views.fun_random.mono.lobby.tooltips.entry_point_tooltip(), model=FunRandomEntryPointTooltipViewModel())
        super(FunRandomEntryPointTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomEntryPointTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            status = self.getSubModesStatus()
            model.setAssetsPointer(self.getModeAssetsPointer())
            model.setModeState(getFunRandomEventState(status))
            endTime = status.endTime
            leftTime = status.primeDelta if status.state == FunSubModesState.NOT_AVAILABLE else time_utils.getTimeDeltaFromNowInLocal(endTime)
            model.setStartTime(status.rightBorder)
            model.setLeftTime(leftTime)
            model.setEndTime(endTime)
            packPerformanceAlertInfo(model.performance, self._funRandomCtrl.subModesInfo.getPerformanceAlertGroup())
