# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/intro_view_model.py
from frameworks.wulf import ViewModel

class IntroViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(IntroViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(IntroViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
