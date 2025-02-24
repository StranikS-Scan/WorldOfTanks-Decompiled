# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/optional_devices_assistant_preset_model_type.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class OptionalDevicesAssistantPresetTypeEnum(IntEnum):
    COMMON = 0
    LEGENDARY = 1


class OptionalDevicesAssistantPresetModelType(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(OptionalDevicesAssistantPresetModelType, self).__init__(properties=properties, commands=commands)

    def getMType(self):
        return OptionalDevicesAssistantPresetTypeEnum(self._getNumber(0))

    def setMType(self, value):
        self._setNumber(0, value.value)

    def _initialize(self):
        super(OptionalDevicesAssistantPresetModelType, self)._initialize()
        self._addNumberProperty('mType')
