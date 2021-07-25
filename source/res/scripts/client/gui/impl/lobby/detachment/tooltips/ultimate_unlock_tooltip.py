# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/ultimate_unlock_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.ultimate_unlock_tooltip_model import UltimateUnlockTooltipModel
from gui.impl.pub import ViewImpl
from uilogging.detachment.loggers import DynamicGroupTooltipLogger

class UltimateUnlockTooltipView(ViewImpl):
    __slots__ = ('__ultimatePerkSelected', '__currentPoints', '__maxPoints')
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, ultimatePerkSelected, currentPoints, maxPoints):
        self.__ultimatePerkSelected = ultimatePerkSelected
        self.__currentPoints = currentPoints
        self.__maxPoints = maxPoints
        settings = ViewSettings(R.views.lobby.detachment.tooltips.UltimateUnlockTooltip())
        settings.model = UltimateUnlockTooltipModel()
        super(UltimateUnlockTooltipView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(UltimateUnlockTooltipView, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setUltimateSelected(self.__ultimatePerkSelected)
            vm.setCurrentPoints(self.__currentPoints)
            vm.setMaxPoints(self.__maxPoints)

    @property
    def viewModel(self):
        return super(UltimateUnlockTooltipView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(UltimateUnlockTooltipView, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(UltimateUnlockTooltipView, self)._finalize()
