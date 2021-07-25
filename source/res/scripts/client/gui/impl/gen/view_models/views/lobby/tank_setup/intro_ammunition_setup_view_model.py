# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/intro_ammunition_setup_view_model.py
from frameworks.wulf import ViewModel

class IntroAmmunitionSetupViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(IntroAmmunitionSetupViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(IntroAmmunitionSetupViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
