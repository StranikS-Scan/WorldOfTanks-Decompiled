# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/price_cards_content/base_price_list.py
import typing
import Event
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.tankman_operations import packPriceList
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel, CardState
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_list_model import PriceListModel
from gui.impl.pub import ViewImpl
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from helpers_common import getRetrainCost, isAllRetrainOperationFree
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from skeletons.gui.shared.utils.requesters import IShopRequester
    from gui.shared.gui_items.Vehicle import Vehicle
GOLD_OPERATION = 2

def _convertMoneyToTuple(money):
    return (money.credits, money.gold, money.crystal)


class BasePriceList(ViewImpl):
    __slots__ = ('_selectedCardIndex', '_priceData', 'onPriceChange', '_retrainCost')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, settings):
        shopRequester = self._itemsCache.items.shop
        self._retrainCost = getRetrainCost(shopRequester.tankmanCost, shopRequester.tankman['retrain']['options'])
        self._selectedCardIndex = None
        self._priceData = []
        self._fillPrices()
        self.onPriceChange = Event.Event()
        super(BasePriceList, self).__init__(settings)
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            index = int(event.getArgument('index'))
            itemPrice, _, _ = self._getPriceData(index)
            if not itemPrice:
                return
            if itemPrice.isActionPrice():
                specialAlias = (None,
                 None,
                 _convertMoneyToTuple(itemPrice.price),
                 _convertMoneyToTuple(itemPrice.defPrice),
                 True,
                 False,
                 None,
                 True)
                return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.ACTION_PRICE, specialArgs=specialAlias)
            shortage = self._itemsCache.items.stats.money.getShortage(itemPrice.defPrice)
            if bool(shortage):
                currency = shortage.getCurrency()
                return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage.get(currency), currency))
        return super(BasePriceList, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def selectedPriceData(self):
        return self._getPriceData(self._selectedCardIndex)

    @property
    def selectedOperationData(self):
        _, operationData, _ = self.selectedPriceData
        return operationData

    def getOperationUselessInfo(self, tankman, targetRole, vehicle, cost, retrainCost, isMassRetrain=False):
        sameVehicle = vehicle.intCD == tankman.vehicleNativeDescr.type.compactDescr
        sameRole = targetRole == tankman.role
        isRoleChangeDisable = cost['skillsEfficiencyWithRoleChange'] < 0
        isOperationDisable = isRoleChangeDisable and not sameRole
        isAllOperationFree = isAllRetrainOperationFree(tankman.descriptor, retrainCost)
        if isAllOperationFree:
            isOperationDisable = not bool(cost['gold'])
        newSE = self.__getMaxTmanSkillEfficiencyForEachOperation(cost, tankman, not sameRole, isOperationDisable, isMassRetrain)
        isOperationUseless = sameVehicle and sameRole and tankman.skillsEfficiency >= newSE
        return (isOperationUseless,
         isOperationDisable,
         isAllOperationFree,
         newSE)

    @property
    def _priceListPacker(self):
        return packPriceList

    def _deselectCurrentCard(self, vm):
        if self._selectedCardIndex is None:
            return
        else:
            self._getCard(vm, self._selectedCardIndex).setCardState(CardState.DEFAULT)
            return

    def _selectCard(self, vm, index=None):
        self._deselectCurrentCard(vm)
        if index is not None:
            self._getCard(vm, index).setCardState(CardState.SELECTED)
        self._selectedCardIndex = index
        self.onPriceChange(self._selectedCardIndex)
        return

    def _fillPrices(self):
        pass

    def _onLoading(self, *args, **kwargs):
        super(BasePriceList, self)._onLoading(*args, **kwargs)
        self._updateViewModel()

    @staticmethod
    def _getCard(vm, index):
        return vm.getCardsList().getValue(index)

    def _getPriceData(self, index):
        return self._priceData[index] if index is not None and len(self._priceData) >= index + 1 else (None, None, None)

    def _getEvents(self):
        return ((self.viewModel.onCardClick, self._onCardClick), (self._itemsCache.onSyncCompleted, self._onCacheResync))

    def _getCallbacks(self):
        return (('stats.gold', self._onGoldUpdate),
         ('stats.credits', self._onCreditsUpdate),
         ('inventory.8.compDescr', self._onTankmanChanged),
         ('cache.mayConsumeWalletResources', self._onConsumeWalletUpdate))

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        cardList = vm.getCardsList()
        cardList.clear()
        self._priceListPacker(cardList, self._priceData)
        if self._selectedCardIndex is not None:
            card = cardList.getValue(self._selectedCardIndex)
            cardIndex = None if card.getCardState() == CardState.DISABLED else self._selectedCardIndex
            self._selectCard(vm, cardIndex)
        cardList.invalidate()
        return

    def _onTankmanChanged(self, data):
        self._updateViewModel()

    def _onConsumeWalletUpdate(self, *_):
        self._updateViewModel()

    def _onCreditsUpdate(self, *_):
        self._updateViewModel()

    def _onGoldUpdate(self, *_):
        self._updateViewModel()

    def _onCacheResync(self, reason, _):
        if reason in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC):
            self._fillPrices()
            self._updateViewModel()

    def _onCardClick(self, args):
        with self.viewModel.transaction() as vm:
            self._selectCard(vm, int(args.get('index', 0)))

    def __getMaxTmanSkillEfficiencyForEachOperation(self, cost, tankman, isRoleChanging, isOperationDisable, isMassRetrain):
        changingRoleSE = cost['skillsEfficiencyWithRoleChange'] if isRoleChanging and cost['skillsEfficiencyWithRoleChange'] > 0 and not isOperationDisable else cost['skillsEfficiency']
        if isOperationDisable and not isMassRetrain:
            return changingRoleSE
        isAllRetrainOptFree = isAllRetrainOperationFree(tankman.descriptor, self._retrainCost)
        return self._retrainCost[GOLD_OPERATION]['skillsEfficiency'] if isAllRetrainOptFree else changingRoleSE
