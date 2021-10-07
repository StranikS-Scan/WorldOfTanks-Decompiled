# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/subscription/subscription_award_view.py
import WWISE
import BigWorld
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.subscription.subscription_award_view_model import SubscriptionAwardViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.Scaleform.daapi.view.lobby.wot_plus.sound_constants import SOUNDS
from gui.shared.event_dispatcher import showWotPlusInfoPage

class SubscriptionAwardView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = SubscriptionAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SubscriptionAwardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SubscriptionAwardView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onCloseButtonClick += self._onClose
        self.viewModel.onInfoButtonClick += self._onInfo

    def _finalize(self):
        self.viewModel.onCloseButtonClick -= self._onClose
        self._soundsOnClose()

    def _onLoading(self, *args, **kwargs):
        self.viewModel.setNextCharge(BigWorld.player().renewableSubscription.getExpiryTime())
        self._soundsOnOpen()

    def _onClose(self):
        self.destroyWindow()

    def _onInfo(self):
        showWotPlusInfoPage()

    def _soundsOnOpen(self):
        WWISE.WW_eventGlobal(backport.sound(R.sounds.gui_reward_screen_general()))
        WWISE.WW_setState(SOUNDS.OVERLAY_HANGAR_GENERAL, SOUNDS.OVERLAY_HANGAR_GENERAL_ON)

    def _soundsOnClose(self):
        WWISE.WW_setState(SOUNDS.OVERLAY_HANGAR_GENERAL, SOUNDS.OVERLAY_HANGAR_GENERAL_OFF)


class SubscriptionAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self):
        super(SubscriptionAwardWindow, self).__init__(content=SubscriptionAwardView(R.views.lobby.subscription.SubscriptionAwardView()))
