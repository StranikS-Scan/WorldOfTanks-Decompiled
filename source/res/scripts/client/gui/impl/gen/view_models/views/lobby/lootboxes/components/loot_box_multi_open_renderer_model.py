# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/components/loot_box_multi_open_renderer_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootBoxMultiOpenRendererModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(LootBoxMultiOpenRendererModel, self).__init__(properties=properties, commands=commands)

    def getIndx(self):
        return self._getNumber(0)

    def setIndx(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(LootBoxMultiOpenRendererModel, self)._initialize()
        self._addNumberProperty('indx', 0)
        self._addArrayProperty('rewards', Array())
