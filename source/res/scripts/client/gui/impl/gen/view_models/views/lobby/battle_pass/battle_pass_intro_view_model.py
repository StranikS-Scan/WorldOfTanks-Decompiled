# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_intro_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BattlePassIntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onVideo')

    def __init__(self, properties=1, commands=2):
        super(BattlePassIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getVideo(self):
        return self._getResource(0)

    def setVideo(self, value):
        self._setResource(0, value)

    def _initialize(self):
        super(BattlePassIntroViewModel, self)._initialize()
        self._addResourceProperty('video', R.invalid())
        self.onClose = self._addCommand('onClose')
        self.onVideo = self._addCommand('onVideo')
