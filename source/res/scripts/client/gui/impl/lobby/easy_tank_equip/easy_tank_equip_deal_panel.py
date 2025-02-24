# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/easy_tank_equip_deal_panel.py
from typing import TYPE_CHECKING
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.proposal_model import ProposalType
from gui.impl.lobby.easy_tank_equip.easy_tank_equip_buy_price_builder import EasyTankEquipBuyPriceModelBuilder
from gui.impl.lobby.tank_setup.configurations.base import BaseDealPanel
from gui.shared.gui_items.fitting_item import canBuyWithGoldExchange
from gui.shared.money import ZERO_MONEY, Currency
if TYPE_CHECKING:
    from typing import Dict, Optional
    from collections import OrderedDict
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.money import Money
    from gui.impl.gen.view_models.views.lobby.tank_setup.common.deal_panel_model import DealPanelModel
    from gui.impl.lobby.easy_tank_equip.data_providers.base_data_provider import BaseDataProvider, PresetInfo

class EasyTankEquipDealPanel(BaseDealPanel):
    _IN_TANK = 'inTank'
    _KITS = 'demountKits'
    _DEF_PRICE = 'defPrice'
    _DISCOUNT = 'discount'
    _DEFAULT_PRICES = {_IN_TANK: 0,
     _KITS: 0,
     BaseDealPanel._IN_STORAGE: 0,
     BaseDealPanel._MONEY: ZERO_MONEY,
     _DEF_PRICE: ZERO_MONEY,
     _DISCOUNT: ZERO_MONEY}
    _prices = _DEFAULT_PRICES.copy()

    @classmethod
    def updateDealPanelPrice(cls, vehicle, presets, dealPanelModel):
        cls._prices.update(cls._DEFAULT_PRICES)
        for proposalType, selectedPreset in presets.items():
            cls.addItem(vehicle, selectedPreset, cls._prices)
            if proposalType == ProposalType.OPT_DEVICES:
                cls._prices[cls._KITS] += selectedPreset.demountKits

        cls._fillDealPanelPrice(dealPanelModel)

    @classmethod
    def addItem(cls, vehicle, item, prices):
        prices[cls._IN_TANK] += item.installedItemsCount
        prices[cls._IN_STORAGE] += item.storedItemsCount
        prices[cls._MONEY] += item.itemPrice.price
        prices[cls._DEF_PRICE] += item.itemPrice.defPrice
        prices[cls._DISCOUNT] += item.itemPrice.getActionPrcAsMoney()

    @classmethod
    def updatePrices(cls, dealPanelModel):
        cls._fillDealPanelPrice(dealPanelModel)

    @classmethod
    def getTotalPrice(cls):
        return cls._prices[cls._MONEY]

    @classmethod
    def _fillDealPanelPrice(cls, model):
        model.setTotalItemsInStorage(cls._prices[cls._IN_STORAGE])
        model.setTotalItemsInstalled(cls._prices[cls._IN_TANK])
        model.setDemountKitsCount(cls._prices[cls._KITS])
        model.getPrice().clear()
        model.getDefPrice().clear()
        model.getDiscount().clear()
        EasyTankEquipBuyPriceModelBuilder.fillPriceModel(model, cls._prices[cls._MONEY], action=cls._prices[cls._DISCOUNT], defPrice=cls._prices[cls._DEF_PRICE], checkBalanceAvailability=True)
        model.getPrice().invalidate()
        cls._updateDisabled(cls._prices, model)

    @classmethod
    def _updateDisabled(cls, prices, dealPanelModel):
        stats = cls._itemsCache.items.stats
        goldAmountInPriceForExchange = 0
        availableGoldForExchange = stats.money.gold - cls._prices[cls._MONEY].gold
        isEnabled = stats.mayConsumeWalletResources and availableGoldForExchange >= 0 and canBuyWithGoldExchange(cls._prices[cls._MONEY].replace(Currency.GOLD, goldAmountInPriceForExchange), stats.money.replace(Currency.GOLD, availableGoldForExchange), cls._itemsCache.items.shop.exchangeRate)
        dealPanelModel.setIsDisabled(not isEnabled)


class EasyTankEquipBottomContent(SubModelPresenter):

    def __init__(self, viewModel, parentView, providers):
        super(EasyTankEquipBottomContent, self).__init__(viewModel, parentView)
        self.__providers = providers

    @staticmethod
    def getTotalPrice():
        return EasyTankEquipDealPanel.getTotalPrice()

    def initialize(self, *args, **kwargs):
        super(EasyTankEquipBottomContent, self).initialize(*args, **kwargs)
        self.update()

    def update(self):
        presets = self.__getSelectedPresets()
        presetsAreNotEmpty = True if presets else False
        self.getViewModel().setCanCancel(presetsAreNotEmpty)
        self.getViewModel().setCanAccept(presetsAreNotEmpty)
        EasyTankEquipDealPanel.updateDealPanelPrice(None, presets, self.getViewModel())
        return

    def updatePrices(self):
        EasyTankEquipDealPanel.updatePrices(self.getViewModel())

    def __getSelectedPresets(self):
        presets = {}
        for proposalType, provider in self.__providers.items():
            if provider.isProposalSelected and not provider.isCurrentPresetDisabledForApplying():
                presets[proposalType] = provider.presets[provider.currentPresetIndex]

        return presets
