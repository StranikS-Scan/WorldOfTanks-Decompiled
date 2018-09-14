# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/stronghold/stronghold_provider.py
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui import DialogsInterface
from gui.wgnc.proxy_data import ShowInBrowserItem
from gui.wgnc.actions import OpenInternalBrowser
from gui.Scaleform.framework import g_entitiesFactories
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.clans.clan_helpers import isStrongholdsEnabled
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class ClientStrongholdProvider(IGlobalListener):
    """
    Handle strongholds events
    Check server settings for isStrongholdsEnabled flag change
    and if flag disabled - leave unit and show info popup if possible
    """
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(ClientStrongholdProvider, self).__init__()
        self.__tabActive = False
        self.__entityActive = False
        self.__unitActive = False
        if self.prbEntity:
            self.__checkSwitch()

    def start(self):
        self.startGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_eventBus.addListener(events.StrongholdEvent.STRONGHOLD_ACTIVATED, self.__onStrongholdsActivate, EVENT_BUS_SCOPE.FORT)
        g_eventBus.addListener(events.StrongholdEvent.STRONGHOLD_DEACTIVATED, self.__onStrongholdsDeactivate, EVENT_BUS_SCOPE.FORT)
        from gui.Scaleform.daapi.view.lobby.strongholds import createStrongholdsWebHandlers
        ShowInBrowserItem.addWebHandler('stronghold', createStrongholdsWebHandlers(True))
        OpenInternalBrowser.addWebHandler('stronghold', createStrongholdsWebHandlers(True))

    def stop(self):
        self.stopGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_eventBus.removeListener(events.StrongholdEvent.STRONGHOLD_ACTIVATED, self.__onStrongholdsActivate, EVENT_BUS_SCOPE.FORT)
        g_eventBus.removeListener(events.StrongholdEvent.STRONGHOLD_DEACTIVATED, self.__onStrongholdsDeactivate, EVENT_BUS_SCOPE.FORT)
        ShowInBrowserItem.removeWebHandler('stronghold')
        OpenInternalBrowser.removeWebHandler('stronghold')

    def onPrbEntitySwitched(self):
        self.__checkSwitch()

    def __onServerSettingChanged(self, diff):
        """
        Check isStrongholdsEnabled flag for change.
        If true - leave from Strongholds Tab(if active) and
        if unit not created - close battle room window and show info popup
        """
        if 'isStrongholdsEnabled' in diff:
            enabled = diff['isStrongholdsEnabled']
            if not enabled:
                if self.__tabActive or self.__entityActive:
                    if self.__tabActive:
                        g_eventBus.handleEvent(g_entitiesFactories.makeLoadEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
                    if not self.__unitActive:
                        self.__leave()
                        self.__showPopupDlg()

    @process
    def __leave(self):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction())

    def __checkSwitch(self):
        """
        Check for unit change.
        Show info popup if on unit leave isStrongholdsEnabled flag is disabled
        """
        entity = self.prbEntity
        flags = entity.getFunctionalFlags()
        entityActive = flags & FUNCTIONAL_FLAG.FORT2 > 0
        unitActive = flags & FUNCTIONAL_FLAG.UNIT > 0 and entityActive
        switched = unitActive is not self.__unitActive
        if switched:
            isStrongholdsDisabled = not isStrongholdsEnabled()
            if isStrongholdsDisabled and self.__unitActive:
                self.__showPopupDlg()
        self.__entityActive = entityActive
        self.__unitActive = unitActive

    def __onStrongholdsActivate(self, _):
        self.__tabActive = True

    def __onStrongholdsDeactivate(self, _):
        self.__tabActive = False

    @process
    def __showPopupDlg(self):
        yield DialogsInterface.showI18nInfoDialog('fortDisabled')
