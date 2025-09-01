# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/elite_window/elite_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class WindowType(Enum):
    STANDARD = 'standard'
    POST_PROGRESSION = 'postProgression'
    VEH_SKILL_TREE = 'vehSkillTree'


class EliteViewModel(ViewModel):
    __slots__ = ('onGoToProgression', 'onClose')

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

    def getType(self):
        return WindowType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getIsPrestigeAvailable(self):
        return self._getBool(3)

    def setIsPrestigeAvailable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(EliteViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('prestigeEmblem', PrestigeEmblemModel())
        self._addStringProperty('type')
        self._addBoolProperty('isPrestigeAvailable', False)
        self.onGoToProgression = self._addCommand('onGoToProgression')
        self.onClose = self._addCommand('onClose')
