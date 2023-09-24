# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/price_cards_content/retrain_price_list.py
import typing
from frameworks.wulf import ViewSettings, Array
from gui.impl.auxiliary.tankman_operations import packRetrain
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_list_model import PriceListModel
from gui.impl.lobby.crew.dialogs.price_cards_content.base_price_list import BasePriceList
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, Money
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import ShopRequester
    from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel
    from gui.shared.gui_items.Tankman import Tankman
    from gui.shared.gui_items.Vehicle import Vehicle

class RetrainPriceList(BasePriceList):
    __slots__ = ('_tankmen', '_vehicle')

    def __init__(self, tankmenIds, vehicleCD):
        self._tankmen = [ self._itemsCache.items.getTankman(tankmanId) for tankmanId in tankmenIds ]
        self._vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        settings = ViewSettings(R.views.lobby.crew.widgets.PriceList())
        settings.model = PriceListModel()
        super(RetrainPriceList, self).__init__(settings)

    @property
    def _priceListPacker(self):
        return packRetrain

    def _getTankmanRoleLevel(self, tankman, cost):
        roleLevel = tankman.roleLevel
        sameVehicle = self._vehicle.intCD == tankman.vehicleNativeDescr.type.compactDescr
        sameVehicleType = self._vehicle.type == tankman.vehicleNativeType
        defaultTrainingLevel = cost['roleLevel']
        baseRoleLoss = cost['baseRoleLoss']
        classChangeRoleLoss = cost['classChangeRoleLoss']
        if sameVehicle:
            return (defaultTrainingLevel, roleLevel >= defaultTrainingLevel)
        else:
            if sameVehicleType:
                trainingLossMultiplier = baseRoleLoss
            else:
                trainingLossMultiplier = baseRoleLoss + classChangeRoleLoss
            newRoleLevel = int(roleLevel - roleLevel * trainingLossMultiplier)
            if newRoleLevel < defaultTrainingLevel:
                newRoleLevel = defaultTrainingLevel
            return (newRoleLevel, newRoleLevel < defaultTrainingLevel)

    def _getOperationData(self, cost):
        roleLevelRange = []
        isUselessForTankman = []
        for tankman in self._tankmen:
            trainingLevel, isUseless = self._getTankmanRoleLevel(tankman, cost)
            roleLevelRange.append(trainingLevel)
            isUselessForTankman.append(isUseless)

        minRoleLevel = min(roleLevelRange)
        maxRoleLevel = max(roleLevelRange)
        return (minRoleLevel, maxRoleLevel, isUselessForTankman)

    def _fillPrices(self):
        shopRequester = self._itemsCache.items.shop
        tankmanCost = shopRequester.tankmanCost
        defaultTankmanCost = shopRequester.defaults.tankmanCost
        self._priceData = []
        for idx, cost in enumerate(tankmanCost):
            defCost = defaultTankmanCost[idx]
            itemPrice = ItemPrice(price=Money(credits=cost.get(Currency.CREDITS, 0), gold=cost.get(Currency.GOLD, 0)), defPrice=Money(credits=defCost.get(Currency.CREDITS, 0), gold=defCost.get(Currency.GOLD, 0)))
            self._priceData.append((itemPrice, self._getOperationData(cost), idx))

    def _onTankmanChanged(self, _):
        pass
