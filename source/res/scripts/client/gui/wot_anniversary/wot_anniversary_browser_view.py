# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/wot_anniversary_browser_view.py
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IWotAnniversaryController

class WotAnniversaryBrowserView(WebView, IGlobalListener):
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)

    def webHandlers(self):
        from web_handlers import createWotAnniversaryWebHandlers
        return createWotAnniversaryWebHandlers()

    def onPrbEntitySwitched(self):
        self.destroy()

    def _populate(self):
        super(WotAnniversaryBrowserView, self)._populate()
        self.__wotAnniversaryCtrl.onSettingsChanged += self.__onSettingsChange
        switchHangarOverlaySoundFilter(on=True)
        self.startGlobalListening()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(WotAnniversaryBrowserView, self)._onRegisterFlashComponent(viewPy, alias)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        super(WotAnniversaryBrowserView, self)._dispose()
        self.stopGlobalListening()
        self.__wotAnniversaryCtrl.onSettingsChanged -= self.__onSettingsChange
        switchHangarOverlaySoundFilter(on=False)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)

    def __onSettingsChange(self):
        if not self.__wotAnniversaryCtrl.isAvailable():
            self.destroy()
