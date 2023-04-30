# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/crew_intro_view_model.py
from frameworks.wulf import ViewModel

class CrewIntroViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(CrewIntroViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CrewIntroViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
