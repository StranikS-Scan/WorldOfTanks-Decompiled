# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/fun_random_maps_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_maps_map_model import FunRandomMapsMapModel
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_maps_selected_map_model import FunRandomMapsSelectedMapModel

class FunRandomMapsViewModel(ViewModel):
    __slots__ = ('onClose', 'onInfo', 'onSwitchSelected', 'onNextMap', 'onPrevMap', 'onViewSwitch')

    def __init__(self, properties=4, commands=6):
        super(FunRandomMapsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectedMapModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getSelectedMapModelType():
        return FunRandomMapsSelectedMapModel

    def getAssetsPointer(self):
        return self._getString(1)

    def setAssetsPointer(self, value):
        self._setString(1, value)

    def getIsMapSelected(self):
        return self._getBool(2)

    def setIsMapSelected(self, value):
        self._setBool(2, value)

    def getMaps(self):
        return self._getArray(3)

    def setMaps(self, value):
        self._setArray(3, value)

    @staticmethod
    def getMapsType():
        return FunRandomMapsMapModel

    def _initialize(self):
        super(FunRandomMapsViewModel, self)._initialize()
        self._addViewModelProperty('selectedMapModel', FunRandomMapsSelectedMapModel())
        self._addStringProperty('assetsPointer', '')
        self._addBoolProperty('isMapSelected', False)
        self._addArrayProperty('maps', Array())
        self.onClose = self._addCommand('onClose')
        self.onInfo = self._addCommand('onInfo')
        self.onSwitchSelected = self._addCommand('onSwitchSelected')
        self.onNextMap = self._addCommand('onNextMap')
        self.onPrevMap = self._addCommand('onPrevMap')
        self.onViewSwitch = self._addCommand('onViewSwitch')
