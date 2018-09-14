# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/sf_settings.py
from adisp import process
from gui.Scaleform.daapi.view.lobby.fortifications import FortifiedWindowScopes
from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleDirectionPopover import FortBattleDirectionPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortCalendarWindow import FortCalendarWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortClanStatisticsData import getDataObject as getWindowData
from gui.Scaleform.daapi.view.lobby.fortifications.FortCombatReservesIntroWindow import FortCombatReservesIntroWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortDatePickerPopover import FortDatePickerPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortChoiceDivisionWindow import FortChoiceDivisionWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortClanBattleRoom import FortClanBattleRoom
from gui.Scaleform.daapi.view.lobby.fortifications.FortDeclarationOfWarWindow import FortDeclarationOfWarWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortDisableDefencePeriodWindow import FortDisableDefencePeriodWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceWindow import FortIntelligenceWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceNotAvailableWindow import FortIntelligenceNotAvailableWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderInfoWindow import FortOrderInfoWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrdersPanelComponent import FortOrdersPanelComponent
from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleRoomOrdersPanelComponent import FortBattleRoomOrdersPanelComponent
from gui.Scaleform.daapi.view.lobby.fortifications.FortRosterIntroWindow import FortRosterIntroWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortSortieOrdersPanelComponent import FortSortieOrdersPanelComponent
from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsDayoffPopover import FortSettingsDayoffPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsWindow import FortSettingsWindow
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortIntelligenceClanDescription import FortIntelligenceClanDescription
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesListView import FortBattlesListView
from gui.Scaleform.daapi.view.lobby.fortifications.FortPeriodDefenceWindow import FortPeriodDefenceWindow
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortDisconnectViewComponent import FortDisconnectViewComponent
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortIntelFilter import FortIntelFilter
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesIntroView import FortBattlesIntroView
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesSortieListView import FortBattlesSortieListView
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortMainViewComponent import FortMainViewComponent
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortBattlesRoomView import FortBattlesRoomView
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortWelcomeViewComponent import FortWelcomeViewComponent
from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceClanFilterPopover import FortIntelligenceClanFilterPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsPeripheryPopover import FortSettingsPeripheryPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsDefenceHourPopover import FortSettingsDefenceHourPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsVacationPopover import FortSettingsVacationPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleResultsWindow import FortBattleResultsWindow
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.prb_control.settings import UNIT_MODE_FLAGS
from gui.shared import EVENT_BUS_SCOPE
from debug_utils import LOG_DEBUG
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
from gui.Scaleform.daapi.view.lobby.fortifications.FortNotCommanderFirstEnterWindow import FortNotCommanderFirstEnterWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderConfirmationWindow import FortOrderConfirmationWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderPopover import FortOrderPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortTransportConfirmationWindow import FortTransportConfirmationWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortBuildingComponent import FortBuildingComponent
from gui.Scaleform.daapi.view.lobby.fortifications.FortDemountBuildingWindow import FortDemountBuildingWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrderSelectPopover import FortOrderSelectPopover
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.shared.events import ShowDialogEvent
from gui.shared.utils.functions import getViewName

