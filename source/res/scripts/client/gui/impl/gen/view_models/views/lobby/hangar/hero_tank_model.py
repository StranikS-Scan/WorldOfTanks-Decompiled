# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/hero_tank_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.hangar.marker_position_model import MarkerPositionModel

class HeroTankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HeroTankModel, self).__init__(properties=properties, commands=commands)

    @property
    def heroTankMarker(self):
        return self._getViewModel(0)

    @staticmethod
    def getHeroTankMarkerType():
        return MarkerPositionModel

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(HeroTankModel, self)._initialize()
        self._addViewModelProperty('heroTankMarker', MarkerPositionModel())
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
