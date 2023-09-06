# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collection/intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collection.intro_view_model import IntroViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.collection.account_settings import setIntroShown
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import isPlayerAccount

class IntroView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.collection.IntroView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = IntroViewModel()
        super(IntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroView, self).getViewModel()

    def _finalize(self):
        setIntroShown()
        if isPlayerAccount():
            g_eventBus.handleEvent(events.CollectionsEvent(events.CollectionsEvent.COLLECTION_INTRO_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        super(IntroView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self):
        self.destroyWindow()


class IntroWindow(LobbyWindow):

    def __init__(self, parent=None):
        super(IntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=IntroView(), parent=parent)
