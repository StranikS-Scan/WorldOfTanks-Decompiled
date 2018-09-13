# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/sf_settings.py
from gui.Scaleform.daapi.view.lobby.fortifications import FortifiedWindowScopes
from gui.Scaleform.daapi.view.lobby.fortifications.FortChoiceDivisionWindow import FortChoiceDivisionWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceWindow import FortIntelligenceWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrdersPanelComponent import FortOrdersPanelComponent
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortDisconnectViewComponent import FortDisconnectViewComponent
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortIntroView import FortIntroView
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortListView import FortListView
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortMainViewComponent import FortMainViewComponent
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortRoomView import FortRoomView
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortWelcomeViewComponent import FortWelcomeViewComponent
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.lobby.fortifications.FortBuildingProcessWindow import FortBuildingProcessWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortFixedPlayersWindow import FortFixedPlayersWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortificationsView import FortificationsView
from gui.Scaleform.daapi.view.lobby.fortifications.FortModernizationWindow import FortModernizationWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleRoomWindow import FortBattleRoomWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortBuildingCardPopover import FortBuildingCardPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortClanListWindow import FortClanListWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortClanStatisticsWindow import FortClanStatisticsWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortCreateDirectionWindow import FortCreateDirectionWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortCreationCongratulationsWindow import FortCreationCongratulationsWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderConfirmationWindow import FortOrderConfirmationWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderPopover import FortOrderPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortTransportConfirmationWindow import FortTransportConfirmationWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortBuildingComponent import FortBuildingComponent
from gui.Scaleform.daapi.view.lobby.fortifications.DemountBuildingWindow import DemountBuildingWindow
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.shared.events import LoadEvent, ShowPopoverEvent, ShowDialogEvent

def getViewSettings():
    return [ViewSettings(FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS, FortificationsView, FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_UI, ViewTypes.LOBBY_SUB, LoadEvent.LOAD_FORTIFICATIONS, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, FortTransportConfirmationWindow, FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FortOrderPopover, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_UI, ViewTypes.WINDOW, ShowPopoverEvent.SHOW_FORT_ORDER_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_ORDER_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_ALIAS, FortOrderConfirmationWindow, FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_UI, ViewTypes.TOP_WINDOW, ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS, FortCreationCongratulationsWindow, FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS, FortCreateDirectionWindow, FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, FortClanStatisticsWindow, FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS, FortClanListWindow, FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FortBuildingCardPopover, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_UI, ViewTypes.WINDOW, ShowPopoverEvent.SHOW_FORT_BUILDING_CARD_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_BUILDING_CARD_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS, FortBattleRoomWindow, FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_UI, ViewTypes.WINDOW, '', FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_EVENT, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, FortModernizationWindow, FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, FortFixedPlayersWindow, FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, FortBuildingProcessWindow, FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, FortIntelligenceWindow, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, DemountBuildingWindow, FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_COMPONENT_ALIAS, FortBuildingComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_ORDERS_PANEL_COMPONENT_ALIAS, FortOrdersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.MAIN_VIEW_ALIAS, FortMainViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.WELCOME_VIEW_ALIAS, FortWelcomeViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.DISCONNECT_VIEW_ALIAS, FortDisconnectViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_INTRO_VIEW_PY, FortIntroView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_LIST_VIEW_PY, FortListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_PY, FortRoomView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, FortChoiceDivisionWindow, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW_EVENT, None, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [FortsBusinessHandler(), FortsDialogsHandler()]


class FortsBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_EVENT, self.__showFortTransportConfirmationWindow),
         (FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_EVENT, self.__showFortOrderPopover),
         (FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_EVENT, self.__showFortCreationCongratulationsWindow),
         (FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_EVENT, self.__showFortCreateDirectionWindow),
         (FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_EVENT, self.__showFortClanStatisticsWindow),
         (FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_EVENT, self.__showFortClanListWindow),
         (FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_EVENT, self.__showFortBuildingCardPopover),
         (FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_EVENT, self.__showFortBattleRoomWindow),
         (FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_EVENT, self.__showFortModernizationWindow),
         (FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_EVENT, self.__showFortFixedPlayersWindow),
         (FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_EVENT, self.__showFortBuildingProcessWindow),
         (FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_EVENT, self.__showFortIntelligenceWindow),
         (FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_EVENT, self.__showDemountBuildingWindow),
         (FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW_EVENT, self.__showChoiceDivisionWindow)]
        super(FortsBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def __loadOrUpdateWindow(self, name, alias, ctx):
        manager = self.app.containerManager
        windowContainer = manager.getContainer(ViewTypes.WINDOW)
        window = windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: alias})
        if window is not None:
            window.updateWindow(ctx)
            isOnTop = manager.as_isOnTopS(ViewTypes.WINDOW, name)
            if not isOnTop:
                manager.as_bringToFrontS(ViewTypes.WINDOW, name)
        else:
            self.app.loadView(alias, name, ctx)
        return

    def __showChoiceDivisionWindow(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW)

    def __showDemountBuildingWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, event.ctx)

    def __showFortIntelligenceWindow(self, event):
        self.app.loadView(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW)

    def __showFortTransportConfirmationWindow(self, event):
        from debug_utils import LOG_DEBUG
        LOG_DEBUG(event.ctx)
        self._loadView(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, event.ctx['fromId'], event.ctx['toId'])

    def __showFortOrderPopover(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS)

    def __showFortCreationCongratulationsWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS)

    def __showFortCreateDirectionWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS
        self.app.loadView(alias, name)

    def __showFortClanStatisticsWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS
        self.app.loadView(alias, name)

    def __showFortClanListWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS
        self.app.loadView(alias, name)

    def __showFortBuildingCardPopover(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, event.ctx)

    def __showFortBattleRoomWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS
        self.app.loadView(alias, name, event.ctx)

    def __showFortModernizationWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS
        self.__loadOrUpdateWindow(alias, name, event.ctx)

    def __showFortFixedPlayersWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS
        self.__loadOrUpdateWindow(alias, name, event.ctx)

    def __showFortBuildingProcessWindow(self, event):
        alias = FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS
        dir = event.ctx.get('buildingDirection')
        pos = event.ctx.get('buildingPosition')
        name = '%s%d%d' % (alias, dir, pos)
        self.app.loadView(alias, name, event.ctx)


class FortsDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        super(FortsDialogsHandler, self).__init__([(ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG, self.__showFortOrderConfirmationWindow)], EVENT_BUS_SCOPE.DEFAULT)

    def __showFortOrderConfirmationWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_ALIAS, event.meta, event.handler)
