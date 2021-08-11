# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/eleventh_birthday_calendar/shop_birthday_section_entry_point_view_model.py
from frameworks.wulf import ViewModel

class ShopBirthdaySectionEntryPointViewModel(ViewModel):
    __slots__ = ('openShopBirthdaySection',)

    def __init__(self, properties=1, commands=1):
        super(ShopBirthdaySectionEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getTokenQuantity(self):
        return self._getNumber(0)

    def setTokenQuantity(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(ShopBirthdaySectionEntryPointViewModel, self)._initialize()
        self._addNumberProperty('tokenQuantity', 0)
        self.openShopBirthdaySection = self._addCommand('openShopBirthdaySection')
