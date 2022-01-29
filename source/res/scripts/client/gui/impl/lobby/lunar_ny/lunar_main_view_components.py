# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_main_view_components.py
from gui.shared import g_eventBus
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.main_view_model import Tab
from gui.impl.lobby.lunar_ny.envelopes.envelopes_storage import EnvelopesStorageView
from gui.impl.lobby.lunar_ny.envelopes.send_envelopes_view import SendEnvelopesView
from gui.impl.lobby.lunar_ny.lunar_ny_album_view import LunarNYAlbumView
from gui.impl.lobby.lunar_ny.lunar_ny_info_view import LunarNYInfoView
from gui.impl.lobby.lunar_ny.envelopes.fill_envelope_view import FillEnvelopeView
from lunar_ny.lunar_ny_constants import MAIN_VIEW_INIT_CONTEXT_TAB, MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE, SEND_TO_PLAYER_EVENT, SEND_TO_PLAYER_EVENT_IS_ENABLED

class MainViewComponents(object):
    __slots__ = ('__views', '__currentTab', '__viewModel', '__fillEnvelopeView')

    def __init__(self, viewModel, view):
        self.__views = {Tab.STOREENVELOPES: EnvelopesStorageView(viewModel.storeEnvelopes, view),
         Tab.ALBUM: LunarNYAlbumView(viewModel.album, view),
         Tab.SENDENVELOPES: SendEnvelopesView(viewModel.sendEnvelopes, view),
         Tab.INFO: LunarNYInfoView(viewModel.info, view)}
        self.__fillEnvelopeView = FillEnvelopeView(viewModel.fillEnvelope, view)
        self.__currentTab = None
        self.__viewModel = viewModel
        return

    def initialize(self):
        for view in self.__views.values():
            view.initialize()

        self.__fillEnvelopeView.initialize()
        g_eventBus.addListener(SEND_TO_PLAYER_EVENT, self.__onSendToPlayerEvent)

    def onLoading(self, initCtx):
        self.__currentTab = initCtx.get(MAIN_VIEW_INIT_CONTEXT_TAB, Tab.SENDENVELOPES)
        for tab, view in self.__views.iteritems():
            view.onLoading(initCtx, tab == self.__currentTab)

        isFillEnvelopeState = self.__currentTab == Tab.SENDENVELOPES and initCtx.get(MAIN_VIEW_INIT_CONTEXT_ENVELOPE_TYPE, None) is not None
        self.__viewModel.setFillEnvelopeIsVisible(isFillEnvelopeState)
        self.__fillEnvelopeView.onLoading(initCtx, isFillEnvelopeState)
        return

    def onLoaded(self):
        for view in self.__views.itervalues():
            view.onLoaded()

        self.__fillEnvelopeView.onLoaded()

    def update(self):
        for view in self.__views.values():
            view.update()

    def finalize(self):
        for view in self.__views.values():
            view.finalize()

        self.__fillEnvelopeView.finalize()
        g_eventBus.removeListener(SEND_TO_PLAYER_EVENT, self.__onSendToPlayerEvent)

    def onCurrentTabChange(self, tab):
        if tab != self.__currentTab:
            self.__views[self.__currentTab].setActive(False)
            self.__views[tab].setActive(True)
        self.__currentTab = tab

    def createToolTipContent(self, event, contentID):
        return self.__fillEnvelopeView.createToolTipContent(event, contentID) if self.__fillEnvelopeView.getIsActive() else self.__views[self.__currentTab].createToolTipContent(event, contentID)

    def __onSendToPlayerEvent(self, event):
        isEnabled = event.ctx.get(SEND_TO_PLAYER_EVENT_IS_ENABLED, False)
        self.__viewModel.setFillEnvelopeIsVisible(isEnabled)
        self.__fillEnvelopeView.setActive(isEnabled)
        if isEnabled:
            self.__showFillEnvelope(event.ctx)

    def __showFillEnvelope(self, ctx):
        self.__fillEnvelopeView.show(ctx)
