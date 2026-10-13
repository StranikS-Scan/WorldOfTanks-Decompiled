# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/meta_intro_view.py
from __future__ import absolute_import
from account_helpers import AccountSettings
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from halloween.gui.halloween_account_settings import AccountSettingsKeys
from halloween.gui.impl.gen.view_models.views.lobby.meta_intro_view_model import MetaIntroViewModel
from halloween.gui.impl.lobby.base_view import BaseView, HWLobbyWindow
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import META_INTRO_ENTER, META_INTRO_EXIT
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from helpers import dependency

class MetaIntroView(BaseView):
    __slots__ = ()
    _hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)

    def __init__(self):
        settings = ViewSettings(R.views.halloween.mono.lobby.meta_intro(), ViewFlags.VIEW, MetaIntroViewModel())
        super(MetaIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MetaIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MetaIntroView, self)._onLoading(*args, **kwargs)
        mainGift = self._hwArtefactsCtrl.getMainGiftVehicle()
        self.viewModel.setLevel(int(mainGift.level))
        self.viewModel.setName(mainGift.userName)

    def _initialize(self, *args, **kwargs):
        super(MetaIntroView, self)._initialize(*args, **kwargs)
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


class MetaIntroWindow(HWLobbyWindow):

    def __init__(self, parent=None):
        super(MetaIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=MetaIntroView(), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
