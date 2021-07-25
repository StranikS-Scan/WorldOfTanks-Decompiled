# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructors_and_skins_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class InstructorsAndSkinsModel(ViewModel):
    __slots__ = ()
    STATUS_CHECK = 'check'
    STATUS_WARNING = 'warning'

    def __init__(self, properties=4, commands=0):
        super(InstructorsAndSkinsModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIsInstructor(self):
        return self._getBool(1)

    def setIsInstructor(self, value):
        self._setBool(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getStatus(self):
        return self._getString(3)

    def setStatus(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(InstructorsAndSkinsModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addBoolProperty('isInstructor', False)
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('status', '')
