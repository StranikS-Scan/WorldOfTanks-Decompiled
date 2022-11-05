# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/tooltips/deconstruct_from_inventory_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.tank_setup.tooltips.deconstruct_from_inventory_tooltip_model import DeconstructFromInventoryTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class DeconstructFromInventoryTooltip(ViewImpl):
    __slots__ = ('equipmentName', 'equipmentAmount')

    def __init__(self, equipmentName, equipmentAmount, layoutID=R.views.lobby.tanksetup.tooltips.DeconstructFromInventoryTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = DeconstructFromInventoryTooltipModel()
        self.equipmentName = equipmentName
        self.equipmentAmount = equipmentAmount
        super(DeconstructFromInventoryTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DeconstructFromInventoryTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(DeconstructFromInventoryTooltip, self)._initialize(*args, **kwargs)
        self.viewModel.setEquipmentAmount(self.equipmentAmount)
        self.viewModel.setEquipmentName(self.equipmentName)
