# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/progression/fort_rush_progression_complete_view_model.py
from frameworks.wulf import ViewModel

class FortRushProgressionCompleteViewModel(ViewModel):
    __slots__ = ('onClose', 'onSoundPlay')

    def __init__(self, properties=0, commands=2):
        super(FortRushProgressionCompleteViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FortRushProgressionCompleteViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onSoundPlay = self._addCommand('onSoundPlay')
