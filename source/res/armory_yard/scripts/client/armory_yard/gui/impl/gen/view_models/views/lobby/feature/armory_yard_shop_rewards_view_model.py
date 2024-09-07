# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_shop_rewards_view_model.py
from frameworks.wulf import ViewModel

class ArmoryYardShopRewardsViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=4, commands=1):
        super(ArmoryYardShopRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getCount(self):
        return self._getNumber(2)

    def setCount(self, value):
        self._setNumber(2, value)

    def getItemType(self):
        return self._getString(3)

    def setItemType(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(ArmoryYardShopRewardsViewModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('count', 0)
        self._addStringProperty('itemType', '')
        self.onClose = self._addCommand('onClose')
