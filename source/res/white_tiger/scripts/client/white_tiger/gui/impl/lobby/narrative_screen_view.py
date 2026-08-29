# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/narrative_screen_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from helpers import dependency
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.narrative_screen_view_model import NarrativeScreenViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from white_tiger.gui.white_tiger_account_settings import isFinalNarrativeVoiceActive, setFinalNarrativeVoiceActive
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController

class NarrativeScreenView(ViewImpl):
    LAYOUT_ID = R.views.white_tiger.mono.lobby.narrative_screen()
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self, layoutID=LAYOUT_ID, *args, **kwargs):
        settings = ViewSettings(layoutID, ViewFlags.VIEW, NarrativeScreenViewModel(), *args, **kwargs)
        super(NarrativeScreenView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(NarrativeScreenView, self)._onLoading(*args, **kwargs)
        voActive = isFinalNarrativeVoiceActive()
        self.viewModel.setIsVoiceoverActive(voActive)
        if self.__wtCtrl:
            self.__wtCtrl.wtHangarSound.setFinalNarrativeOpen(True)
            if voActive:
                self.__wtCtrl.wtHangarSound.setFinalNarrativeActive(True)

    @property
    def viewModel(self):
        return super(NarrativeScreenView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onVoiceoverToggle, self._onVoiceoverToggle))

    def _onVoiceoverToggle(self):
        newActive = not isFinalNarrativeVoiceActive()
        setFinalNarrativeVoiceActive(newActive)
        self.viewModel.setIsVoiceoverActive(newActive)
        if self.__wtCtrl:
            self.__wtCtrl.wtHangarSound.setFinalNarrativeActive(newActive)

    def _onClose(self):
        self.__wtCtrl.wtHangarSound.setFinalNarrativeOpen(False)
        self.destroyWindow()


class NarrativeScreenViewWindow(WindowImpl):

    def __init__(self, parent=None):
        super(NarrativeScreenViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NarrativeScreenView(), parent=parent)
