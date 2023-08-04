# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/birthday2023/birthday2023_intro_view_model.py
from frameworks.wulf import ViewModel

class Birthday2023IntroViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(Birthday2023IntroViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(Birthday2023IntroViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
