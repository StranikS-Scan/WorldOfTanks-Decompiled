# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/lootboxes/bonus_items_names.py
from frameworks.wulf import ViewModel

class BonusItemsNames(ViewModel):
    __slots__ = ()
    TOYS = 'ny21Toys'
    PREMIUM_PLUS = 'premium_plus'
    EXTRA_SLOT = 'ny21:extraSlot'
    VARIADIC_DISCOUNT = 'variadicDiscount'
    OTHER = 'other'

    def __init__(self, properties=0, commands=0):
        super(BonusItemsNames, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(BonusItemsNames, self)._initialize()
