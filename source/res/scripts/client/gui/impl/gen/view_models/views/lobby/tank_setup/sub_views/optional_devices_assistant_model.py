# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/optional_devices_assistant_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_preset import OptionalDevicesAssistantPreset
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_preset_model_type import OptionalDevicesAssistantPresetModelType

class OptionalDevicesAssistantItemType(Enum):
    STEREOSCOPE = 'stereoscope'
    TURBOCHARGER = 'turbocharger'
    ENHANCEDAIMDRIVES = 'enhancedAimDrives'
    COMMANDERSVIEW = 'commandersView'
    GROUSERS = 'grousers'
    ADDITINVISIBILITYDEVICE = 'additionalInvisibilityDevice'
    RADIOCOMMUNICATION = 'improvedRadioCommunication'
    ANTIFRAGMENTATIONLINING = 'antifragmentationLining'
    CAMOUFLAGENET = 'camouflageNet'
    ROTATIONMECHANISM = 'improvedRotationMechanism'
    VENTILATION = 'improvedVentilation'
    HEALTHRESERVE = 'extraHealthReserve'
    IMPROVEDSIGHTS = 'improvedSights'
    RAMMER = 'tankRammer'
    COATEDOPTICS = 'coatedOptics'
    AIMINGSTABILIZER = 'aimingStabilizer'
    IMPROVEDCONFIGURATION = 'improvedConfiguration'
    MODERNIZEDEXTRAHEALTHRESERVEANTIFRAGMENTATIONLINING = 'modernizedExtraHealthReserveAntifragmentationLining'
    MODERNIZEDTURBOCHARGERROTATIONMECHANISM = 'modernizedTurbochargerRotationMechanism'
    MODERNIZEDAIMDRIVESAIMINGSTABILIZER = 'modernizedAimDrivesAimingStabilizer'
    MODERNIZEDIMPROVEDSIGHTSENHANCEDAIMDRIVES = 'modernizedImprovedSightsEnhancedAimDrives'
    EMPTY = ''


class OptionalDevicesAssistantStateEnum(Enum):
    VISIBLE = 'visible'
    HIDDEN = 'hidden'
    NOTSUITABLEVEHICLE = 'notSuitableVehicle'
    NODATAATALL = 'noDataAtAll'


class OptionalDevicesAssistantModel(ViewModel):
    __slots__ = ('onPresetSelected',)

    def __init__(self, properties=3, commands=1):
        super(OptionalDevicesAssistantModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectedPreset(self):
        return self._getViewModel(0)

    @staticmethod
    def getSelectedPresetType():
        return OptionalDevicesAssistantPresetModelType

    def getOptionalDevicesAssistantPresets(self):
        return self._getArray(1)

    def setOptionalDevicesAssistantPresets(self, value):
        self._setArray(1, value)

    @staticmethod
    def getOptionalDevicesAssistantPresetsType():
        return OptionalDevicesAssistantPreset

    def getState(self):
        return OptionalDevicesAssistantStateEnum(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(OptionalDevicesAssistantModel, self)._initialize()
        self._addViewModelProperty('selectedPreset', OptionalDevicesAssistantPresetModelType())
        self._addArrayProperty('optionalDevicesAssistantPresets', Array())
        self._addStringProperty('state', OptionalDevicesAssistantStateEnum.HIDDEN.value)
        self.onPresetSelected = self._addCommand('onPresetSelected')
