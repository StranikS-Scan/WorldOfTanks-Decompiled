# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dragon_boat/dragon_boat_intro_view_model.py
from frameworks.wulf import ViewModel

class DragonBoatIntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onAccept')

    def __init__(self, properties=0, commands=2):
        super(DragonBoatIntroViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(DragonBoatIntroViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onAccept = self._addCommand('onAccept')
