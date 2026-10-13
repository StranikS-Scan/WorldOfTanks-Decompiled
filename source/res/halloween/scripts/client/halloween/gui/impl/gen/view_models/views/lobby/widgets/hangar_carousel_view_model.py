# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/widgets/hangar_carousel_view_model.py
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_vehicle_view_model import HangarCarouselVehicleViewModel

class HangarCarouselViewModel(ViewModel):
    __slots__ = ('onChangeVehicle', 'onVehiclePreview', 'onChangeSize')

    def __init__(self, properties=2, commands=3):
        super(HangarCarouselViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedVehicle(self):
        return self._getNumber(0)

    def setSelectedVehicle(self, value):
        self._setNumber(0, value)

    def getVehicles(self):
        return self._getArray(1)

    def setVehicles(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehiclesType():
        return HangarCarouselVehicleViewModel

    def _initialize(self):
        super(HangarCarouselViewModel, self)._initialize()
        self._addNumberProperty('selectedVehicle', 0)
        self._addArrayProperty('vehicles', Array())
        self.onChangeVehicle = self._addCommand('onChangeVehicle')
        self.onVehiclePreview = self._addCommand('onVehiclePreview')
        self.onChangeSize = self._addCommand('onChangeSize')
