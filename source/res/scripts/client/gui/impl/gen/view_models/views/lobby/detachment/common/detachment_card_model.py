# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_card_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_base_model import DetachmentBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel

class DetachmentCardModel(DetachmentBaseModel):
    __slots__ = ()

    def __init__(self, properties=38, commands=1):
        super(DetachmentCardModel, self).__init__(properties=properties, commands=commands)

    def getRecoveryTime(self):
        return self._getNumber(33)

    def setRecoveryTime(self, value):
        self._setNumber(33, value)

    def getAvailablePoints(self):
        return self._getNumber(34)

    def setAvailablePoints(self, value):
        self._setNumber(34, value)

    def getIsDismissDisable(self):
        return self._getBool(35)

    def setIsDismissDisable(self, value):
        self._setBool(35, value)

    def getState(self):
        return self._getString(36)

    def setState(self, value):
        self._setString(36, value)

    def getInstructorsList(self):
        return self._getArray(37)

    def setInstructorsList(self, value):
        self._setArray(37, value)

    def _initialize(self):
        super(DetachmentCardModel, self)._initialize()
        self._addNumberProperty('recoveryTime', 0)
        self._addNumberProperty('availablePoints', 0)
        self._addBoolProperty('isDismissDisable', False)
        self._addStringProperty('state', '')
        self._addArrayProperty('instructorsList', Array())
