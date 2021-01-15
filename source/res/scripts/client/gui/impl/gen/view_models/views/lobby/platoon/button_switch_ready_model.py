# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/button_switch_ready_model.py
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel

class ButtonSwitchReadyModel(ButtonModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=1):
        super(ButtonSwitchReadyModel, self).__init__(properties=properties, commands=commands)

    def getIsRed(self):
        return self._getBool(4)

    def setIsRed(self, value):
        self._setBool(4, value)

    def getTooltipHeader(self):
        return self._getString(5)

    def setTooltipHeader(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(ButtonSwitchReadyModel, self)._initialize()
        self._addBoolProperty('isRed', False)
        self._addStringProperty('tooltipHeader', '')
