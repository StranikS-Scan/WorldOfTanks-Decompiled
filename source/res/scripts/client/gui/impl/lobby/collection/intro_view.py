# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collection/intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.collection.intro_view_model import IntroViewModel
from gui.impl.pub import ViewImpl
from gui.collection.account_settings import setIntroShown
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import isPlayerAccount

class IntroView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
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
