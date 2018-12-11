# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/tooltips/compensation_tooltip.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.pub import ViewImpl

class CompensationTooltipContent(ViewImpl):
    __slots__ = ()

    @property
    def viewModel(self):
        return super(CompensationTooltipContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            tx.setIconBefore(kwargs.get('iconBefore', ''))
            tx.setLabelBefore(kwargs.get('labelBefore', ''))
            tx.setIconAfter(kwargs.get('iconAfter', ''))
            tx.setLabelAfter(kwargs.get('labelAfter', ''))
            tx.setBonusName(kwargs.get('bonusName', ''))
            tx.setTooltipType(LootBoxCompensationTooltipTypes.BASE)


class VehicleCompensationTooltipContent(CompensationTooltipContent):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(VehicleCompensationTooltipContent, self).__init__(R.views.lootBoxVehicleCompensationTooltipContent, ViewFlags.VIEW, LootBoxVehicleCompensationTooltipModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(VehicleCompensationTooltipContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(VehicleCompensationTooltipContent, self)._initialize(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setVehicleName(kwargs.get('vehicleName', ''))
            tx.setVehicleType(kwargs.get('vehicleType', ''))
            tx.setIsElite(kwargs.get('isElite', True))
            tx.setVehicleLvl(kwargs.get('vehicleLvl', ''))
            tx.setTooltipType(LootBoxCompensationTooltipTypes.VEHICLE)
