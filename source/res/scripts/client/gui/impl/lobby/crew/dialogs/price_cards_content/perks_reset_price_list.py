# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/price_cards_content/perks_reset_price_list.py
import typing
from frameworks.wulf import ViewSettings, Array
from gui.impl.auxiliary.tankman_operations import packPerksResetTankmanAfter, packPerksResetTankmanBefore, packSkillReset
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_tankman_model import CrewWidgetTankmanModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.perks_reset_content_model import PerksResetContentModel
from gui.impl.lobby.crew.dialogs.price_cards_content.base_price_list import BasePriceList
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, Money
from items.tankmen import TankmanDescr
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import ShopRequester
    from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel
DEFAULT_XP_REUSE_FRACTION = 0.8

class PerksResetPriceList(BasePriceList):
    __slots__ = ('_tankman', '_goldOptionKey')

    def __init__(self, tankmanId):
        self._goldOptionKey = None
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        settings = ViewSettings(R.views.lobby.crew.dialogs.PerksResetContent())
        settings.model = PerksResetContentModel()
        super(PerksResetPriceList, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isRecertification(self):
        return self._selectedCardIndex + 1 == len(self.viewModel.getCardsList())

    @property
    def goldOptionKey(self):
        return self._goldOptionKey

    @property
    def _priceListPacker(self):
        return packSkillReset

    def _onLoading(self, *args, **kwargs):
        self.viewModel.getTankmen().addViewModel(CrewWidgetTankmanModel())
        super(PerksResetPriceList, self)._onLoading(*args, **kwargs)
        self._updateTankmenBefore(self.viewModel)

    def _getCallbacks(self):
        callbacks = typing.cast(typing.Tuple, super(PerksResetPriceList, self)._getCallbacks())
        return callbacks + (('goodies', self._onGoodiesUpdate),)

    def _onGoodiesUpdate(self, *_):
        self._updateViewModel()

    def _selectCard(self, vm, index=None):
        super(PerksResetPriceList, self)._selectCard(vm, index)
        self._updateTankmanAfter(vm)
        vm.getTankmen().invalidate()

    def _updateTankmenBefore(self, vm):
        vmTankman = vm.getTankmen().getValue(0)
        packPerksResetTankmanBefore(vmTankman, self._tankman)

    def _updateTankmanAfter(self, vm):
        tankmenList = vm.getTankmen()
        isTankmanAfter = len(tankmenList) > 1
        if isTankmanAfter and self._selectedCardIndex is None:
            tankmenList.remove(1)
            return
        else:
            vmTankman = tankmenList.getValue(1) if isTankmanAfter else CrewWidgetTankmanModel()
            if not isTankmanAfter:
                tankmenList.addViewModel(vmTankman)
            tmanDescr = TankmanDescr(self._tankman.strCD)
            _, factor, _ = self._getPriceData(self._selectedCardIndex)
            xpReuseFraction = factor if factor else 1
            tmanDescr.dropSkills(xpReuseFraction)
            tankman = Tankman(tmanDescr.makeCompactDescr())
            tankman.setCombinedRoles(self._tankman.roles())
            packPerksResetTankmanAfter(vmTankman, tankman)
            return

    def _fillPrices(self):
        shopRequester = self._itemsCache.items.shop
        dropSkillsCost = shopRequester.dropSkillsCost
        defaultDropSkillsCost = shopRequester.defaults.dropSkillsCost
        self._priceData = []
        for key, cost in dropSkillsCost.iteritems():
            if cost['gold'] > 0:
                self._goldOptionKey = key
            defCost = defaultDropSkillsCost.get(key, {})
            itemPrice = ItemPrice(price=Money(credits=cost.get(Currency.CREDITS, 0), gold=cost.get(Currency.GOLD, 0)), defPrice=Money(credits=defCost.get(Currency.CREDITS, 0), gold=defCost.get(Currency.GOLD, 0)))
            self._priceData.append((itemPrice, cost.get('xpReuseFraction', DEFAULT_XP_REUSE_FRACTION), key))

    def _onTankmanChanged(self, data):
        tankmanId = self._tankman.invID
        if tankmanId in data:
            if data[tankmanId] is None:
                self.destroyWindow()
                return
            self._fillPrices()
            self._updateViewModel()
        return
