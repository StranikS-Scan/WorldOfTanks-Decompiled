# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/widgets/progression_view_model.py
from frameworks.wulf import ViewModel

class ProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutClicked', 'onTakeReward')

    def __init__(self, properties=0, commands=3):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onAboutClicked = self._addCommand('onAboutClicked')
        self.onTakeReward = self._addCommand('onTakeReward')
