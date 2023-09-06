# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/battle/epilogue_window_view_model.py
from frameworks.wulf import ViewModel

class EpilogueWindowViewModel(ViewModel):
    __slots__ = ('onClose', 'onLoaded')

    def __init__(self, properties=0, commands=2):
        super(EpilogueWindowViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(EpilogueWindowViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onLoaded = self._addCommand('onLoaded')
