# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/newbie_advertising_view.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub import WindowImpl, ViewImpl
from story_mode.account_settings import setNewbieAdvertisingScreenSeen
from story_mode.gui.impl.gen.view_models.views.lobby.advertising_view_model import AdvertisingViewModel
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode.uilogging.story_mode.loggers import NewbieAdvertisingViewLogger

class NewbieAdvertisingView(ViewImpl):
    __slots__ = ('_uiLogger',)
    layoutID = R.views.story_mode.lobby.NewbieAdvertisingView()

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, ViewFlags.VIEW, AdvertisingViewModel())
        self._uiLogger = NewbieAdvertisingViewLogger()
        super(NewbieAdvertisingView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NewbieAdvertisingView, self).getViewModel()

    def _getEvents(self):
        viewModel = self.getViewModel()
        return ((viewModel.onClose, self.__onClose),
         (viewModel.onClose, self.__onCloseClicked),
         (viewModel.onSubmit, self.__onClose),
         (viewModel.onSubmit, self.__onSubmitClicked),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    def _onLoaded(self, *args, **kwargs):
        super(NewbieAdvertisingView, self)._onLoaded(*args, **kwargs)
        self._uiLogger.logOpen()

    def __onClose(self):
        self._uiLogger.logClose()
        setNewbieAdvertisingScreenSeen()
        self.destroyWindow()

    def __onCloseClicked(self):
        self._uiLogger.logClick(LogButtons.CLOSE)

    def __onSubmitClicked(self):
        self._uiLogger.logClick(LogButtons.SUBMIT)

    def __onDisconnected(self):
        self.destroyWindow()


class NewbieAdvertisingWindow(WindowImpl):

    def __init__(self, layoutID):
        super(NewbieAdvertisingWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NewbieAdvertisingView(layoutID=layoutID))
