# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/map_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SlotStateEnum(Enum):
    EMPTY = 'empty'
    SELECTED = 'selected'
    DISABLED = 'disabled'


class MapModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(MapModel, self).__init__(properties=properties, commands=commands)

    def getCooldownEndTimeInSecs(self):
        return self._getNumber(0)

    def setCooldownEndTimeInSecs(self, value):
        self._setNumber(0, value)

    def getMapId(self):
        return self._getString(1)

    def setMapId(self, value):
        self._setString(1, value)

    def getSlotState(self):
        return SlotStateEnum(self._getString(2))

    def setSlotState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(MapModel, self)._initialize()
        self._addNumberProperty('cooldownEndTimeInSecs', 0)
        self._addStringProperty('mapId', '')
        self._addStringProperty('slotState')
