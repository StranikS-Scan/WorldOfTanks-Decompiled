# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/custom_tankmen_voiceover_view_model.py
from gui.impl.gen.view_models.views.lobby.battle_pass.tankmen_voiceover_view_model import TankmenVoiceoverViewModel

class CustomTankmenVoiceoverViewModel(TankmenVoiceoverViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=2):
        super(CustomTankmenVoiceoverViewModel, self).__init__(properties=properties, commands=commands)

    def getSeasonNum(self):
        return self._getNumber(1)

    def setSeasonNum(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(CustomTankmenVoiceoverViewModel, self)._initialize()
        self._addNumberProperty('seasonNum', 0)
