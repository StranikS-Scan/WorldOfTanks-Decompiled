# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/platoon/comp7_light_window_model.py
from frameworks.wulf import Array
from comp7_light.gui.impl.gen.view_models.views.lobby.platoon.comp7_light_header_model import Comp7LightHeaderModel
from comp7_light.gui.impl.gen.view_models.views.lobby.platoon.comp7_light_slot_model import Comp7LightSlotModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel

class Comp7LightWindowModel(MembersWindowModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=3):
        super(Comp7LightWindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def header(self):
        return self._getViewModel(17)

    @staticmethod
    def getHeaderType():
        return Comp7LightHeaderModel

    def getSlots(self):
        return self._getArray(18)

    def setSlots(self, value):
        self._setArray(18, value)

    @staticmethod
    def getSlotsType():
        return Comp7LightSlotModel

    def _initialize(self):
        super(Comp7LightWindowModel, self)._initialize()
        self._addViewModelProperty('header', Comp7LightHeaderModel())
        self._addArrayProperty('slots', Array())
