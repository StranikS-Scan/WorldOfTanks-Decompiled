# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/base_event_view.py
from collections import namedtuple
import HBAccountSettings
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import AccountSettingsKeys
InfoCommonViewSettings = namedtuple('InfoCommonViewSettings', ('layoutID', 'viewClass', 'viewKey'))

class BaseEventView(ViewImpl, IGlobalListener):
    DESTROY_ON_EVENT_DISABLED = True
    INFO_VIEW_SETTINGS = InfoCommonViewSettings(layoutID=None, viewClass=None, viewKey=None)
    _gameEventController = dependency.descriptor(IGameEventController)

    def _onLoading(self, *args, **kwargs):
        super(BaseEventView, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()
        self.updateHeaderMenu(HeaderMenuVisibilityState.NOTHING)
        self._showInfoWindow(self.INFO_VIEW_SETTINGS)
        self._gameEventController.onGameParamsChanged += self._onGameParamsChanged

    def _finalize(self):
        self.stopGlobalListening()
        self.updateHeaderMenu(HeaderMenuVisibilityState.ALL)
        self._gameEventController.onGameParamsChanged -= self._onGameParamsChanged
        super(BaseEventView, self)._finalize()

    def onPrbEntitySwitched(self):
        if not self._gameEventController.isHistoricalBattlesMode():
            self.destroyWindow()

    def updateHeaderMenu(self, state):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onGameParamsChanged(self):
        if not self._gameEventController.isEnabled() and self.DESTROY_ON_EVENT_DISABLED:
            self.destroyWindow()

    @staticmethod
    def _showInfoWindow(infoViewSettings):
        if infoViewSettings.layoutID and infoViewSettings.viewClass and infoViewSettings.viewKey:
            settings = HBAccountSettings.getSettings(AccountSettingsKeys.HISTORICAL_BATTLES_INFO_WINDOWS)
            if not settings.get(infoViewSettings.viewKey):
                from historical_battles.gui.shared.event_dispatcher import showInfoWindow
                showInfoWindow((infoViewSettings.layoutID, infoViewSettings.viewClass))
            settings[infoViewSettings.viewKey] = True
            HBAccountSettings.setSettings(AccountSettingsKeys.HISTORICAL_BATTLES_INFO_WINDOWS, settings)
