# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/welcome_screen_view_model.py
from frameworks.wulf import ViewModel

class WelcomeScreenViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(WelcomeScreenViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WelcomeScreenViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
