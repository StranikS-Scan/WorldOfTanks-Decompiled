# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/custom_sound_button_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel

class CustomSoundButtonModel(ButtonModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=1):
        super(CustomSoundButtonModel, self).__init__(properties=properties, commands=commands)

    def getSoundClickName(self):
        return self._getResource(6)

    def setSoundClickName(self, value):
        self._setResource(6, value)

    def _initialize(self):
        super(CustomSoundButtonModel, self)._initialize()
        self._addResourceProperty('soundClickName', R.invalid())
