# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/welcome_screen_model.py
from frameworks.wulf import ViewModel

class WelcomeScreenModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(WelcomeScreenModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WelcomeScreenModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
