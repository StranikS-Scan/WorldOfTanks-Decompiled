# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/instructor_base_model.py
from frameworks.wulf import ViewModel

class InstructorBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(InstructorBaseModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getBackground(self):
        return self._getString(2)

    def setBackground(self, value):
        self._setString(2, value)

    def getGrade(self):
        return self._getNumber(3)

    def setGrade(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(InstructorBaseModel, self)._initialize()
        self._addNumberProperty('id', -1)
        self._addStringProperty('icon', '')
        self._addStringProperty('background', '')
        self._addNumberProperty('grade', 0)
