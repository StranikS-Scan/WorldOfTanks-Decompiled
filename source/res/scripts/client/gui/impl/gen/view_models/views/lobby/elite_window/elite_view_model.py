# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/elite_window/elite_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class EliteViewModel(ViewModel):
    __slots__ = ('onGoToPostProgression', 'onClose')

    def __init__(self, properties=2, commands=2):
        super(EliteViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    def getIsPostProgressionExists(self):
        return self._getBool(1)

    def setIsPostProgressionExists(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(EliteViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addBoolProperty('isPostProgressionExists', False)
        self.onGoToPostProgression = self._addCommand('onGoToPostProgression')
        self.onClose = self._addCommand('onClose')
