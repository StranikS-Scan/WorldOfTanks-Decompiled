# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/fort_rush_welcome_screen_view_model.py
from frameworks.wulf import ViewModel

class FortRushWelcomeScreenViewModel(ViewModel):
    __slots__ = ('onVideoPlay', 'onClose', 'onViewLoaded')

    def __init__(self, properties=0, commands=3):
        super(FortRushWelcomeScreenViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FortRushWelcomeScreenViewModel, self)._initialize()
        self.onVideoPlay = self._addCommand('onVideoPlay')
        self.onClose = self._addCommand('onClose')
        self.onViewLoaded = self._addCommand('onViewLoaded')
