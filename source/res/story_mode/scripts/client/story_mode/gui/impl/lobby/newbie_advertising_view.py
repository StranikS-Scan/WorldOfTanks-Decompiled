# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/newbie_advertising_view.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub import WindowImpl, ViewImpl
from story_mode.account_settings import setNewbieAdvertisingScreenSeen
from story_mode.gui.impl.gen.view_models.views.lobby.advertising_view_model import AdvertisingViewModel

class NewbieAdvertisingView(ViewImpl):
    __slots__ = ()
    layoutID = R.views.story_mode.lobby.NewbieAdvertisingView()

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, ViewFlags.VIEW, AdvertisingViewModel())
        super(NewbieAdvertisingView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NewbieAdvertisingView, self).getViewModel()

    def _getEvents(self):
        viewModel = self.getViewModel()
        return ((viewModel.onClose, self.__onClose), (viewModel.onSubmit, self.__onClose), (g_playerEvents.onDisconnected, self.__onDisconnected))

    def __onClose(self):
        setNewbieAdvertisingScreenSeen()
        self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()


class NewbieAdvertisingWindow(WindowImpl):

    def __init__(self, layoutID):
        super(NewbieAdvertisingWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NewbieAdvertisingView(layoutID=layoutID))
