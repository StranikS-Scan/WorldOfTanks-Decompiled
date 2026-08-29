# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/prebattle_highlights/prebattle_highlights_marker_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class PrebattleHighlightsMarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(PrebattleHighlightsMarkerModel, self).__init__(properties=properties, commands=commands)

    @property
    def userName(self):
        return self._getViewModel(0)

    @staticmethod
    def getUserNameType():
        return UserNameModel

    @property
    def vehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    @property
    def prestigeEmblem(self):
        return self._getViewModel(2)

    @staticmethod
    def getPrestigeEmblemType():
        return PrestigeEmblemModel

    def getPersonal(self):
        return self._getBool(3)

    def setPersonal(self, value):
        self._setBool(3, value)

    def getPosx(self):
        return self._getReal(4)

    def setPosx(self, value):
        self._setReal(4, value)

    def getPosy(self):
        return self._getReal(5)

    def setPosy(self, value):
        self._setReal(5, value)

    def getSquadIndex(self):
        return self._getNumber(6)

    def setSquadIndex(self, value):
        self._setNumber(6, value)

    def getVehId(self):
        return self._getNumber(7)

    def setVehId(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(PrebattleHighlightsMarkerModel, self)._initialize()
        self._addViewModelProperty('userName', UserNameModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addViewModelProperty('prestigeEmblem', PrestigeEmblemModel())
        self._addBoolProperty('personal', False)
        self._addRealProperty('posx', 0.0)
        self._addRealProperty('posy', 0.0)
        self._addNumberProperty('squadIndex', 0)
        self._addNumberProperty('vehId', 0)
