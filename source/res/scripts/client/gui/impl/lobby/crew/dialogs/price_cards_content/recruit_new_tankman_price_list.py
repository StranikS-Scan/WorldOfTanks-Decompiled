# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/price_cards_content/recruit_new_tankman_price_list.py
import typing
from frameworks.wulf import ViewSettings, Array
from gui.impl.auxiliary.tankman_operations import packRecruit
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_list_model import PriceListModel
from gui.impl.lobby.crew.dialogs.price_cards_content.base_price_list import BasePriceList
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, Money
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import ShopRequester
    from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel

class RecruitNewTankmanPriceList(BasePriceList):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.crew.widgets.PriceList())
        settings.model = PriceListModel()
        super(RecruitNewTankmanPriceList, self).__init__(settings)

    @property
    def _priceListPacker(self):
        return packRecruit

    def _fillPrices(self):
        shopRequester = self._itemsCache.items.shop
        opts = shopRequester.tankman['recruit']['options']
        optsDef = shopRequester.defaults.tankman['recruit']['options']
        self._priceData = []
        for idx, (option, optionDef) in enumerate(zip(opts, optsDef)):
            itemPrice = ItemPrice(price=Money(credits=option.get(Currency.CREDITS, 0), gold=option.get(Currency.GOLD, 0)), defPrice=Money(credits=optionDef.get(Currency.CREDITS, 0), gold=optionDef.get(Currency.GOLD, 0)))
            self._priceData.append((itemPrice, option, idx))

    def _onTankmanChanged(self, _):
        pass
