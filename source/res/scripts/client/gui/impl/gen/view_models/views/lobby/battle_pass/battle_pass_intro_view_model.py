# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_intro_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.base_intro_view_model import BaseIntroViewModel

class BattlePassIntroViewModel(BaseIntroViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=3):
        super(BattlePassIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getBackground(self):
        return self._getResource(4)

    def setBackground(self, value):
        self._setResource(4, value)

    def _initialize(self):
        super(BattlePassIntroViewModel, self)._initialize()
        self._addResourceProperty('background', R.invalid())
