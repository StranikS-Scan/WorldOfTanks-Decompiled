# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/main_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.missions_state_model import MissionsStateModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.new_operation_banner import NewOperationBanner
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_model import OperationModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_status_model import OperationStatusModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.select_operation_model import SelectOperationModel

class MainScreenState(Enum):
    ASSEMBLING = 'assembling'
    MISSIONS = 'missions'
    PROGRESSION = 'progression'


class AnimationState(Enum):
    IDLE = 'idle'
    ANIMATION_STARTED = 'animationStarted'
    ASSEMBLING = 'assembling'
    CONTINUE_DETAIL_INFO = 'continueDetailInfo'
    CONTINUE_CLAIM_DETAIL = 'continueClaimDetail'
    CONTINUE_BACK = 'continueBack'


class MainViewModel(ViewModel):
    __slots__ = ('onBack', 'onSwitchOperation', 'showOperationVehicleVideo', 'onOperationStatusButtonClick', 'onDetailInfo', 'onClaimDetail', 'onMission', 'onAdditionalMission', 'onVehiclePreview', 'showVehicleInHangar', 'showDetailVideo', 'onMoveSpace', 'onMouseOver3dScene', 'showStylePreview', 'setFreeCamera', 'updateAnimationState')
    OPERATION_ID = 'operationId'
    DETAIL_ID = 'detailId'
    ANIMATION_STATE = 'animationState'

    def __init__(self, properties=11, commands=16):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleInfoModel

    @property
    def status(self):
        return self._getViewModel(1)

    @staticmethod
    def getStatusType():
        return OperationStatusModel

    @property
    def missionsModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getMissionsModelType():
        return MissionsStateModel

    @property
    def banner(self):
        return self._getViewModel(3)

    @staticmethod
    def getBannerType():
        return NewOperationBanner

    def getActiveOperationId(self):
        return self._getNumber(4)

    def setActiveOperationId(self, value):
        self._setNumber(4, value)

    def getAnimationState(self):
        return AnimationState(self._getString(5))

    def setAnimationState(self, value):
        self._setString(5, value.value)

    def getCampaignName(self):
        return self._getString(6)

    def setCampaignName(self, value):
        self._setString(6, value)

    def getMenuItems(self):
        return self._getArray(7)

    def setMenuItems(self, value):
        self._setArray(7, value)

    @staticmethod
    def getMenuItemsType():
        return SelectOperationModel

    def getOperations(self):
        return self._getArray(8)

    def setOperations(self, value):
        self._setArray(8, value)

    @staticmethod
    def getOperationsType():
        return OperationModel

    def getMainScreenState(self):
        return MainScreenState(self._getString(9))

    def setMainScreenState(self, value):
        self._setString(9, value.value)

    def getCameraFlightInProgress(self):
        return self._getBool(10)

    def setCameraFlightInProgress(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleInfoModel())
        self._addViewModelProperty('status', OperationStatusModel())
        self._addViewModelProperty('missionsModel', MissionsStateModel())
        self._addViewModelProperty('banner', NewOperationBanner())
        self._addNumberProperty('activeOperationId', 0)
        self._addStringProperty('animationState', AnimationState.IDLE.value)
        self._addStringProperty('campaignName', '')
        self._addArrayProperty('menuItems', Array())
        self._addArrayProperty('operations', Array())
        self._addStringProperty('mainScreenState')
        self._addBoolProperty('cameraFlightInProgress', False)
        self.onBack = self._addCommand('onBack')
        self.onSwitchOperation = self._addCommand('onSwitchOperation')
        self.showOperationVehicleVideo = self._addCommand('showOperationVehicleVideo')
        self.onOperationStatusButtonClick = self._addCommand('onOperationStatusButtonClick')
        self.onDetailInfo = self._addCommand('onDetailInfo')
        self.onClaimDetail = self._addCommand('onClaimDetail')
        self.onMission = self._addCommand('onMission')
        self.onAdditionalMission = self._addCommand('onAdditionalMission')
        self.onVehiclePreview = self._addCommand('onVehiclePreview')
        self.showVehicleInHangar = self._addCommand('showVehicleInHangar')
        self.showDetailVideo = self._addCommand('showDetailVideo')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.showStylePreview = self._addCommand('showStylePreview')
        self.setFreeCamera = self._addCommand('setFreeCamera')
        self.updateAnimationState = self._addCommand('updateAnimationState')
