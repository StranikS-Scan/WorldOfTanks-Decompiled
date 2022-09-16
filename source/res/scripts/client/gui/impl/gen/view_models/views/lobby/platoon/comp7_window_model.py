# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/comp7_window_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.platoon.comp7_header_model import Comp7HeaderModel
from gui.impl.gen.view_models.views.lobby.platoon.comp7_slot_model import Comp7SlotModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel

class Comp7WindowModel(MembersWindowModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=3):
        super(Comp7WindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def header(self):
        return self._getViewModel(17)

    @staticmethod
    def getHeaderType():
        return Comp7HeaderModel

    def getSlots(self):
        return self._getArray(18)

    def setSlots(self, value):
        self._setArray(18, value)

    @staticmethod
    def getSlotsType():
        return Comp7SlotModel

    def _initialize(self):
        super(Comp7WindowModel, self)._initialize()
        self._addViewModelProperty('header', Comp7HeaderModel())
        self._addArrayProperty('slots', Array())
