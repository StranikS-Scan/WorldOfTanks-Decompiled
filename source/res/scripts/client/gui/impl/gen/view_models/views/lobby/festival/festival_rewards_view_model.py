# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_rewards_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.festival.festival_items_info_view_model import FestivalItemsInfoViewModel

class FestivalRewardsViewModel(FestivalItemsInfoViewModel):
    __slots__ = ()

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(FestivalRewardsViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
