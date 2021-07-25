# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/barrack_instructors_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.instructors_view_base_model import InstructorsViewBaseModel

class BarrackInstructorsViewModel(InstructorsViewBaseModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=6):
        super(BarrackInstructorsViewModel, self).__init__(properties=properties, commands=commands)

    def getIsRecruitsTabEnabled(self):
        return self._getBool(9)

    def setIsRecruitsTabEnabled(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(BarrackInstructorsViewModel, self)._initialize()
        self._addBoolProperty('isRecruitsTabEnabled', False)
