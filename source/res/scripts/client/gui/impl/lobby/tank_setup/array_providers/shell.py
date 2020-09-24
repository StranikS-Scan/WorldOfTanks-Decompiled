# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/shell.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_slot_model import ShellSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_specification_model import ShellSpecificationModel
from gui.impl.lobby.tank_setup.array_providers.base import VehicleBaseArrayProvider
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters.formatters import MEASURE_UNITS, formatParameter
from helpers import dependency, i18n
from skeletons.gui.shared import IItemsCache
_SHELLS_INFO_PARAMS = ('avgDamage', 'avgPiercingPower', 'shotSpeed', 'explosionRadius', 'stunDurationList')

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
            BuyPriceModelBuilder.fillPriceModelByItemPrice(model.price, buyPrice)
            self._fillSpecification(model, item)
        inTankCount = 0
        for shell in self._getVehicle().shells.installed:
            if shell == item:
                inTankCount = shell.count

        boughtCount = item.inventoryCount + inTankCount
        buyCount = max(item.count - boughtCount, 0)
        model.setCount(item.count)
        model.setItemsInStorage(max(boughtCount - item.count, 0))
        model.setBuyCount(buyCount)
        BuyPriceModelBuilder.clearPriceModel(model.totalPrice)
        if buyCount:
            BuyPriceModelBuilder.fillPriceModelByItemPrice(model.totalPrice, buyPrice * buyCount)

    def _fillSpecification(self, model, item):
        specifications = model.getSpecifications()
        specifications.clear()
        for paramName in _SHELLS_INFO_PARAMS:
            specificationModel = ShellSpecificationModel()
            specificationModel.setParamName(paramName)
            specificationModel.setMetricValue(i18n.makeString(MEASURE_UNITS.get(paramName, '')))
            shellParam = params_helper.getParameters(item, self._getVehicle().descriptor)
            specificationModel.setValue(formatParameter(paramName, shellParam.get(paramName)) or '')
            specifications.addViewModel(specificationModel)

        specifications.invalidate()
