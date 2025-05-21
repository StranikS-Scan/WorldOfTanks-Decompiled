# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/key_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.key_tooltip_view_model import KeyTooltipViewModel
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency

class KeyTooltipView(ViewImpl):
    __slots__ = ('__isPostBattle', '__ctx')
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self, isPostBattle, ctx=None, layoutID=R.views.last_stand.mono.lobby.tooltips.key_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = KeyTooltipViewModel()
        super(KeyTooltipView, self).__init__(settings)
        self.__isPostBattle = isPostBattle
        self.__ctx = ctx

    @property
    def viewModel(self):
        return super(KeyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(KeyTooltipView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setIsPostBattle(self.__isPostBattle)
            model.setKeyCount(self.lsArtifactsCtrl.getArtefactKeyQuantity())
            model.setEndDate(self.lsCtrl.getConfig().get('endDate', 0))
            if self.__isPostBattle:
                model.setEffective(self.__ctx.get('effective', 0))
                model.setVehicleDaily(self.__ctx.get('vehicleDaily', 0))
                model.setMissionDaily(self.__ctx.get('missionDaily', 0))
