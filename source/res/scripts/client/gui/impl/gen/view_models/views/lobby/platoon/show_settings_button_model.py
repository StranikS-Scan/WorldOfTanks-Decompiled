# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/show_settings_button_model.py
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel

class ShowSettingsButtonModel(ButtonModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=1):
        super(ShowSettingsButtonModel, self).__init__(properties=properties, commands=commands)

    def getIsVisible(self):
        return self._getBool(3)

    def setIsVisible(self, value):
        self._setBool(3, value)

    def getIsPressed(self):
        return self._getBool(4)

    def setIsPressed(self, value):
        self._setBool(4, value)

    def getShouldShowPopover(self):
        return self._getBool(5)

    def setShouldShowPopover(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ShowSettingsButtonModel, self)._initialize()
        self._addBoolProperty('isVisible', False)
        self._addBoolProperty('isPressed', False)
        self._addBoolProperty('shouldShowPopover', False)
