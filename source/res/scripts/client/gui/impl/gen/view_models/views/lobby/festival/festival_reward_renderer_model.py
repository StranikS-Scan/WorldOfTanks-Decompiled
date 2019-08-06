# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_reward_renderer_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.ui_kit.base_reward_renderer_model import BaseRewardRendererModel

class FestivalRewardRendererModel(BaseRewardRendererModel):
    __slots__ = ()

    def getIcons(self):
        return self._getArray(7)

    def setIcons(self, value):
        self._setArray(7, value)

    def getItemName(self):
        return self._getString(8)

    def setItemName(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(FestivalRewardRendererModel, self)._initialize()
        self._addArrayProperty('icons', Array())
        self._addStringProperty('itemName', '')
