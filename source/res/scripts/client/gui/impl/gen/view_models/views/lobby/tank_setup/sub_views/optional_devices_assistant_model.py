# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/optional_devices_assistant_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_item import OptionalDevicesAssistantItem

class OptionalDevicesAssistantType(IntEnum):
    NORMAL = 0
    LINKED = 1
    NODATA = 2


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


class OptionalDevicesAssistantModel(ViewModel):
    __slots__ = ('onHintShown',)

    def __init__(self, properties=4, commands=1):
        super(OptionalDevicesAssistantModel, self).__init__(properties=properties, commands=commands)

    def getOptionalDevicesResultType(self):
        return OptionalDevicesAssistantType(self._getNumber(0))

    def setOptionalDevicesResultType(self, value):
        self._setNumber(0, value.value)

    def getSourceVehicleCompDescr(self):
        return self._getNumber(1)

    def setSourceVehicleCompDescr(self, value):
        self._setNumber(1, value)

    def getOptionalDevicesAssistantItems(self):
        return self._getArray(2)

    def setOptionalDevicesAssistantItems(self, value):
        self._setArray(2, value)

    @staticmethod
    def getOptionalDevicesAssistantItemsType():
        return OptionalDevicesAssistantItem

    def getIsHintShown(self):
        return self._getBool(3)

    def setIsHintShown(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(OptionalDevicesAssistantModel, self)._initialize()
        self._addNumberProperty('optionalDevicesResultType')
        self._addNumberProperty('sourceVehicleCompDescr', 0)
        self._addArrayProperty('optionalDevicesAssistantItems', Array())
        self._addBoolProperty('isHintShown', False)
        self.onHintShown = self._addCommand('onHintShown')
