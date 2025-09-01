# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/vehicles_sidebar/vehicles_sidebar_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.customization.vehicles_sidebar.vehicles_sidebar_item_model import VehiclesSidebarItemModel

class VehiclesSidebarModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=1, commands=1):
        super(VehiclesSidebarModel, self).__init__(properties=properties, commands=commands)

    def getVehiclesSelection(self):
        return self._getArray(0)

    def setVehiclesSelection(self, value):
        self._setArray(0, value)

    @staticmethod
    def getVehiclesSelectionType():
        return VehiclesSidebarItemModel

    def _initialize(self):
        super(VehiclesSidebarModel, self)._initialize()
        self._addArrayProperty('vehiclesSelection', Array())
        self.onClose = self._addCommand('onClose')
