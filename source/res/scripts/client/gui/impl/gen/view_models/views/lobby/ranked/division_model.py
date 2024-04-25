# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/division_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.ranked.rank_model import RankModel

class DivisionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(DivisionModel, self).__init__(properties=properties, commands=commands)

    @property
    def ranks(self):
        return self._getViewModel(0)

    @staticmethod
    def getRanksType():
        return RankModel

    def getDivisionID(self):
        return self._getNumber(1)

    def setDivisionID(self, value):
        self._setNumber(1, value)

    def getVehicleLevel(self):
        return self._getNumber(2)

    def setVehicleLevel(self, value):
        self._setNumber(2, value)

    def getFirstRank(self):
        return self._getNumber(3)

    def setFirstRank(self, value):
        self._setNumber(3, value)

    def getLastRank(self):
        return self._getNumber(4)

    def setLastRank(self, value):
        self._setNumber(4, value)

    def getIsSingleReward(self):
        return self._getBool(5)

    def setIsSingleReward(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(DivisionModel, self)._initialize()
        self._addViewModelProperty('ranks', UserListModel())
        self._addNumberProperty('divisionID', 0)
        self._addNumberProperty('vehicleLevel', 0)
        self._addNumberProperty('firstRank', 0)
        self._addNumberProperty('lastRank', 0)
        self._addBoolProperty('isSingleReward', True)
