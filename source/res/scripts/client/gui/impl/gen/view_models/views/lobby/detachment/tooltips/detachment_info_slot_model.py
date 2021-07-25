# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/detachment_info_slot_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class DetachmentInfoSlotModel(ViewModel):
    __slots__ = ()
    ASSIGNED = 'assigned'
    EMPTY = 'empty'
    LOCKED = 'locked'

    def __init__(self, properties=7, commands=0):
        super(DetachmentInfoSlotModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getStatus(self):
        return self._getString(2)

    def setStatus(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def getIsCurrentVehicle(self):
        return self._getBool(4)

    def setIsCurrentVehicle(self, value):
        self._setBool(4, value)

    def getLevelReq(self):
        return self._getNumber(5)

    def setLevelReq(self, value):
        self._setNumber(5, value)

    def getGrade(self):
        return self._getNumber(6)

    def setGrade(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(DetachmentInfoSlotModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('status', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isCurrentVehicle', False)
        self._addNumberProperty('levelReq', 0)
        self._addNumberProperty('grade', 0)
