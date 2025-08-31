# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/ranked_slot_model.py
from gui.impl.gen.view_models.views.lobby.platoon.ranked_platoon_rank_data import RankedPlatoonRankData
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel

class RankedSlotModel(SlotModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(RankedSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def rankData(self):
        return self._getViewModel(13)

    @staticmethod
    def getRankDataType():
        return RankedPlatoonRankData

    def getIsWaiting(self):
        return self._getBool(14)

    def setIsWaiting(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(RankedSlotModel, self)._initialize()
        self._addViewModelProperty('rankData', RankedPlatoonRankData())
        self._addBoolProperty('isWaiting', False)
