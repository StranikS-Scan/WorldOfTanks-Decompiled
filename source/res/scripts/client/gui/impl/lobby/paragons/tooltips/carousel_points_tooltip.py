# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/carousel_points_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.paragons_carousel_points_tooltip_model import ParagonsCarouselPointsTooltipModel
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IParagonsController

class ParagonsCarouselPointsTooltip(ViewImpl):
    __slots__ = ('__isNeedWin', '__vehicleCD')
    __paragonsCtrl = dependency.descriptor(IParagonsController)

    def __init__(self, isNeedWin=False, vehicleCD=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.paragons.tooltips.ParagonsCarouselPointsTooltip())
        settings.model = ParagonsCarouselPointsTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ParagonsCarouselPointsTooltip, self).__init__(settings)
        self.__isNeedWin = isNeedWin
        self.__vehicleCD = vehicleCD

    @property
    def viewModel(self):
        return super(ParagonsCarouselPointsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        isNextVehUnlocked = self.__paragonsCtrl.isNextResetVehUnlocked(self.__vehicleCD)
        with self.viewModel.transaction() as tx:
            tx.setIsNeedWin(self.__isNeedWin)
            tx.setIsNextVehUnlocked(isNextVehUnlocked)
