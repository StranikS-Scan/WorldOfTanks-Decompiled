# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/welcome_screen_view_model.py
from frameworks.wulf import ViewModel

class WelcomeScreenViewModel(ViewModel):
    __slots__ = ('onVideoPlay', 'onClose', 'onViewLoaded')

    def __init__(self, properties=0, commands=3):
        super(WelcomeScreenViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WelcomeScreenViewModel, self)._initialize()
        self.onVideoPlay = self._addCommand('onVideoPlay')
        self.onClose = self._addCommand('onClose')
        self.onViewLoaded = self._addCommand('onViewLoaded')
