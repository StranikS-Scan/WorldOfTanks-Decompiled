# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/slot_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SlotState(Enum):
    FILL = 'fill'
    READY = 'ready'
    AVAILABLE = 'available'
    LOCKED = 'locked'


class SlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(SlotModel, self).__init__(properties=properties, commands=commands)

    def getDayId(self):
        return self._getNumber(0)

    def setDayId(self, value):
        self._setNumber(0, value)

    def getLabel(self):
        return self._getString(1)

    def setLabel(self, value):
        self._setString(1, value)

    def getState(self):
        return SlotState(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def getOpenTimestamp(self):
        return self._getNumber(3)

    def setOpenTimestamp(self, value):
        self._setNumber(3, value)

    def getSpecial(self):
        return self._getBool(4)

    def setSpecial(self, value):
        self._setBool(4, value)

    def getInitialAnimationRequired(self):
        return self._getBool(5)

    def setInitialAnimationRequired(self, value):
        self._setBool(5, value)

    def getVideo(self):
        return self._getString(6)

    def setVideo(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addNumberProperty('dayId', 0)
        self._addStringProperty('label', '')
        self._addStringProperty('state')
        self._addNumberProperty('openTimestamp', 0)
        self._addBoolProperty('special', False)
        self._addBoolProperty('initialAnimationRequired', False)
        self._addStringProperty('video', '')
