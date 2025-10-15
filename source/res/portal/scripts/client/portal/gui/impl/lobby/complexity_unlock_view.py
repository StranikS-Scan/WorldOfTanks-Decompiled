# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/complexity_unlock_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from portal.gui.impl.gen.view_models.views.lobby.complexity_unlock_view_model import ComplexityUnlockViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from portal.sounds.sound_constants import PORTAL_COMPLEXITY_UNLOCK_SOUND_SPACE

class ComplexityUnlockView(ViewImpl):
    __slots__ = ('__unlockedComplexity',)
    _COMMON_SOUND_SPACE = PORTAL_COMPLEXITY_UNLOCK_SOUND_SPACE

    def __init__(self, layoutID, unlockedComplexity):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ComplexityUnlockViewModel()
        super(ComplexityUnlockView, self).__init__(settings)
        self.__unlockedComplexity = unlockedComplexity

    @property
    def viewModel(self):
        return super(ComplexityUnlockView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onApprove, self.__onClose),)

    def _onLoading(self, *args, **kwargs):
        super(ComplexityUnlockView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            model.setComplexity(self.__unlockedComplexity)

    def __onClose(self, *args):
        self.destroyWindow()


class ComplexityUnlockedWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, unlockedComplexity, parent=None):
        super(ComplexityUnlockedWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ComplexityUnlockView(R.views.portal.lobby.ComplexityUnlockView(), unlockedComplexity), parent=parent)
