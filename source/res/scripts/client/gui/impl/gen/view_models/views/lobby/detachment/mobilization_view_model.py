# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/mobilization_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_with_points_model import DetachmentWithPointsModel
from gui.impl.gen.view_models.views.lobby.detachment.common.fast_operation_model import FastOperationModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel

class MobilizationViewModel(NavigationViewModel):
    __slots__ = ('onContinueClick', 'onInfoClick', 'onFlashLayoutUpdate')
    VEHICLE_DEFAULT = 'default'
    VEHICLE_IN_BATTLE = 'inBattle'
    VEHICLE_IN_PLATOON = 'inPlatoon'
    VEHICLE_LOCK_CREW = 'lockCrew'
    VEHICLE_ELITE = 'elite'
    COMPONENT_VEHICLE = 'componentVehicle'
    COMPONENT_RECRUITS = 'componentRecruits'

    def __init__(self, properties=7, commands=6):
        super(MobilizationViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentInfo(self):
        return self._getViewModel(2)

    @property
    def fastOperation(self):
        return self._getViewModel(3)

    def getState(self):
        return self._getString(4)

    def setState(self, value):
        self._setString(4, value)

    def getVehicleStatus(self):
        return self._getString(5)

    def setVehicleStatus(self, value):
        self._setString(5, value)

    def getIsMedallionEnable(self):
        return self._getBool(6)

    def setIsMedallionEnable(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(MobilizationViewModel, self)._initialize()
        self._addViewModelProperty('detachmentInfo', DetachmentWithPointsModel())
        self._addViewModelProperty('fastOperation', FastOperationModel())
        self._addStringProperty('state', '')
        self._addStringProperty('vehicleStatus', 'default')
        self._addBoolProperty('isMedallionEnable', False)
        self.onContinueClick = self._addCommand('onContinueClick')
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onFlashLayoutUpdate = self._addCommand('onFlashLayoutUpdate')
