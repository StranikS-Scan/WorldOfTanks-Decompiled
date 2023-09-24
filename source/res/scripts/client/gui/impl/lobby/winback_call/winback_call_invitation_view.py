# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback_call/winback_call_invitation_view.py
import typing
import BigWorld
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_base import WinbackCallFriendBase
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_invitation_view_model import WinbackCallInvitationViewModel
from gui.impl.lobby.winback_call.winback_call_helper import fillFriendBaseData
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IWinBackCallController
from uilogging.winback_call.constants import WinbackCallLogItem, WinbackCallLogScreenParent
from uilogging.winback_call.loggers import WinBackCallLogger
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, Dict
    from gui.game_control.winback_call_controller import _FriendsCache

class WinbackCallInvitationView(ViewImpl):
    __slots__ = ('__friendsStorage', '__blur', '__wbcLogger')
    __winBackCallCtrl = dependency.descriptor(IWinBackCallController)

    def __init__(self, friendsStorage, blurLayer):
        settings = ViewSettings(R.views.lobby.winback_call.WinbackCallInvitationView())
        settings.flags = ViewFlags.VIEW
        settings.model = WinbackCallInvitationViewModel()
        self.__friendsStorage = friendsStorage
        self.__blur = CachedBlur(enabled=True, ownLayer=blurLayer, blurAnimRepeatCount=1)
        self.__wbcLogger = WinBackCallLogger()
        super(WinbackCallInvitationView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WinbackCallInvitationView, self).getViewModel()

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        self.__friendsStorage = None
        super(WinbackCallInvitationView, self)._finalize()
        return

    def _getEvents(self):
        events = super(WinbackCallInvitationView, self)._getEvents()
        return events + ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onSend, self.__onSend),
         (self.__winBackCallCtrl.onFriendStatusUpdated, self.__onFriendStatusUpdated),
         (self.__winBackCallCtrl.onStateChanged, self.__onStateChanged),
         (self.__winBackCallCtrl.onFriendsUpdated, self.__onFriendsUpdated))

    def _onLoading(self, *args, **kwargs):
        super(WinbackCallInvitationView, self)._onLoading(*args, **kwargs)
        self.__updateFriendsList()

    def __updateFriendsList(self):
        with self.viewModel.transaction() as model:
            friendsModel = model.getFriends()
            friendsModel.clear()
            for friend in self.__friendsStorage.friends:
                friendModel = WinbackCallFriendBase()
                fillFriendBaseData(friendModel, friend)
                friendsModel.addViewModel(friendModel)

            friendsModel.invalidate()

    def __onFriendStatusUpdated(self):
        self.__updateFriendsList()

    def __onFriendsUpdated(self, friendsData):
        self.__friendsStorage = friendsData
        self.__updateFriendsList()

    def __onStateChanged(self):
        if self.__winBackCallCtrl.isEnabled:
            self.__updateFriendsList()
        else:
            self.__onClose()

    def __onClose(self):
        self.destroyWindow()

    def __onSend(self, user):
        self.__wbcLogger.handleClick(WinbackCallLogItem.INVITE_BUTTON, WinbackCallLogScreenParent.FRIENDS_FORM)
        spaID = int(user.get(u'databaseID', 0))
        if spaID:
            self.__winBackCallCtrl.sendInviteCode(spaID)


class WinbackCallInvitationViewWindow(LobbyWindow):

    def __init__(self, friendsStorage, parent=None):
        self.__focusCallbackID = None
        layer = WindowLayer.FULLSCREEN_WINDOW
        blurLayer = parent.layer if parent else layer - 1
        super(WinbackCallInvitationViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackCallInvitationView(friendsStorage, blurLayer), parent=parent, layer=layer)
        return

    def _onShown(self):
        super(WinbackCallInvitationViewWindow, self)._onShown()
        self.__focusCallbackID = BigWorld.callback(0.1, self.__setFocused)

    def _finalize(self):
        if self.__focusCallbackID:
            BigWorld.cancelCallback(self.__focusCallbackID)
            self.__focusCallbackID = None
        super(WinbackCallInvitationViewWindow, self)._finalize()
        return

    def __setFocused(self):
        self.__focusCallbackID = None
        if not self.isFocused:
            self.tryFocus()
        return
