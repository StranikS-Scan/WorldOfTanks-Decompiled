# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_tutorial_video_view_model.py
from frameworks.wulf import ViewModel

class FestivalTutorialVideoViewModel(ViewModel):
    __slots__ = ('onCloseBtnClicked', 'onStartVideoPlaying', 'onStopVideoPlaying')

    def _initialize(self):
        super(FestivalTutorialVideoViewModel, self)._initialize()
        self.onCloseBtnClicked = self._addCommand('onCloseBtnClicked')
        self.onStartVideoPlaying = self._addCommand('onStartVideoPlaying')
        self.onStopVideoPlaying = self._addCommand('onStopVideoPlaying')
