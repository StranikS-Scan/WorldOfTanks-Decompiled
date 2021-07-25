# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_with_points_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_slot_base_model import InstructorSlotBaseModel

class DetachmentWithPointsModel(DetachmentShortInfoModel):
    __slots__ = ()

    def __init__(self, properties=34, commands=1):
        super(DetachmentWithPointsModel, self).__init__(properties=properties, commands=commands)

    def getAvailablePoints(self):
        return self._getNumber(31)

    def setAvailablePoints(self, value):
        self._setNumber(31, value)

    def getEmptyInstructorSlots(self):
        return self._getNumber(32)

    def setEmptyInstructorSlots(self, value):
        self._setNumber(32, value)

    def getInstructorsList(self):
        return self._getArray(33)

    def setInstructorsList(self, value):
        self._setArray(33, value)

    def _initialize(self):
        super(DetachmentWithPointsModel, self)._initialize()
        self._addNumberProperty('availablePoints', 0)
        self._addNumberProperty('emptyInstructorSlots', 0)
        self._addArrayProperty('instructorsList', Array())
