# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/subscription/wot_plus_intro_view_model.py
from frameworks.wulf import ViewModel

class WotPlusIntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onAffirmative', 'onInfo')

    def __init__(self, properties=0, commands=3):
        super(WotPlusIntroViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WotPlusIntroViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onAffirmative = self._addCommand('onAffirmative')
        self.onInfo = self._addCommand('onInfo')
