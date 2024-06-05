# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/entry_point_view_model.py
from frameworks.wulf import ViewModel

class EntryPointViewModel(ViewModel):
    __slots__ = ('onClick', 'onHoverForSetTime', 'onLeaveAfterSetTime')

    def __init__(self, properties=4, commands=3):
        super(EntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getIsNew(self):
        return self._getBool(2)

    def setIsNew(self, value):
        self._setBool(2, value)

    def getIsNewTasksUnlocked(self):
        return self._getBool(3)

    def setIsNewTasksUnlocked(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(EntryPointViewModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isNewTasksUnlocked', False)
        self.onClick = self._addCommand('onClick')
        self.onHoverForSetTime = self._addCommand('onHoverForSetTime')
        self.onLeaveAfterSetTime = self._addCommand('onLeaveAfterSetTime')
