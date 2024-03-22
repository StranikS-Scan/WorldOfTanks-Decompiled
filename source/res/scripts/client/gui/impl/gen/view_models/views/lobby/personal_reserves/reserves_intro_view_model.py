# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_reserves/reserves_intro_view_model.py
from frameworks.wulf import ViewModel

class ReservesIntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onDetailsClicked')

    def __init__(self, properties=0, commands=2):
        super(ReservesIntroViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ReservesIntroViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onDetailsClicked = self._addCommand('onDetailsClicked')
