# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/empty_instructor_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel

class EmptyInstructorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EmptyInstructorTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def information(self):
        return self._getViewModel(0)

    def getIsLocked(self):
        return self._getBool(1)

    def setIsLocked(self, value):
        self._setBool(1, value)

    def getUnlockLevels(self):
        return self._getArray(2)

    def setUnlockLevels(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(EmptyInstructorTooltipModel, self)._initialize()
        self._addViewModelProperty('information', InstructorBaseModel())
        self._addBoolProperty('isLocked', False)
        self._addArrayProperty('unlockLevels', Array())
