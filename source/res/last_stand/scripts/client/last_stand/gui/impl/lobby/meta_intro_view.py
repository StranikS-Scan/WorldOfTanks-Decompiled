# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/meta_intro_view.py
from account_helpers import AccountSettings
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui.impl.gen.view_models.views.lobby.meta_intro_view_model import MetaIntroViewModel
from last_stand.gui.impl.lobby.base_view import BaseView, EventLobbyWindow
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import META_INTRO_ENTER, META_INTRO_EXIT
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from helpers import dependency

class MetaIntroView(BaseView):
    __slots__ = ()
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)

    def __init__(self):
        settings = ViewSettings(R.views.last_stand.mono.lobby.meta_intro(), ViewFlags.VIEW, MetaIntroViewModel())
        super(MetaIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MetaIntroView, self).getViewModel()

    def _initialize(self):
        super(MetaIntroView, self)._initialize()
        playSound(META_INTRO_ENTER)

    def _finalize(self):
        playSound(META_INTRO_EXIT)
        super(MetaIntroView, self)._finalize()

    def _subscribe(self):
        super(MetaIntroView, self)._subscribe()
        self.viewModel.onClose += self._onClose

    def _unsubscribe(self):
        super(MetaIntroView, self)._unsubscribe()
        self.viewModel.onClose -= self._onClose

    def _onClose(self):
        settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
        settings[AccountSettingsKeys.META_INTRO_VIEW_SHOWED] = True
        AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)
        self.destroyWindow()


class MetaIntroWindow(EventLobbyWindow):

    def __init__(self, parent=None):
        super(MetaIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=MetaIntroView(), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
