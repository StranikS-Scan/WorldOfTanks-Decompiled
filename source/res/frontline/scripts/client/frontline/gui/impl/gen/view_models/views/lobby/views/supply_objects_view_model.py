# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/supply_objects_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.supply_objects_model import SupplyObjectsModel
from frontline.gui.impl.gen.view_models.views.lobby.views.supply_params_model import SupplyParamsModel

class SupplyObjectsViewModel(ViewModel):
    __slots__ = ('onSupplySelected', 'onClose')

    def __init__(self, properties=6, commands=2):
        super(SupplyObjectsViewModel, self).__init__(properties=properties, commands=commands)

    def getIsFullScreen(self):
        return self._getBool(0)

    def setIsFullScreen(self, value):
        self._setBool(0, value)

    def getSupplyTeam(self):
        return self._getNumber(1)

    def setSupplyTeam(self, value):
        self._setNumber(1, value)

    def getSupplyHullDamageFactor(self):
        return self._getReal(2)

    def setSupplyHullDamageFactor(self, value):
        self._setReal(2, value)

    def getSupplyTurretDamageFactor(self):
        return self._getReal(3)

    def setSupplyTurretDamageFactor(self, value):
        self._setReal(3, value)

    def getSupplyObjects(self):
        return self._getArray(4)

    def setSupplyObjects(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSupplyObjectsType():
        return SupplyObjectsModel

    def getSupplyParams(self):
        return self._getArray(5)

    def setSupplyParams(self, value):
        self._setArray(5, value)

    @staticmethod
    def getSupplyParamsType():
        return SupplyParamsModel

    def _initialize(self):
        super(SupplyObjectsViewModel, self)._initialize()
        self._addBoolProperty('isFullScreen', False)
        self._addNumberProperty('supplyTeam', 0)
        self._addRealProperty('supplyHullDamageFactor', 0.0)
        self._addRealProperty('supplyTurretDamageFactor', 0.0)
        self._addArrayProperty('supplyObjects', Array())
        self._addArrayProperty('supplyParams', Array())
        self.onSupplySelected = self._addCommand('onSupplySelected')
        self.onClose = self._addCommand('onClose')
