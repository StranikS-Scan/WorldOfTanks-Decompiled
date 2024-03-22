# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/retrain_massive_dialog.py
from typing import TYPE_CHECKING
import BigWorld
import SoundGroups
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.customization.shared import getPurchaseGoldForCredits, getPurchaseMoneyState, MoneyForPurchase
from gui.impl.auxiliary.tankman_operations import ITEM_PRICE_FREE, packRetrainTankman
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.dialogs.widgets.single_price import SinglePriceWidget
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_model import DialogTankmanModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.retrain_massive_dialog_model import RetrainMassiveDialogModel
from gui.impl.lobby.crew.crew_sounds import SOUNDS
from gui.impl.lobby.crew.dialogs.price_cards_content.retrain_massive_price_list import RetrainMassivePriceList
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TAGS
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Money
from gui.shop import showBuyGoldForCrew
from helpers import dependency
from helpers_common import getFinalRetrainCost, getRetrainCost
from items.tankmen import TankmanDescr
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl.lobby.crew.crew_helpers.tankman_helpers import getPriceDiscountMassRetrain
if TYPE_CHECKING:
    from skeletons.gui.shared.utils.requesters import IShopRequester
_LOC = R.strings.dialogs.retrain

class RetrainMassiveDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankmen', '_vehicle', '_selectedTankmenIds', '_priceListContent', '_toolTipMgr', '_retrainCost')
    LAYOUT_ID = R.views.lobby.crew.dialogs.RetrainMassiveDialog()
    VIEW_MODEL = RetrainMassiveDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, tankmenIds, vehicleCD, **kwargs):
        self._tankmen = [ self._itemsCache.items.getTankman(tankmanId) for tankmanId in tankmenIds ]
        self._vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        self._selectedTankmenIds = []
        self._priceListContent = RetrainMassivePriceList(tankmenIds, vehicleCD)
        self._toolTipMgr = self._appLoader.getApp().getToolTipMgr()
        shopRequester = self._itemsCache.items.shop
        self._retrainCost = getRetrainCost(shopRequester.tankmanCost, shopRequester.tankman['retrain']['options'])
        super(RetrainMassiveDialog, self).__init__(**kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId == TooltipConstants.CREW_SKILL_UNTRAINED:
                args = ()
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED
            if tooltipId == TooltipConstants.SKILLS_EFFICIENCY:
                isShowDiscount = True
                args = (event.getArgument('tankmanInvId'), event.getArgument('skillEfficiency'), isShowDiscount)
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.SKILLS_EFFICIENCY, args, event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                return tooltipId
        return super(RetrainMassiveDialog, self).createToolTip(event)

    def _getCallbacks(self):
        return (('inventory.1.compDescr', self._onVehiclesInventoryUpdate),)

    def _getEvents(self):
        return ((self._priceListContent.onPriceChange, self._onPriceChange),)

    def _onPriceChange(self, index=None):
        submitBtn = self.getButton(DialogButtons.SUBMIT)
        if submitBtn is not None:
            submitBtn.isDisabled = index is None
        with self.viewModel.transaction() as vm:
            vm.setIsPriceSelected(index is not None)
            self._updateTankmen(vm)
            self._updatePrice(vm, index)
        return

    def _onVehiclesInventoryUpdate(self, diff):
        if self._vehicle.invID in diff and diff[self._vehicle.invID] is None:
            self.destroyWindow()
        return

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
        self.setChildView(SinglePriceWidget.LAYOUT_DYN_ACCESSOR(), SinglePriceWidget(R.strings.dialogs.retrain.price(), ItemPrice(Money(gold=0, credits=0), Money(gold=0, credits=0)), CurrencySize.BIG, showDiscountValue=False))
        self.setChildView(self._priceListContent.layoutID, self._priceListContent)
        self.addButton(ConfirmButton(_LOC.submit(), isDisabled=True, buttonType=ButtonType.MAIN))
        self.addButton(CancelButton(_LOC.cancel()))
        self._initModel()
        self._updateViewModel()
        super(RetrainMassiveDialog, self)._onLoading(*args, **kwargs)

    def _getWarning(self):
        return R.strings.dialogs.retrain.warning.premiumVehicle() if self._tankmen[0].descriptor.canUseSkills(self._vehicle.descriptor.type) else R.invalid()

    def _initModel(self):
        with self.viewModel.transaction() as vm:
            vm.setWarning(self._getWarning())
            tankmenVL = vm.getTankmen()
            tankmenVL.clear()
            for _, tankman in enumerate(self._tankmen):
                tankmanModel = DialogTankmanModel()
                packRetrainTankman(tankmanModel, tankman)
                tankmenVL.addViewModel(tankmanModel)

            fillVehicleInfo(vm.targetVehicle, self._vehicle, tags=[VEHICLE_TAGS.PREMIUM])

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        vm.setIsPriceVisible(False)
        self._updateTankmen(vm)

    def _updateTankmen(self, vm):
        isApplicableForTankmen = self._priceListContent.selectedOperationData['isPriceApplicable']
        skillEfficienciesAfter = self._priceListContent.selectedOperationData['skillEfficiencies']
        tankmenVL = vm.getTankmen()
        self._selectedTankmenIds = []
        for idx, tankman in enumerate(self._tankmen):
            tankmanModel = tankmenVL.getValue(idx)
            currentVehicleSkillsEfficiency = tankman.currentVehicleSkillsEfficiency
            if skillEfficienciesAfter is None or isApplicableForTankmen is None:
                tankmanModel.setSkillEfficiency(currentVehicleSkillsEfficiency)
                tankmanModel.setIsSelected(False)
            skillEfficiencyAfter = skillEfficienciesAfter[idx]
            isRetrainUseless = isApplicableForTankmen[idx]
            tankmanModel.setSkillEfficiency(tankman.currentVehicleSkillsEfficiency if isRetrainUseless else skillEfficiencyAfter)
            tankmanModel.setIsSelected(not isRetrainUseless)
            if not isRetrainUseless:
                self._selectedTankmenIds.append(tankman.invID)
                if skillEfficiencyAfter != currentVehicleSkillsEfficiency:
                    SoundGroups.g_instance.playSound2D(SOUNDS.CREW_PERK_UPGRADE)

        tankmenVL.invalidate()
        return

    def _updatePrice(self, vm, idx):
        price = self.getChildView(SinglePriceWidget.LAYOUT_DYN_ACCESSOR())
        itemPrice, priceData, _ = self._priceListContent.selectedPriceData
        vm.setIsPriceVisible(itemPrice and itemPrice != ITEM_PRICE_FREE)
        if price is None or itemPrice is None:
            return
        else:
            goldSum, creditsSum = getPriceDiscountMassRetrain(idx, priceData['isPriceApplicable'], self._tankmen)
            finalPrice = Money(credits=creditsSum, gold=goldSum)
            itemPrice = ItemPrice(price=finalPrice, defPrice=Money(credits=itemPrice.defPrice.credits, gold=itemPrice.defPrice.gold) * len(self._selectedTankmenIds))
            price.updatePrice(itemPrice)
            return

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            if not self._retrainTankmen():
                return
        super(RetrainMassiveDialog, self)._setResult(result)

    def _retrainTankmen(self):
        _, priceData, retrainKey = self._priceListContent.selectedPriceData
        goldSum, creditsSum = getPriceDiscountMassRetrain(retrainKey, priceData['isPriceApplicable'], self._tankmen)
        money = Money(credits=creditsSum, gold=goldSum)
        purchaseMoneyState = getPurchaseMoneyState(money)
        if purchaseMoneyState is MoneyForPurchase.NOT_ENOUGH:
            showBuyGoldForCrew(goldSum)
            return False
        elif purchaseMoneyState is MoneyForPurchase.ENOUGH_WITH_EXCHANGE:
            purchaseGold = getPurchaseGoldForCredits(money)
            event_dispatcher.showExchangeCurrencyWindowModal(currencyValue=purchaseGold)
            return False
        else:
            doActions = []
            for tankmanInvID in self._selectedTankmenIds:
                tankman = self._itemsCache.items.getTankman(tankmanInvID)
                if tankman is None:
                    continue
                doActions.append((factory.RETRAIN_TANKMAN,
                 tankmanInvID,
                 self._vehicle.intCD,
                 retrainKey,
                 0))

            BigWorld.player().doActions(doActions)
            return True

    def __getTankmanFinalPrice(self, tankman, idx):
        return getFinalRetrainCost(TankmanDescr(tankman.strCD), self._retrainCost[idx])
