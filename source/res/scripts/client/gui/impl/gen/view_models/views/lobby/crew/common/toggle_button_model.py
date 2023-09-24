# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/toggle_button_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.crew.common.button_model import ButtonModel

class ToggleState(Enum):
    ON = 'on'
    OFF = 'off'
    DISABLED = 'disabled'
    HIDDEN = 'hidden'


class ToggleButtonModel(ButtonModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ToggleButtonModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return ToggleState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ToggleButtonModel, self)._initialize()
        self._addStringProperty('state')
        self._addBoolProperty('isDisabled', False)
