# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/instructor_card_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_info_model import InstructorInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel

class InstructorCardModel(InstructorInfoModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(InstructorCardModel, self).__init__(properties=properties, commands=commands)

    def getIsTokenNationsUnsuitable(self):
        return self._getBool(14)

    def setIsTokenNationsUnsuitable(self, value):
        self._setBool(14, value)

    def getAmount(self):
        return self._getNumber(15)

    def setAmount(self, value):
        self._setNumber(15, value)

    def getPerks(self):
        return self._getArray(16)

    def setPerks(self, value):
        self._setArray(16, value)

    def _initialize(self):
        super(InstructorCardModel, self)._initialize()
        self._addBoolProperty('isTokenNationsUnsuitable', False)
        self._addNumberProperty('amount', 0)
        self._addArrayProperty('perks', Array())
