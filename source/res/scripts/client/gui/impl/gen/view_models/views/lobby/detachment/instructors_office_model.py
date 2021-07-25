# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructors_office_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel

class InstructorsOfficeModel(NavigationViewModel):
    __slots__ = ('onMoveInstructorClick', 'onHireInstructorClick')

    def __init__(self, properties=8, commands=5):
        super(InstructorsOfficeModel, self).__init__(properties=properties, commands=commands)

    def getInstructors(self):
        return self._getArray(2)

    def setInstructors(self, value):
        self._setArray(2, value)

    def getHasDog(self):
        return self._getBool(3)

    def setHasDog(self, value):
        self._setBool(3, value)

    def getCanHire(self):
        return self._getBool(4)

    def setCanHire(self, value):
        self._setBool(4, value)

    def getBackground(self):
        return self._getResource(5)

    def setBackground(self, value):
        self._setResource(5, value)

    def getDogTooltipHeader(self):
        return self._getResource(6)

    def setDogTooltipHeader(self, value):
        self._setResource(6, value)

    def getDogTooltipDescription(self):
        return self._getResource(7)

    def setDogTooltipDescription(self, value):
        self._setResource(7, value)

    def _initialize(self):
        super(InstructorsOfficeModel, self)._initialize()
        self._addArrayProperty('instructors', Array())
        self._addBoolProperty('hasDog', False)
        self._addBoolProperty('canHire', False)
        self._addResourceProperty('background', R.invalid())
        self._addResourceProperty('dogTooltipHeader', R.invalid())
        self._addResourceProperty('dogTooltipDescription', R.invalid())
        self.onMoveInstructorClick = self._addCommand('onMoveInstructorClick')
        self.onHireInstructorClick = self._addCommand('onHireInstructorClick')
