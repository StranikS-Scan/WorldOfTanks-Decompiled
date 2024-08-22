# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/price_cards_content/retrain_single_price_list.py
import typing
from frameworks.wulf import ViewSettings, Array
from gui.impl.auxiliary.tankman_operations import packSingleRetrain
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel, CardState
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_list_model import PriceListModel
from gui.impl.lobby.crew.dialogs.price_cards_content.base_price_list import BasePriceList
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, Money
from helpers_common import getFinalRetrainCost, isAllRetrainOperationFree
from items.tankmen import TankmanDescr
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Tankman import Tankman
    from gui.shared.gui_items.Vehicle import Vehicle
    from skeletons.gui.shared.utils.requesters import IShopRequester
_TOOLTIP_LOC = R.strings.tooltips.retrain.priceCard.disable

class RetrainSinglePriceList(BasePriceList):
    __slots__ = ('_tankman', '_vehicle', '_targetRole')

    def __init__(self, tankmanId, vehicleCD, targetRole=None):
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        self._vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        self._targetRole = targetRole
        settings = ViewSettings(R.views.lobby.crew.widgets.PriceList())
        settings.model = PriceListModel()
        super(RetrainSinglePriceList, self).__init__(settings)

    @property
    def _priceListPacker(self):
        return packSingleRetrain

    def _deselectCurrentCard(self, vm):
        if self._selectedCardIndex is None:
            return
        else:
            isUselessForTankmen, _, _, _ = self.selectedOperationData
            state = CardState.DISABLED if isUselessForTankmen else CardState.DEFAULT
            self._getCard(vm, self._selectedCardIndex).setCardState(state)
            return

    @property
    def isRoleChangeAvailable(self):
        _, _, cost, _ = self.selectedOperationData
        return cost is None or cost['skillsEfficiencyWithRoleChange'] >= 0

    @property
    def selectedOperationData(self):
        operationData = super(RetrainSinglePriceList, self).selectedOperationData
        return (None, None, None, None) if operationData is None else operationData

    @property
    def isAllRetrainOperationFree(self):
        return isAllRetrainOperationFree(self._tankman.descriptor, self._retrainCost)

    def updateTargetRole(self, role):
        if self._targetRole == role:
            return
        self._targetRole = role
        self._fillPrices()
        self._updateViewModel()

    @staticmethod
    def _getDisableTooltipData(isDiscount, isUseless, isDisableByRoleChange):
        if isDiscount:
            return (_TOOLTIP_LOC.discount.header(), _TOOLTIP_LOC.discount.body())
        if isUseless:
            return (_TOOLTIP_LOC.useless.header(), _TOOLTIP_LOC.useless.body())
        return (_TOOLTIP_LOC.roleChange.header(), _TOOLTIP_LOC.roleChange.body()) if isDisableByRoleChange else (R.invalid(), R.invalid())

    def _getOperationCustomData(self, tankman, cost):
        isOperationUseless, isOperationDisable, isAllOperationFree, newSE = self.getOperationUselessInfo(tankman, self._targetRole, self._vehicle, cost, self._retrainCost)
        header, body = self._getDisableTooltipData(isAllOperationFree and isOperationDisable, isOperationUseless, isOperationDisable)
        tooltipData = {'header': header,
         'body': body}
        return (newSE, isOperationUseless or isOperationDisable, tooltipData)

    def _getOperationData(self, cost):
        skillEfficiency, isDisabled, tooltipData = self._getOperationCustomData(self._tankman, cost)
        return (isDisabled,
         skillEfficiency,
         cost,
         tooltipData)

    def _fillPrices(self):
        shopRequester = self._itemsCache.items.shop
        defaultTankmanCost = shopRequester.defaults.tankmanCost
        self._priceData = []
        for idx, cost in enumerate(self._retrainCost):
            defCost = defaultTankmanCost[idx]
            credits, gold = getFinalRetrainCost(TankmanDescr(self._tankman.strCD), cost)
            if self.isAllRetrainOperationFree and not credits:
                credits = defCost.get(Currency.CREDITS, 0)
            itemPrice = ItemPrice(price=Money(credits=credits, gold=gold), defPrice=Money(credits=defCost.get(Currency.CREDITS, 0), gold=defCost.get(Currency.GOLD, 0)))
            self._priceData.append((itemPrice, self._getOperationData(cost), idx))

    def _onTankmanChanged(self, _):
        pass
