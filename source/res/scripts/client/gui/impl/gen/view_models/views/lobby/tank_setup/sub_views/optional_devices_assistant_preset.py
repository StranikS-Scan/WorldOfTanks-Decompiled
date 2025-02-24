# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/optional_devices_assistant_preset.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_item import OptionalDevicesAssistantItem
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_preset_model_type import OptionalDevicesAssistantPresetModelType

class OptionalDevicesAssistantTypeEnum(IntEnum):
    NODATA = 0
    NORMAL = 1
    LINKED = 2
    COMBINED = 3


class OptionalDevicesAssistantModeTypeEnum(Enum):
    UNKNOWN = 'unknown'
    RANDOM = 'random'
    COMP7 = 'comp7'


class OptionalDevicesAssistantPreset(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(OptionalDevicesAssistantPreset, self).__init__(properties=properties, commands=commands)

    @property
    def presetType(self):
        return self._getViewModel(0)

    @staticmethod
    def getPresetTypeType():
        return OptionalDevicesAssistantPresetModelType

    def getOptionalDevicesResultType(self):
        return OptionalDevicesAssistantTypeEnum(self._getNumber(1))

    def setOptionalDevicesResultType(self, value):
        self._setNumber(1, value.value)

    def getModeType(self):
        return OptionalDevicesAssistantModeTypeEnum(self._getString(2))

    def setModeType(self, value):
        self._setString(2, value.value)

    def getSourceVehicleCompDescr(self):
        return self._getNumber(3)

    def setSourceVehicleCompDescr(self, value):
        self._setNumber(3, value)

    def getIsDataOutdated(self):
        return self._getBool(4)

    def setIsDataOutdated(self, value):
        self._setBool(4, value)

    def getOptionalDevicesAssistantItems(self):
        return self._getArray(5)

    def setOptionalDevicesAssistantItems(self, value):
        self._setArray(5, value)

    @staticmethod
    def getOptionalDevicesAssistantItemsType():
        return OptionalDevicesAssistantItem

    def _initialize(self):
        super(OptionalDevicesAssistantPreset, self)._initialize()
        self._addViewModelProperty('presetType', OptionalDevicesAssistantPresetModelType())
        self._addNumberProperty('optionalDevicesResultType')
        self._addStringProperty('modeType')
        self._addNumberProperty('sourceVehicleCompDescr', 0)
        self._addBoolProperty('isDataOutdated', False)
        self._addArrayProperty('optionalDevicesAssistantItems', Array())
