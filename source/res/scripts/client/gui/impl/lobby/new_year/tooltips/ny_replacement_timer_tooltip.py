# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_replacement_timer_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_replacement_timer_tooltip_model import NyReplacementTimerTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import time_utils

class NyReplacementTimerTooltip(ViewImpl):
    __slots__ = ('__isAvailable', '__isFinished')

    def __init__(self, isAvailable, isFinished):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyReplacementTimerTooltip())
        settings.model = NyReplacementTimerTooltipModel()
        super(NyReplacementTimerTooltip, self).__init__(settings)
        self.__isAvailable = isAvailable
        self.__isFinished = isFinished

    @property
    def viewModel(self):
        return super(NyReplacementTimerTooltip, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(NyReplacementTimerTooltip, self)._onLoaded()
        self.viewModel.setTimeTill(time_utils.getDayTimeLeft())
        self.viewModel.setIsAvailable(self.__isAvailable)
        self.viewModel.setIsFinished(self.__isFinished)
