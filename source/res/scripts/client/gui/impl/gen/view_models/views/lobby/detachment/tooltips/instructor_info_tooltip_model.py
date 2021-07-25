# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/instructor_info_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_info_model import InstructorInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel

class InstructorInfoTooltipModel(InstructorInfoModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(InstructorInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getResource(14)

    def setDescription(self, value):
        self._setResource(14, value)

    def getRequiredSlots(self):
        return self._getNumber(15)

    def setRequiredSlots(self, value):
        self._setNumber(15, value)

    def getAmount(self):
        return self._getNumber(16)

    def setAmount(self, value):
        self._setNumber(16, value)

    def getPerks(self):
        return self._getArray(17)

    def setPerks(self, value):
        self._setArray(17, value)

    def _initialize(self):
        super(InstructorInfoTooltipModel, self)._initialize()
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('requiredSlots', 0)
        self._addNumberProperty('amount', 0)
        self._addArrayProperty('perks', Array())
