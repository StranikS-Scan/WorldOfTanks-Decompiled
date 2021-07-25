# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/main_content/main_contents.py
import typing
from gui.impl.gen.view_models.constants.fitting_types import FittingTypes
from gui.impl.lobby.dialogs.auxiliary.confirmed_item_helpers import ConfirmedItemWarningTypes
from gui.impl.lobby.dialogs.contents.multiple_items_content import MultipleItemsContent
from gui.impl.lobby.tank_setup.dialogs.helpers.ammunition_buy_helper import modulesSortFunction
from gui.impl.lobby.tank_setup.base_sub_model_view import BaseSubModelView
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.main_content.ammunition_buy_content import AmmunitionBuyContent
    from gui.shared.utils.requesters import RequestCriteria

class AmmunitionBuyMainContent(MultipleItemsContent):
    __slots__ = ('__filterCriteria',)

    def __init__(self, viewModel, items, itemsType=None, vehicleInvID=None, filterCriteria=None):
        super(AmmunitionBuyMainContent, self).__init__(viewModel, items, vehicleInvID, itemsType)
        self.__filterCriteria = filterCriteria

    def onLoading(self, *args, **kwargs):
        super(AmmunitionBuyMainContent, self).onLoading(*args, **kwargs)
        with self._viewModel.transaction() as model:
            self.__lacksItem(model.getLacksItem())

    def updateFilter(self, filterCriteria):
        if self.__filterCriteria != filterCriteria:
            self.__filterCriteria = filterCriteria
            with self._viewModel.transaction() as model:
                self._fillItems(model.getConfirmedItems())

    def _fillItems(self, array):
        array.clear()
        for item in self._confirmedItemsPacker.packItems(items=self._items, filterFunc=self.__filterCriteria, sortFunction=modulesSortFunction if self._itemsType == FittingTypes.MODULE else None):
            array.addViewModel(item.getCofirmedItemViewModel())

        array.invalidate()
        return

    def __lacksItem(self, array):
        array.clear()
        for item in self._confirmedItemsPacker.packItems(items=self._items):
            devicesName = [ name for warningType, warning in item.getWarnings().iteritems() for name in warning.getDevicesName() if warningType == ConfirmedItemWarningTypes.DEPENDS_ON_DEVICES ]
            for deviceName in devicesName:
                array.addString(deviceName)

        array.invalidate()


class NeedRepairMainContent(BaseSubModelView):

    def __init__(self, viewModel, repairPercentage, vehicle):
        super(NeedRepairMainContent, self).__init__(viewModel)
        self.__repairPercentage = repairPercentage
        self.__vehicle = vehicle

    def onLoading(self, *args, **kwargs):
        super(NeedRepairMainContent, self).onLoading(*args, **kwargs)
        with self._viewModel.transaction() as model:
            model.setRepairPercentage(self.__repairPercentage)
            model.setFreeAutoRepair(self.__vehicle.level == 1 and self.__vehicle.repairCost == 0)

    def update(self, repairPercentage=None):
        if repairPercentage is not None:
            self.__repairPercentage = repairPercentage
        self._viewModel.setRepairPercentage(self.__repairPercentage)
        return
