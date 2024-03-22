# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/price_cards_content/retrain_massive_price_list.py
import typing
from frameworks.wulf import ViewSettings, Array
from gui.impl.auxiliary.tankman_operations import packMassRetrain
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_list_model import PriceListModel
from gui.impl.lobby.crew.dialogs.price_cards_content.base_price_list import BasePriceList
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel, CardState
from gui.shared.money import Currency, Money
from helpers_common import getFinalRetrainCost
from items.tankmen import TankmanDescr
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Tankman import Tankman
    from gui.shared.gui_items.Vehicle import Vehicle
DEFAULT_OPERATION_DATA = {'isPriceApplicable': None,
 'isCardDisabled': None,
 'skillEfficiencies': None,
 'cost': None}

class RetrainMassivePriceList(BasePriceList):
    __slots__ = ('_tankmen', '_vehicle')

    def __init__(self, tankmenIds, vehicleCD):
        self._tankmen = [ self._itemsCache.items.getTankman(tankmanId) for tankmanId in tankmenIds ]
        self._vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        settings = ViewSettings(R.views.lobby.crew.widgets.PriceList())
        settings.model = PriceListModel()
        super(RetrainMassivePriceList, self).__init__(settings)

    @property
    def _priceListPacker(self):
        return packMassRetrain

    def _deselectCurrentCard(self, vm):
        if self._selectedCardIndex is None:
            return
        else:
            state = CardState.DISABLED if all(self.selectedOperationData['isCardDisabled']) else CardState.DEFAULT
            self._getCard(vm, self._selectedCardIndex).setCardState(state)
            return

    @property
    def selectedOperationData(self):
        operationData = super(RetrainMassivePriceList, self).selectedOperationData
        return DEFAULT_OPERATION_DATA if operationData is None else operationData

    def _getTankmanSkillsEfficiency(self, tankman, cost):
        isOperationUseless, isOperationDisabled, _, newSE = self.getOperationUselessInfo(tankman, tankman.role, self._vehicle, cost, self._retrainCost, True)
        return (newSE, isOperationUseless, isOperationDisabled)

    def _getOperationData(self, cost):
        ser = []
        isApplicableForTankmen = []
        isCardDisabledForAllTankmen = []
        for tankman in self._tankmen:
            se, isUseless, isDisabled = self._getTankmanSkillsEfficiency(tankman, cost)
            ser.append(se)
            isApplicableForTankmen.append(isUseless)
            isCardDisabledForAllTankmen.append(isUseless or isDisabled)

        return {'isPriceApplicable': isApplicableForTankmen,
         'isCardDisabled': isCardDisabledForAllTankmen,
         'skillEfficiencies': ser,
         'cost': cost}

    def _fillPrices(self):
        tankmanCost = self._itemsCache.items.shop.tankmanCost
        defaultTankmanCost = self._itemsCache.items.shop.defaults.tankmanCost
        self._priceData = []
        for idx, cost in enumerate(self._retrainCost):
            currCost = tankmanCost[idx]
            defCost = defaultTankmanCost[idx]
            itemPrice = ItemPrice(price=Money(credits=currCost.get(Currency.CREDITS, 0), gold=currCost.get(Currency.GOLD, 0)), defPrice=Money(credits=defCost.get(Currency.CREDITS, 0), gold=defCost.get(Currency.GOLD, 0)))
            self._priceData.append((itemPrice, self._getOperationData(cost), idx))

    def _onTankmanChanged(self, _):
        pass

    def __isAllTankmenHasFreeOperation(self, tankmen, cost):
        allCosts = []
        for tankman in tankmen:
            allCosts += getFinalRetrainCost(TankmanDescr(tankman.strCD), cost)

        return not bool(sum(allCosts))
