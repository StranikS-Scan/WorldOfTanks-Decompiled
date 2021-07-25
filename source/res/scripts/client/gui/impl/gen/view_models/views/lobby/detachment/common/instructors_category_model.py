# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/instructors_category_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_card_model import InstructorCardModel

class InstructorsCategoryModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(InstructorsCategoryModel, self).__init__(properties=properties, commands=commands)

    def getGrade(self):
        return self._getNumber(0)

    def setGrade(self, value):
        self._setNumber(0, value)

    def getIsEnoughSlots(self):
        return self._getBool(1)

    def setIsEnoughSlots(self, value):
        self._setBool(1, value)

    def getRequiredLevel(self):
        return self._getNumber(2)

    def setRequiredLevel(self, value):
        self._setNumber(2, value)

    def getItems(self):
        return self._getArray(3)

    def setItems(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(InstructorsCategoryModel, self)._initialize()
        self._addNumberProperty('grade', 0)
        self._addBoolProperty('isEnoughSlots', True)
        self._addNumberProperty('requiredLevel', 0)
        self._addArrayProperty('items', Array())
