# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/instructor_slot_base_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel

class InstructorSlotBaseModel(InstructorBaseModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(InstructorSlotBaseModel, self).__init__(properties=properties, commands=commands)

    def getSlotIndex(self):
        return self._getNumber(4)

    def setSlotIndex(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(InstructorSlotBaseModel, self)._initialize()
        self._addNumberProperty('slotIndex', 0)
