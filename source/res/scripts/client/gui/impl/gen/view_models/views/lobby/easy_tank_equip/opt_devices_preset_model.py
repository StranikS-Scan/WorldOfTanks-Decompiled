# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/opt_devices_preset_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.preset_model import PresetModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.opt_devices_preset_slot_model import OptDevicesPresetSlotModel

class OptDevicesPresetType(Enum):
    STANDARD = 'standard'
    ADVANCED = 'advanced'


class OptDevicesPresetModel(PresetModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(OptDevicesPresetModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return OptDevicesPresetType(self._getString(5))

    def setType(self, value):
        self._setString(5, value.value)

    def getItems(self):
        return self._getArray(6)

    def setItems(self, value):
        self._setArray(6, value)

    @staticmethod
    def getItemsType():
        return OptDevicesPresetSlotModel

    def getDemountKitsCount(self):
        return self._getNumber(7)

    def setDemountKitsCount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(OptDevicesPresetModel, self)._initialize()
        self._addStringProperty('type')
        self._addArrayProperty('items', Array())
        self._addNumberProperty('demountKitsCount', 0)
