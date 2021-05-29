# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/map_box_intro_model.py
from frameworks.wulf import ViewModel

class MapBoxIntroModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(MapBoxIntroModel, self).__init__(properties=properties, commands=commands)

    def getSeasonNumber(self):
        return self._getNumber(0)

    def setSeasonNumber(self, value):
        self._setNumber(0, value)

    def getDate(self):
        return self._getNumber(1)

    def setDate(self, value):
        self._setNumber(1, value)

    def getIsActive(self):
        return self._getBool(2)

    def setIsActive(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(MapBoxIntroModel, self)._initialize()
        self._addNumberProperty('seasonNumber', 0)
        self._addNumberProperty('date', 0)
        self._addBoolProperty('isActive', False)
        self.onClose = self._addCommand('onClose')
