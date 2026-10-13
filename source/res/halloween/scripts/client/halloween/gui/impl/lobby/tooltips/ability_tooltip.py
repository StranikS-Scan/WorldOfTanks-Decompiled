# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/ability_tooltip.py
from __future__ import absolute_import
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.ability_tooltip_view_model import AbilityTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class AbilityTooltipView(ViewImpl):
    __slots__ = ('__showPriceBlock', '__intCD', 'item')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, intCD, showPriceBlock=True):
        r = R.views.halloween.mono.lobby.tooltips
        settings = ViewSettings(r.ability_tooltip() if intCD > 0 else r.empty_ability_slot_tooltip())
        settings.model = AbilityTooltipViewModel()
        super(AbilityTooltipView, self).__init__(settings)
        self.__showPriceBlock = showPriceBlock
        self.item = self.__itemsCache.items.getItemByCD(int(intCD)) if intCD else None
        return

    @property
    def viewModel(self):
        return super(AbilityTooltipView, self).getViewModel()

    @staticmethod
    def _getInstalledVehicles(module, inventoryVehicles):
        return module.getInstalledVehicles(inventoryVehicles.values())

    def _onLoading(self):
        item = self.item
        if item is None:
            return
        else:
            items = self.__itemsCache.items
            descriptor = item.descriptor
            itemPrice = item.buyPrices.itemPrice
            price = itemPrice.price
            currency = price.getCurrency()
            value = price.getSignValue(currency)
            money = items.stats.money
            isMoneyEnough = money >= price
            with self.viewModel.transaction() as tx:
                tx.setAbilityName(item.name)
                tx.setIcon(descriptor.iconName)
                tx.setCooldown(descriptor.cooldownSeconds)
                tx.setMiriumCost(descriptor.usageCost)
                tx.setCurrencyType(currency)
                tx.setAbilityPrice(value)
                if not isMoneyEnough:
                    tx.setRequiredMore(value - money.getSignValue(currency))
                tx.setInDepot(item.inventoryCount)
                inventoryVehicles = items.getVehicles(REQ_CRITERIA.INVENTORY)
                installedVehicles = self._getInstalledVehicles(item, inventoryVehicles)
                vehicles = tx.getInVehiclesList()
                vehicles.clear()
                for v in installedVehicles:
                    vehicles.addString(v.shortUserName)

                vehicles.invalidate()
                tx.setShowPriceBlock(self.__showPriceBlock)
            return
