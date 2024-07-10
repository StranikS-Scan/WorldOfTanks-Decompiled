# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_tier_list_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_lootbox import FunRandomLootbox

class FunRandomTierListViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(FunRandomTierListViewModel, self).__init__(properties=properties, commands=commands)

    def getLootBoxes(self):
        return self._getArray(0)

    def setLootBoxes(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLootBoxesType():
        return FunRandomLootbox

    def getAssetsPointer(self):
        return self._getString(1)

    def setAssetsPointer(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(FunRandomTierListViewModel, self)._initialize()
        self._addArrayProperty('lootBoxes', Array())
        self._addStringProperty('assetsPointer', 'undefined')
        self.onClose = self._addCommand('onClose')
