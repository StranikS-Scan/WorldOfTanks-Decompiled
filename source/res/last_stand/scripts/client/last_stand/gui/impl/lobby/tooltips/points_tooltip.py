# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/points_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.points_tooltip_view_model import PointsTooltipViewModel
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_shop_controller import ILSShopController
from helpers import dependency
from shared_utils import first

class PointsTooltipView(ViewImpl):
    __slots__ = ('__isPostBattle', '__ctx')
    lsCtrl = dependency.descriptor(ILSController)
    lsShopCtrl = dependency.descriptor(ILSShopController)

    def __init__(self, isPostBattle, ctx=None, layoutID=R.views.last_stand.mono.lobby.tooltips.points_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = PointsTooltipViewModel()
        super(PointsTooltipView, self).__init__(settings)
        self.__isPostBattle = isPostBattle
        self.__ctx = ctx

    @property
    def viewModel(self):
        return super(PointsTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PointsTooltipView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setIsPostBattle(self.__isPostBattle)
            model.setEndDate(self.lsCtrl.getConfig().get('endDate', 0))
            bundle = first(self.lsShopCtrl.keyBundles())
            if bundle:
                self.viewModel.setBundleKey(str(bundle.descrGroupKey))
            if self.__isPostBattle:
                model.setEffective(self.__ctx.get('effective', 0))
                model.setObelisk(self.__ctx.get('obelisk', 0))
                model.setVehicleDaily(self.__ctx.get('vehicleDaily', 0))
                model.setMissionDaily(self.__ctx.get('missionDaily', 0))
