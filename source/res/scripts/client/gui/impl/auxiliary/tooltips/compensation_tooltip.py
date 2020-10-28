# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/tooltips/compensation_tooltip.py
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_model import LootBoxCompensationTooltipModel
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
            tx.setCountBefore(kwargs.get('countBefore', 1))
            tx.setTooltipType(kwargs.get('tooltipType', LootBoxCompensationTooltipTypes.BASE))


class CrewSkinsCompensationTooltipContent(CompensationTooltipContent):
    __slots__ = ()

    def _initialize(self, *args, **kwargs):
        super(CrewSkinsCompensationTooltipContent, self)._initialize(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setLabelBefore(kwargs.get('labelBefore', ''))


class VehicleCompensationTooltipContent(CompensationTooltipContent):
    __slots__ = ()

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
