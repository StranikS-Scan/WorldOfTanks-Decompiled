# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/shell.py
import typing
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_slot_model import ShellSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_specification_model import ShellSpecificationModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters.formatters import MEASURE_UNITS, formatParameter
from post_progression_common import TankSetupGroupsId
from helpers import dependency, i18n
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.vehicle_modules import Shell
    from gui.impl.lobby.tank_setup.array_providers.base import BaseVehSectionContext
_SHELLS_INFO_PARAMS = (('distanceDamage', 'avgDamage'),
 ('avgPiercingPower',),
 ('shotSpeed',),
 ('explosionRadius',),
 ('flameMaxDistance',),
 ('stunMaxDuration',))

class ShellProvider(VehicleBaseArrayProvider):
    __slots__ = ('_interactor',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def updateItems(self):
        pass

    def getItemViewModel(self):
        return ShellSlotModel()

    def fillArray(self, array, ctx, itemFilter=None):
        array.clear()
        for item in self._getCurrentLayout():
            itemModel = self.getItemViewModel()
            self.updateSlot(itemModel, item, ctx)
            array.addViewModel(itemModel)

        array.invalidate()

    def updateArray(self, array, ctx):
        for item, itemModel in zip(self._getCurrentLayout(), array):
            self.updateSlot(itemModel, item, ctx)

    def createSlot(self, item, ctx):
        return self.getItemViewModel()

    def updateSlot(self, model, item, ctx):
        super(ShellProvider, self).updateSlot(model, item, ctx)
        buyPrice = item.getBuyPrice()
        if model.getIntCD() != item.intCD:
            model.setType(item.type)
            model.setName(item.userName)
            model.setIntCD(item.intCD)
            model.setItemTypeID(item.itemTypeID)
            model.setImageName(item.descriptor.iconName)
            BuyPriceModelBuilder.clearPriceModel(model.price)
            BuyPriceModelBuilder.fillPriceModelByItemPrice(model.price, buyPrice, checkBalanceAvailability=True)
            self._fillSpecification(model, item)
        vehicle = self._getVehicle()
        inTankCount = 0
        for shell in vehicle.shells.setupLayouts:
            if shell == item:
                inTankCount = max(inTankCount, shell.count)

        boughtCount = item.inventoryCount + inTankCount
        buyCount = max(item.count - boughtCount, 0)
        model.setCount(item.count)
        shellsSetupLayouts = vehicle.shells.setupLayouts
        inTankCount = max(item.count, shellsSetupLayouts.ammoLoadedInOtherSetups(item.intCD))
        model.setItemsInStorage(max(boughtCount - inTankCount, 0))
        if vehicle.isSetupSwitchActive(TankSetupGroupsId.EQUIPMENT_AND_SHELLS):
            model.setItemsInVehicle(inTankCount)
        else:
            model.setItemsInVehicle(-1)
        model.setBuyCount(buyCount)
        BuyPriceModelBuilder.clearPriceModel(model.totalPrice)
        if buyCount:
            BuyPriceModelBuilder.fillPriceModelByItemPrice(model.totalPrice, buyPrice * buyCount, checkBalanceAvailability=True)

    def _fillSpecification(self, model, item):
        specifications = model.getSpecifications()
        specifications.clear()
        shellParam = params_helper.getParameters(item, self._getVehicle().descriptor)
        for rowParams in _SHELLS_INFO_PARAMS:
            for paramName in rowParams:
                formattedParam = formatParameter(paramName, shellParam.get(paramName))
                if formattedParam is None:
                    continue
                model = self._getSpecificationsModel(paramName, formattedParam)
                specifications.addViewModel(model)
                break

        specifications.invalidate()
        return

    def _getSpecificationsModel(self, paramName, formattedParam):
        model = ShellSpecificationModel()
        model.setParamName(paramName)
        model.setMetricValue(i18n.makeString(MEASURE_UNITS.get(paramName, '')))
        model.setValue(formattedParam)
        return model