def getViewSettings():
    return [ViewSettings(FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS, FortificationsView, FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_UI, ViewTypes.LOBBY_SUB, FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, FortTransportConfirmationWindow, FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS, FortPeriodDefenceWindow, FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_ALIAS, FortRosterIntroWindow, FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FortOrderPopover, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, FortBattleDirectionPopover, FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, FortSettingsPeripheryPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, FortSettingsDefenceHourPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, FortSettingsVacationPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, FortDatePickerPopover, FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS, FortOrderSelectPopover, FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_ORDER_SELECT_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_ALIAS, FortOrderConfirmationWindow, FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_UI, ViewTypes.TOP_WINDOW, ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS, FortCreationCongratulationsWindow, FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS, FortCreateDirectionWindow, FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_ALIAS, FortDeclarationOfWarWindow, FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, FortClanStatisticsWindow, FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS, FortCalendarWindow, FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS, FortClanListWindow, FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS, FortNotCommanderFirstEnterWindow, FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FortBuildingCardPopover, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, FortIntelligenceClanFilterPopover, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, FortSettingsDayoffPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS, FortBattleRoomWindow, FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_UI, ViewTypes.WINDOW, '', FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, FortModernizationWindow, FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, FortFixedPlayersWindow, FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, FortBuildingProcessWindow, FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, FortIntelligenceWindow, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW, FortIntelligenceNotAvailableWindow, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, FortDemountBuildingWindow, FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS, FortDisableDefencePeriodWindow, FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS, FortSettingsWindow, FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, FortOrderInfoWindow, FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, FortBattleResultsWindow, FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_ALIAS, FortCombatReservesIntroWindow, FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_ALIAS, None, FortifiedWindowScopes.FORT_MAIN_SCOPE, True),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_COMPONENT_ALIAS, FortBuildingComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_ORDERS_PANEL_COMPONENT_ALIAS, FortOrdersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLEROOM_ORDERS_PANEL_COMPONENT_ALIAS, FortBattleRoomOrdersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_SORTIE_ORDERS_PANEL_COMPONENT_ALIAS, FortSortieOrdersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.MAIN_VIEW_ALIAS, FortMainViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.WELCOME_VIEW_ALIAS, FortWelcomeViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.DISCONNECT_VIEW_ALIAS, FortDisconnectViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_INTRO_VIEW_PY, FortBattlesIntroView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_LIST_VIEW_PY, FortBattlesSortieListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_LIST_VIEW_PY, FortBattlesListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_PY, FortBattlesRoomView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_ROOM_VIEW_PY, FortClanBattleRoom, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_INTEL_FILTER_ALIAS, FortIntelFilter, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, FortChoiceDivisionWindow, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_DESCRIPTION, FortIntelligenceClanDescription, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [FortsBusinessHandler(), FortsDialogsHandler()]


class FortsBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, self.__showAsyncDataView),
         (FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS, self.__showFortBattleRoomWindow),
         (FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, self.__showOrUpdateWindow),
         (FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, self.__showOrUpdateWindow),
         (FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, self.__showFortBuildingProcessWindow),
         (FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, self.__showOrderInfo),
         (FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, self.__showFortBattleResultsWindow),
         (FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS, self.__showViewSimple),
         (FORTIFICATION_ALIASES.FORT_COMBAT_RESERVES_INTRO_ALIAS, self.__showViewSimple)]
        super(FortsBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)
        self.__fortClanInfoNameInc = 0

    def _loadUniqueWindow(self, alias, ctx = None):
        if ctx is not None:
            return self.app.loadView(alias, alias, ctx)
        else:
            return self.app.loadView(alias, alias)

    def __showViewSimple(self, event):
        self.app.loadView(event.eventType, event.name, event.ctx)

    def __showMultipleViews(self, event):
        self.app.loadView(event.eventType, event.name + str(self.__fortClanInfoNameInc), event.ctx)
        self.__fortClanInfoNameInc += 1

    def __showOrderInfo(self, event):
        orderID = event.ctx.get('orderID', None)
        self.app.loadView(FORTIFICATION_ALIASES.FORT_ORDER_INFO_WINDOW_ALIAS, str(orderID), event.ctx)
        return

    def __showOrUpdateWindow(self, event):
        self.__loadOrUpdateWindow(event.eventType, event.name, event.ctx)

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

    def __showFortBattleResultsWindow(self, event):
        ctx = event.ctx['data']
        self.app.loadView(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, getViewName(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, ctx['battleID']), ctx)

    def __showFortBattleRoomWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS
        manager = self.app.containerManager
        windowContainer = manager.getContainer(ViewTypes.WINDOW)
        window = windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: alias})
        if window is not None:
            if event.ctx.get('modeFlags') == UNIT_MODE_FLAGS.SHOW_LIST:
                window.loadListView()
        self.app.loadView(alias, name, event.ctx)
        return

    def __showFortBuildingProcessWindow(self, event):
        alias = FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS
        dir = event.ctx.get('buildingDirection')
        pos = event.ctx.get('buildingPosition')
        name = '%s%d%d' % (alias, dir, pos)
        self.app.loadView(alias, name, event.ctx)

    @process
    def __showAsyncDataView(self, event):
        data = yield getWindowData()
        if data is not None:
            self.app.loadView(event.eventType, event.name, data)
        return


class FortsDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        super(FortsDialogsHandler, self).__init__([(ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG, self.__showFortOrderConfirmationWindow)], EVENT_BUS_SCOPE.DEFAULT)

    def __showFortOrderConfirmationWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_ALIAS, event.meta, event.handler)
