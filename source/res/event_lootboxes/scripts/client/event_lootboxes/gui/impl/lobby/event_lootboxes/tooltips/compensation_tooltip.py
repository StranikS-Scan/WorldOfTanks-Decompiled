# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/lobby/event_lootboxes/tooltips/compensation_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.tooltips.compensation_tooltip_model import CompensationTooltipModel, VehicleType
from gui.impl.pub import ViewImpl
from gui.shared.money import Currency
from shared_utils import first

class EventLootBoxesCompensationTooltip(ViewImpl):
    __slots__ = ('__data',)

    def __init__(self, compensationData):
        settings = ViewSettings(R.views.event_lootboxes.lobby.event_lootboxes.tooltips.CompensationTooltip())
        settings.model = CompensationTooltipModel()
        self.__data = compensationData
        super(EventLootBoxesCompensationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventLootBoxesCompensationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setIconBefore(self.__data['iconBefore'])
            model.setVehicleLevel(self.__data['vehicleLevel'])
            model.setVehicleType(VehicleType(self.__data['vehicleType']))
            model.setVehicleName(self.__data['vehicleName'])
            model.setCompensationCurrency(self.__data['compensation'].get('currency', first(Currency.BY_WEIGHT)))
            model.setCompensationValue(self.__data['compensation'].get('value', 0))
