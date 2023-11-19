# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/elite_window/elite_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class EliteViewModel(ViewModel):
    __slots__ = ('onGoToPostProgression', 'onClose')

    def __init__(self, properties=4, commands=2):
        super(EliteViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    @property
    def prestigeEmblem(self):
        return self._getViewModel(1)

    @staticmethod
    def getPrestigeEmblemType():
        return PrestigeEmblemModel

    def getIsPostProgressionExists(self):
        return self._getBool(2)

    def setIsPostProgressionExists(self, value):
        self._setBool(2, value)

    def getIsPrestigeAvailable(self):
        return self._getBool(3)

    def setIsPrestigeAvailable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(EliteViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('prestigeEmblem', PrestigeEmblemModel())
        self._addBoolProperty('isPostProgressionExists', False)
        self._addBoolProperty('isPrestigeAvailable', False)
        self.onGoToPostProgression = self._addCommand('onGoToPostProgression')
        self.onClose = self._addCommand('onClose')
