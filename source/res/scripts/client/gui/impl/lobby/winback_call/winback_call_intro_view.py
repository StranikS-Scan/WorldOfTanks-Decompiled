# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback_call/winback_call_intro_view.py
from account_helpers.AccountSettings import AccountSettings, WinBackCall
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_intro_view_model import WinbackCallIntroViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import openWinBackCallMainView
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from skeletons.gui.game_control import IWinBackCallController
from uilogging.winback_call.constants import WinbackCallLogItem, WinbackCallLogScreenParent
from uilogging.winback_call.loggers import WinBackCallLogger

class WinbackCallIntroView(ViewImpl):
    __slots__ = ()
    __winBackCallCtrl = dependency.descriptor(IWinBackCallController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.winback_call.WinbackCallIntroView())
        settings.flags = ViewFlags.VIEW
        settings.model = WinbackCallIntroViewModel()
        super(WinbackCallIntroView, self).__init__(settings)

    def _initialize(self, *args, **kwargs):
        super(WinbackCallIntroView, self)._initialize(*args, **kwargs)
        switchHangarFilteredFilter(on=True)

    def _finalize(self):
        switchHangarFilteredFilter(on=False)
        super(WinbackCallIntroView, self)._finalize()

    @property
    def viewModel(self):
        return super(WinbackCallIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WinbackCallIntroView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _onLoaded(self, *args, **kwargs):
        super(WinbackCallIntroView, self)._onLoaded(*args, **kwargs)
        AccountSettings.setWinBackCallSetting(WinBackCall.WIN_BACK_CALL_SHOWN_INTRO, True)

    def _getEvents(self):
        events = super(WinbackCallIntroView, self)._getEvents()
        return events + ((self.__winBackCallCtrl.onConfigChanged, self.__onConfigChanged), (self.__winBackCallCtrl.onStateChanged, self.__onStateChanged), (self.viewModel.onClose, self.__onClose))

    def __onConfigChanged(self):
        self.__updateModel()

    def __onStateChanged(self):
        if self.__winBackCallCtrl.isEnabled:
            self.__updateModel()
        else:
            self.destroyWindow()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            startTime, endTime = self.__winBackCallCtrl.eventPeriod()
            model.setEventStart(startTime)
            model.setEventFinish(endTime)

    def __onClose(self):
        WinBackCallLogger().handleClick(WinbackCallLogItem.ACCEPT_BUTTON, WinbackCallLogScreenParent.INTRO_SCREEN)
        openWinBackCallMainView()
        self.destroyWindow()


class WinbackCallIntroViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WinbackCallIntroViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackCallIntroView(), parent=parent)
