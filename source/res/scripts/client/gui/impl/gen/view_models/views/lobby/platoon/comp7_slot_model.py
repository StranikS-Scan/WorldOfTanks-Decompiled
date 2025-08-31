# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/comp7_slot_model.py
from gui.impl.gen.view_models.views.lobby.platoon.platoon_rank_data import PlatoonRankData
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel

class Comp7SlotModel(SlotModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(Comp7SlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def rankData(self):
        return self._getViewModel(13)

    @staticmethod
    def getRankDataType():
        return PlatoonRankData

    def getIsWaiting(self):
        return self._getBool(14)

    def setIsWaiting(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(Comp7SlotModel, self)._initialize()
        self._addViewModelProperty('rankData', PlatoonRankData())
        self._addBoolProperty('isWaiting', False)
