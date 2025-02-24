# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/easy_tank_equip_buy_price_builder.py
import typing
from gui.shared.money import Currency
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
if typing.TYPE_CHECKING:
    from typing import Tuple, Dict, Union, Iterable
    from gui.shared.money import Money
    Price = Union[Money, Dict]

class EasyTankEquipBuyPriceModelBuilder(BuyPriceModelBuilder):

    @classmethod
    def _getCurrencyIterator(cls, price):
        order = (Currency.CRYSTAL,
         Currency.EQUIP_COIN,
         Currency.GOLD,
         Currency.CREDITS)
        for c in order:
            value = price.get(c)
            if value is not None:
                yield (c, value)

        return
