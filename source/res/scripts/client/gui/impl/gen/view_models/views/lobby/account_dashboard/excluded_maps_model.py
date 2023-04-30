# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/excluded_maps_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.account_dashboard.map_model import MapModel

class ExcludedMapsModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(ExcludedMapsModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getIsWotPlusEnabled(self):
        return self._getBool(1)

    def setIsWotPlusEnabled(self, value):
        self._setBool(1, value)

    def getExcludedMaps(self):
        return self._getArray(2)

    def setExcludedMaps(self, value):
        self._setArray(2, value)

    @staticmethod
    def getExcludedMapsType():
        return MapModel

    def _initialize(self):
        super(ExcludedMapsModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isWotPlusEnabled', False)
        self._addArrayProperty('excludedMaps', Array())
        self.onClick = self._addCommand('onClick')
