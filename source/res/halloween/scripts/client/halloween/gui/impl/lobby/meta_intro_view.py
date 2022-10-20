# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/meta_intro_view.py
import typing
from account_helpers import AccountSettings
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
from halloween.gui.impl.gen.view_models.views.lobby.common.base_view_model import BaseViewModel
from halloween.gui.impl.lobby.base_event_view import BaseEventView
from halloween.hw_constants import AccountSettingsKeys

class MetaIntroView(BaseEventView):
    __slots__ = ('_blur', '_onViewLoaded', '_onViewClosed')
    layoutID = R.views.halloween.lobby.MetaIntroView()

    def __init__(self, layoutID=None, onViewLoaded=None, onViewClosed=None):
        settings = ViewSettings(layoutID or self.layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, BaseViewModel())
        self._onViewLoaded = onViewLoaded
        self._onViewClosed = onViewClosed
        super(MetaIntroView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        if self._onViewLoaded:
            self._onViewLoaded()
        super(MetaIntroView, self)._onLoading(*args, **kwargs)

    def _onClose(self):
        settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
        settings[AccountSettingsKeys.META_INTRO_VIEW_SHOWED] = True
        AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)
        if self._onViewClosed:
            self._onViewClosed()
        self.destroyWindow()


class MetaIntroWindow(LobbyWindow):

    def __init__(self, layoutID, onViewLoaded=None, onViewClosed=None, parent=None):
        super(MetaIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=MetaIntroView(layoutID=layoutID, onViewLoaded=onViewLoaded, onViewClosed=onViewClosed), parent=parent)
        self._blur = None
        self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)
        return

    def _finalize(self):
        if self._blur:
            self._blur.fini()
        super(MetaIntroWindow, self)._finalize()
