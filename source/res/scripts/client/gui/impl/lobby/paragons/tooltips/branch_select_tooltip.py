# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/branch_select_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.branch_select_tooltip_model import BranchSelectTooltipModel
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IParagonsController
from helpers import dependency
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillParagonsVehicleModels

class BranchSelectTooltip(ViewImpl):
    __slots__ = ('__paragonsUnlockID', '__vehicleCDs')
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self, layoutID, paragonsUnlockID):
        settings = ViewSettings(layoutID)
        settings.model = BranchSelectTooltipModel()
        super(BranchSelectTooltip, self).__init__(settings)
        self.__paragonsUnlockID = paragonsUnlockID
        self.__vehicleCDs = None
        return

    @property
    def viewModel(self):
        return super(BranchSelectTooltip, self).getViewModel()

    @property
    def id(self):
        return self.__paragonsUnlockID

    @property
    def vehicleCDs(self):
        if self.__vehicleCDs is None:
            self.__vehicleCDs = self.__paragonsController.config.getParagonsUnlockVehicles(self.id)
        return self.__vehicleCDs

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            fillParagonsVehicleModels(tx.getVehicles(), self.vehicleCDs)
