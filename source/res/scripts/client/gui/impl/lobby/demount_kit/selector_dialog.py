# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/demount_kit/selector_dialog.py
import constants
from frameworks.wulf import ViewSettings, ViewFlags
from goodies.goodie_constants import DEMOUNT_KIT_ID
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control.wallet import WalletController
from gui.goodies.goodie_items import DemountKit
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.demount_kit.selector_dialog_item_model import SelectorDialogItemModel
from gui.impl.gen.view_models.views.lobby.demount_kit.selector_dialog_model import SelectorDialogModel
from gui.impl.lobby.demount_kit.item_base_dialog import BaseItemDialog
from gui.shop import showBuyGoldForEquipment
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache

class DemountOpDevDialog(BaseItemDialog):
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _wallet = dependency.descriptor(IWalletController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, compDescr):
        settings = ViewSettings(layoutID=R.views.lobby.demountkit.DemountWindow(), flags=ViewFlags.TOP_WINDOW_VIEW, model=SelectorDialogModel())
        super(DemountOpDevDialog, self).__init__(settings, compDescr)
        self.removalPrice = self._item.getRemovalPrice(self._itemsCache.items)

    @property
    def viewModel(self):
        return super(DemountOpDevDialog, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            args = []
            if tooltipId == TOOLTIPS_CONSTANTS.AWARD_DEMOUNT_KIT:
                args = [DEMOUNT_KIT_ID]
            if tooltipId in (TOOLTIPS_CONSTANTS.GOLD_ALTERNATIVE_INFO, TOOLTIPS_CONSTANTS.GOLD_ALTERNATIVE_STATS, TOOLTIPS_CONSTANTS.AWARD_DEMOUNT_KIT):
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
                window.load()
                return window
        return super(DemountOpDevDialog, self).createToolTip(event)

    def _initialize(self):
        super(DemountOpDevDialog, self)._initialize()
        self.viewModel.onSelectItem += self.__onSelectItem

    def _finalize(self):
        self.viewModel.onSelectItem -= self.__onSelectItem
        super(DemountOpDevDialog, self)._finalize()

    def _onInventoryResync(self, *args, **kwargs):
        dk = self._goodiesCache.getDemountKit()
        if not dk.enabled:
            self._onCancelClicked()
            return
        super(DemountOpDevDialog, self)._onInventoryResync(args, kwargs)
        self.removalPrice = self._item.getRemovalPrice(self._itemsCache.items)
        gold = self._itemsCache.items.stats.gold
        goldEnought = self._isGoldEnought(gold)
        with self.viewModel.transaction() as model:
            self._setFirstItem(model, dk.inventoryCount)
            self._setSecondItem(model, goldEnought)
            self._setSelectedItem(model, dk.inventoryCount, goldEnought)

    def _setFirstItem(self, model, dkCount):
        model.firstItem.setStorageCount(dkCount)
        model.firstItem.setIsDisabled(dkCount <= 0)
        model.firstItem.setIsItemEnough(dkCount > 0)

    def _setSecondItem(self, model, goldEnought):
        model.secondItem.setIsItemEnough(goldEnought)
        model.secondItem.setIsDisabled(not goldEnought)
        model.secondItem.setNeededItems(self.removalPrice.price.gold)
        model.secondItem.setIsDiscount(self.removalPrice.isActionPrice())

    def _setSelectedItem(self, model, dkCount, goldEnought):
        if self._isGoldSelected() and not goldEnought:
            if dkCount > 0:
                model.setSelectedItem(SelectorDialogItemModel.DEMOUNT_KIT)
            else:
                model.setSelectedItem(SelectorDialogItemModel.NOTHING)
        elif self._isDKSelected() and dkCount <= 0:
            if goldEnought:
                model.setSelectedItem(SelectorDialogItemModel.GOLD)
            else:
                model.setSelectedItem(SelectorDialogItemModel.NOTHING)
        elif self._isNothingSelected():
            if dkCount > 0:
                model.setSelectedItem(SelectorDialogItemModel.DEMOUNT_KIT)
            elif goldEnought:
                model.setSelectedItem(SelectorDialogItemModel.GOLD)

    def _isGoldSelected(self):
        return self.viewModel.getSelectedItem() == SelectorDialogItemModel.GOLD

    def _isDKSelected(self):
        return self.viewModel.getSelectedItem() == SelectorDialogItemModel.DEMOUNT_KIT

    def _isNothingSelected(self):
        return self.viewModel.getSelectedItem() == SelectorDialogItemModel.NOTHING

    def _isUseDemountKit(self):
        return self.viewModel.getSelectedItem() == SelectorDialogItemModel.DEMOUNT_KIT

    def _getAdditionalData(self):
        dk = self._goodiesCache.getDemountKit()
        return {'useDemountKit': self._isUseDemountKit(),
         'openSingleDemountWindow': dk and not dk.enabled}

    def _isGoldEnought(self, gold=None):
        _gold = gold or self._itemsCache.items.stats.gold
        return _gold >= self.removalPrice.price.gold

    def _setBaseParams(self, model):
        super(DemountOpDevDialog, self)._setBaseParams(model)
        dk = self._goodiesCache.getDemountKit()
        goldEnought = self._isGoldEnought()
        model.setTitleBody(R.strings.demount_kit.equipmentDemount.confirmation())
        self._setTitleArgs(self.viewModel.getTitleArgs(), (('equipment', R.strings.artefacts.dyn(self._item.name).name()),))
        model.setAcceptButtonText(R.strings.menu.moduleFits.removeName())
        model.setCancelButtonText(R.strings.dialogs.confirmBuyAndInstall.cancel())
        model.setDescription(R.strings.demount_kit.equipmentDemount.confirmation.description())
        self._setFirstItem(model, dk.inventoryCount)
        model.firstItem.setType(SelectorDialogItemModel.DEMOUNT_KIT)
        model.firstItem.setTooltipName(SelectorDialogItemModel.DK_TOOLTIP)
        self._setSecondItem(model, goldEnought)
        model.secondItem.setType(SelectorDialogItemModel.GOLD)
        model.secondItem.setTooltipName(self.__getWalletTooltipSettings(SelectorDialogItemModel.GOLD))
        if dk.inventoryCount > 0:
            model.setSelectedItem(SelectorDialogItemModel.DEMOUNT_KIT)
        elif goldEnought:
            model.setSelectedItem(SelectorDialogItemModel.GOLD)
        else:
            model.setSelectedItem(SelectorDialogItemModel.NOTHING)

    def _onAcceptClicked(self):
        goldEnought = self._isGoldEnought()
        dk = self._goodiesCache.getDemountKit()
        dkEnought = dk.inventoryCount > 0
        if not goldEnought and not dkEnought:
            showBuyGoldForEquipment(self.removalPrice.price.gold)
        else:
            super(DemountOpDevDialog, self)._onAcceptClicked()

    def __onSelectItem(self, args=None):
        if args is not None:
            selectedItem = args.get('selectedItem')
            self.viewModel.setSelectedItem(selectedItem)
        return

    def __getWalletTooltipSettings(self, btnType):
        currencyStatus = self._wallet.componentsStatuses.get(btnType, WalletController.STATUS.SYNCING)
        tooltip = SelectorDialogItemModel.GOLD_TOOLTIP
        if btnType in (SelectorDialogItemModel.GOLD,):
            if constants.IS_SINGAPORE and self._itemsCache.items.stats.mayConsumeWalletResources:
                tooltip = ''.join((btnType, 'AlternativeStats'))
            elif currencyStatus == WalletController.STATUS.AVAILABLE:
                tooltip = ''.join((btnType, 'AlternativeInfo'))
        return tooltip
