# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/detachment_info_instructor_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel

class DetachmentInfoInstructorModel(InstructorBaseModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(DetachmentInfoInstructorModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(4)

    def setName(self, value):
        self._setString(4, value)

    def getLevelReq(self):
        return self._getNumber(5)

    def setLevelReq(self, value):
        self._setNumber(5, value)

    def getStatus(self):
        return self._getString(6)

    def setStatus(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(DetachmentInfoInstructorModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('levelReq', 0)
        self._addStringProperty('status', '')
