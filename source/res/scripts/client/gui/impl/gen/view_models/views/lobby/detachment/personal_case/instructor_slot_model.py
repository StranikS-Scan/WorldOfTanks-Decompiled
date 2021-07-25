# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/personal_case/instructor_slot_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_card_model import InstructorCardModel

class InstructorSlotModel(InstructorCardModel):
    __slots__ = ()
    ASSIGNED = 'assigned'
    EMPTY = 'empty'
    LOCKED = 'locked'

    def __init__(self, properties=24, commands=0):
        super(InstructorSlotModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return self._getString(17)

    def setStatus(self, value):
        self._setString(17, value)

    def getIsVoiceActive(self):
        return self._getBool(18)

    def setIsVoiceActive(self, value):
        self._setBool(18, value)

    def getIsAnimationActive(self):
        return self._getBool(19)

    def setIsAnimationActive(self, value):
        self._setBool(19, value)

    def getIsDisabled(self):
        return self._getBool(20)

    def setIsDisabled(self, value):
        self._setBool(20, value)

    def getLevelReq(self):
        return self._getNumber(21)

    def setLevelReq(self, value):
        self._setNumber(21, value)

    def getSlotsCount(self):
        return self._getNumber(22)

    def setSlotsCount(self, value):
        self._setNumber(22, value)

    def getSlotIndex(self):
        return self._getNumber(23)

    def setSlotIndex(self, value):
        self._setNumber(23, value)

    def _initialize(self):
        super(InstructorSlotModel, self)._initialize()
        self._addStringProperty('status', '')
        self._addBoolProperty('isVoiceActive', False)
        self._addBoolProperty('isAnimationActive', False)
        self._addBoolProperty('isDisabled', False)
        self._addNumberProperty('levelReq', 0)
        self._addNumberProperty('slotsCount', 0)
        self._addNumberProperty('slotIndex', 0)
