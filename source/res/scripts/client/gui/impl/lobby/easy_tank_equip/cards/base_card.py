# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/cards/base_card.py
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.preset_model import PresetModel
from gui.impl.lobby.easy_tank_equip.easy_tank_equip_buy_price_builder import EasyTankEquipBuyPriceModelBuilder
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.proposal_model import ProposalModel
    from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.slot_info_model import SlotInfoModel
    from gui.impl.lobby.easy_tank_equip.data_providers.base_data_provider import BaseDataProvider, PresetInfo, SlotInfo
    from gui.shared.money import Money
    from typing import Optional

class BaseCard(SubModelPresenter):

    def __init__(self, viewModel, parentView, provider):
        self.provider = provider
        super(BaseCard, self).__init__(viewModel, parentView)

    @property
    def viewModel(self):
        return super(BaseCard, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(BaseCard, self).initialize(*args, **kwargs)
        self.updateModel()

    def finalize(self):
        super(BaseCard, self).finalize()
        self.provider = None
        return

    def updateModel(self):
        with self.viewModel.transaction() as tx:
            self.__fillProposalModel(model=tx)
            self.__fillPresetsModels(self.provider.presets, model=tx)

    def _getEvents(self):
        return super(BaseCard, self)._getEvents() + ((self.provider.onSelect, self._onSelect),
         (self.provider.onSwitchPreset, self._onSwitchPreset),
         (self.provider.onPricesUpdated, self._onPricesUpdated),
         (self.provider.onPresetsUpdated, self._onPresetsUpdated))

    def _getPreset(self):
        raise NotImplementedError

    def _onSelect(self):
        self.viewModel.setSelected(self.provider.isProposalSelected)

    def _onSwitchPreset(self):
        self.viewModel.setPresetIndex(self.provider.currentPresetIndex)

    def _onPricesUpdated(self, balance):
        presetsModels = self.viewModel.getPresets()
        preset = self._getPreset()
        for model, presetInfo in zip(presetsModels, self.provider.presets):
            preset.updatePresetModelPrice(model, presetInfo, balance)

    def _onPresetsUpdated(self):
        self.updateModel()

    @replaceNoneKwargsModel
    def __fillProposalModel(self, model=None):
        model.setSelected(self.provider.isProposalSelected)
        model.setDisableReason(self.provider.proposalDisableReason)
        model.setPresetIndex(self.provider.currentPresetIndex)

    @replaceNoneKwargsModel
    def __fillPresetsModels(self, proposalPresets, model=None):
        presets = model.getPresets()
        presets.clear()
        preset = self._getPreset()
        for presetInfo in proposalPresets:
            presetModel = preset.getPresetModel()
            preset.fillPresetModel(presetModel, presetInfo, self.provider.lastCheckedBalance)
            presets.addViewModel(presetModel)

        presets.invalidate()


class BasePreset(object):

    @classmethod
    def fillPresetModel(cls, model, presetInfo, balance=None):
        model.setInstalled(presetInfo.installed)
        model.setStoredItemsCount(presetInfo.storedItemsCount)
        model.setInstalledItemsCount(presetInfo.installedItemsCount)
        model.setDisableReason(presetInfo.disableReason)
        cls.updatePresetModelPrice(model, presetInfo, balance)

    @classmethod
    def fillSlotInfoModel(cls, model, slotInfo):
        model.setIsInStorage(bool(slotInfo.storedItemsCount))
        model.setIsOnVehicle(bool(slotInfo.installedItemsCount))
        PriceModelBuilder.fillPriceModel(priceModel=model, price=slotInfo.itemPrice.price, action=slotInfo.itemPrice.getActionPrcAsMoney(), defPrice=slotInfo.itemPrice.defPrice)

    @classmethod
    def getPresetModel(cls):
        return PresetModel()

    @classmethod
    def updatePresetModelPrice(cls, model, presetInfo, balance=None):
        EasyTankEquipBuyPriceModelBuilder.clearPriceModel(model.price)
        EasyTankEquipBuyPriceModelBuilder.fillPriceModel(priceModel=model.price, price=presetInfo.itemPrice.price, action=presetInfo.itemPrice.getActionPrcAsMoney(), defPrice=presetInfo.itemPrice.defPrice, balance=balance, checkBalanceAvailability=True)
