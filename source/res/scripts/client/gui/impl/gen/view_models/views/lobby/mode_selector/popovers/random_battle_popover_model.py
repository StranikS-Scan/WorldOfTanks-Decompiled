# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/popovers/random_battle_popover_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.mode_selector.popovers.random_battle_popover_item_model import RandomBattlePopoverItemModel

class RandomBattlePopoverModel(ViewModel):
    __slots__ = ('onItemChanged',)

    def __init__(self, properties=1, commands=1):
        super(RandomBattlePopoverModel, self).__init__(properties=properties, commands=commands)

    def getSettingsList(self):
        return self._getArray(0)

    def setSettingsList(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(RandomBattlePopoverModel, self)._initialize()
        self._addArrayProperty('settingsList', Array())
        self.onItemChanged = self._addCommand('onItemChanged')
