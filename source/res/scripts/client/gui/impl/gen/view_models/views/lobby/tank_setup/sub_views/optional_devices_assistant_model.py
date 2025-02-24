# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/optional_devices_assistant_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_preset import OptionalDevicesAssistantPreset
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_preset_model_type import OptionalDevicesAssistantPresetModelType

class OptionalDevicesAssistantItemType(Enum):
    STEREOSCOPE = 'stereoscope'
    TURBOCHARGER = 'turbocharger'
    ENHANCEDAIMDRIVES = 'enhancedAimDrives'
    COMMANDERSVIEW = 'commandersView'
    GROUSERS = 'grousers'
    ADDITINVISIBILITYDEVICE = 'additInvisibilityDevice'
    RADIOCOMMUNICATION = 'radioCommunication'
    ANTIFRAGMENTATIONLINING = 'antifragmentationLining'
    CAMOUFLAGENET = 'camouflageNet'
    ROTATIONMECHANISM = 'rotationMechanism'
    VENTILATION = 'ventilation'
    HEALTHRESERVE = 'healthReserve'
    IMPROVEDSIGHTS = 'improvedSights'
    RAMMER = 'rammer'
    COATEDOPTICS = 'coatedOptics'
    AIMINGSTABILIZER = 'aimingStabilizer'
    IMPROVEDCONFIGURATION = 'improvedConfiguration'
    MODERNIZEDEXTRAHEALTHRESERVEANTIFRAGMENTATIONLINING = 'modernizedExtraHealthReserveAntifragmentationLining'
    MODERNIZEDTURBOCHARGERROTATIONMECHANISM = 'modernizedTurbochargerRotationMechanism'
    MODERNIZEDAIMDRIVESAIMINGSTABILIZER = 'modernizedAimDrivesAimingStabilizer'
    MODERNIZEDIMPROVEDSIGHTSENHANCEDAIMDRIVES = 'modernizedImprovedSightsEnhancedAimDrives'


class OptionalDevicesAssistantStateEnum(Enum):
    VISIBLE = 'visible'
    HIDDEN = 'hidden'
    NOTSUITABLEVEHICLE = 'notSuitableVehicle'
    NODATAATALL = 'noDataAtAll'


class OptionalDevicesAssistantModel(ViewModel):
    __slots__ = ('onHintShown', 'onPresetSelected')

    def __init__(self, properties=4, commands=2):
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

    def getIsHintShown(self):
        return self._getBool(2)

    def setIsHintShown(self, value):
        self._setBool(2, value)

    def getState(self):
        return OptionalDevicesAssistantStateEnum(self._getString(3))

    def setState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(OptionalDevicesAssistantModel, self)._initialize()
        self._addViewModelProperty('selectedPreset', OptionalDevicesAssistantPresetModelType())
        self._addArrayProperty('optionalDevicesAssistantPresets', Array())
        self._addBoolProperty('isHintShown', False)
        self._addStringProperty('state', OptionalDevicesAssistantStateEnum.HIDDEN.value)
        self.onHintShown = self._addCommand('onHintShown')
        self.onPresetSelected = self._addCommand('onPresetSelected')
