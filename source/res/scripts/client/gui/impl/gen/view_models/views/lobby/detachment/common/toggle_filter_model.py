# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/toggle_filter_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.toggle_button_base_model import ToggleButtonBaseModel

class ToggleFilterModel(ToggleButtonBaseModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ToggleFilterModel, self).__init__(properties=properties, commands=commands)

    def getCounter(self):
        return self._getNumber(5)

    def setCounter(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ToggleFilterModel, self)._initialize()
        self._addNumberProperty('counter', 0)
