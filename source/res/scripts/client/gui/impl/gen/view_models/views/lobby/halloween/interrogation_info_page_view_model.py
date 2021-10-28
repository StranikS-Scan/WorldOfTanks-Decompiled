# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/interrogation_info_page_view_model.py
from frameworks.wulf import ViewModel

class InterrogationInfoPageViewModel(ViewModel):
    __slots__ = ('onAccept', 'onClose')

    def __init__(self, properties=0, commands=2):
        super(InterrogationInfoPageViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(InterrogationInfoPageViewModel, self)._initialize()
        self.onAccept = self._addCommand('onAccept')
        self.onClose = self._addCommand('onClose')
