# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/sf_settings.py
from adisp import process
from gui.Scaleform.daapi.view.lobby.fortifications import FortifiedWindowScopes
from gui.Scaleform.daapi.view.lobby.fortifications.FortBattleDirectionPopover import FortBattleDirectionPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortCalendarWindow import FortCalendarWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortClanStatisticsData import getDataObject as getWindowData
from gui.Scaleform.daapi.view.lobby.fortifications.FortDatePickerPopover import FortDatePickerPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortChoiceDivisionWindow import FortChoiceDivisionWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortClanBattleRoom import FortClanBattleRoom
from gui.Scaleform.daapi.view.lobby.fortifications.FortDeclarationOfWarWindow import FortDeclarationOfWarWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortDisableDefencePeriodWindow import FortDisableDefencePeriodWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceWindow import FortIntelligenceWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortIntelligenceNotAvailableWindow import FortIntelligenceNotAvailableWindow
from gui.Scaleform.daapi.view.lobby.fortifications.FortOrdersPanelComponent import FortOrdersPanelComponent
from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsDayoffPopover import FortSettingsDayoffPopover
from gui.Scaleform.daapi.view.lobby.fortifications.FortSettingsWindow import FortSettingsWindow
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortIntelligenceClanDescription import FortIntelligenceClanDescription
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortClanBattleList import FortClanBattleList
from gui.Scaleform.daapi.view.lobby.fortifications.FortPeriodDefenceWindow import FortPeriodDefenceWindow
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortDisconnectViewComponent import FortDisconnectViewComponent
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortIntelFilter import FortIntelFilter
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortIntroView import FortIntroView
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortListView import FortListView
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortMainViewComponent import FortMainViewComponent
from gui.Scaleform.daapi.view.lobby.fortifications.components.FortRoomView import FortRoomView
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
from gui.Scaleform.daapi.view.lobby.fortifications.DemountBuildingWindow import DemountBuildingWindow
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.shared.events import LoadEvent, ShowPopoverEvent, ShowDialogEvent

def getViewSettings():
    return [ViewSettings(FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS, FortificationsView, FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_UI, ViewTypes.LOBBY_SUB, LoadEvent.LOAD_FORTIFICATIONS, ScopeTemplates.LOBBY_SUB_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, FortTransportConfirmationWindow, FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS, FortPeriodDefenceWindow, FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_ALIAS, FortOrderPopover, FORTIFICATION_ALIASES.FORT_ORDER_POPOVER_UI, ViewTypes.WINDOW, ShowPopoverEvent.SHOW_FORT_ORDER_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_ORDER_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_ALIAS, FortBattleDirectionPopover, FORTIFICATION_ALIASES.FORT_BATTLE_DIRECTION_POPOVER_UI, ViewTypes.WINDOW, ShowPopoverEvent.SHOW_FORT_BATTLE_DIRECTION_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_BATTLE_DIRECTION_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_ALIAS, FortSettingsPeripheryPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_PERIPHERY_POPOVER_UI, ViewTypes.TOP_WINDOW, ShowPopoverEvent.SHOW_FORT_SETTINGS_PERIPHERY_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_SETTINGS_PERIPHERY_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_ALIAS, FortSettingsDefenceHourPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_DEFENCE_HOUR_POPOVER_UI, ViewTypes.TOP_WINDOW, ShowPopoverEvent.SHOW_FORT_SETTINGS_DEFENCE_HOUR_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_SETTINGS_DEFENCE_HOUR_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_ALIAS, FortSettingsVacationPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_VACATION_POPOVER_UI, ViewTypes.TOP_WINDOW, ShowPopoverEvent.SHOW_FORT_SETTINGS_VACATION_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_SETTINGS_VACATION_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_ALIAS, FortDatePickerPopover, FORTIFICATION_ALIASES.FORT_DATE_PICKER_POPOVER_UI, ViewTypes.WINDOW, ShowPopoverEvent.SHOW_FORT_DATE_PICKER_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_DATE_PICKER_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_ALIAS, FortOrderConfirmationWindow, FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_UI, ViewTypes.TOP_WINDOW, ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS, FortCreationCongratulationsWindow, FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS, FortCreateDirectionWindow, FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_ALIAS, FortDeclarationOfWarWindow, FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, FortClanStatisticsWindow, FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS, FortCalendarWindow, FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS, FortClanListWindow, FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS, FortNotCommanderFirstEnterWindow, FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, FortBuildingCardPopover, FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_UI, ViewTypes.WINDOW, ShowPopoverEvent.SHOW_FORT_BUILDING_CARD_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_BUILDING_CARD_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_ALIAS, FortIntelligenceClanFilterPopover, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_UI, ViewTypes.WINDOW, ShowPopoverEvent.SHOW_FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_INTELLIGENCE_CLAN_FILTER_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_ALIAS, FortSettingsDayoffPopover, FORTIFICATION_ALIASES.FORT_SETTINGS_DAYOFF_POPOVER_UI, ViewTypes.TOP_WINDOW, ShowPopoverEvent.SHOW_FORT_SETTINGS_DAYOFF_POPOVER_EVENT, ShowPopoverEvent.SHOW_FORT_SETTINGS_DAYOFF_POPOVER_EVENT, FortifiedWindowScopes.FORT_WINDOWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_ALIAS, FortBattleRoomWindow, FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_UI, ViewTypes.WINDOW, '', FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_EVENT, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, FortModernizationWindow, FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, FortFixedPlayersWindow, FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_ALIAS, FortBuildingProcessWindow, FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW, FortIntelligenceWindow, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW, FortIntelligenceNotAvailableWindow, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, DemountBuildingWindow, FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS, FortDisableDefencePeriodWindow, FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_UI, ViewTypes.TOP_WINDOW, FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS, FortSettingsWindow, FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, FortBattleResultsWindow, FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_EVENT, None, FortifiedWindowScopes.FORT_MAIN_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BUILDING_COMPONENT_ALIAS, FortBuildingComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_ORDERS_PANEL_COMPONENT_ALIAS, FortOrdersPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.MAIN_VIEW_ALIAS, FortMainViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.WELCOME_VIEW_ALIAS, FortWelcomeViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.DISCONNECT_VIEW_ALIAS, FortDisconnectViewComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_INTRO_VIEW_PY, FortIntroView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_LIST_VIEW_PY, FortListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_LIST_VIEW_PY, FortClanBattleList, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_PY, FortRoomView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_ROOM_VIEW_PY, FortClanBattleRoom, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_INTEL_FILTER_ALIAS, FortIntelFilter, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, FortChoiceDivisionWindow, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW_UI, ViewTypes.WINDOW, FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW_EVENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_CLAN_DESCRIPTION, FortIntelligenceClanDescription, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [FortsBusinessHandler(), FortsDialogsHandler()]


class FortsBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_EVENT, self.__showFortTransportConfirmationWindow),
         (FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_EVENT, self.__showPeriodDefenceWindow),
         (FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_EVENT, self.__showFortCreationCongratulationsWindow),
         (FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_EVENT, self.__showFortCreateDirectionWindow),
         (FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_EVENT, self.__showFortDeclarationOfWarWindow),
         (FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_EVENT, self.__showAsyncDataView),
         (FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_EVENT, self.__showFortCalendarWindow),
         (FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_EVENT, self.__showFortClanListWindow),
         (FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_EVENT, self.__showFortBuildingCardPopover),
         (FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_EVENT, self.__showFortBattleRoomWindow),
         (FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_EVENT, self.__showFortModernizationWindow),
         (FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_EVENT, self.__showFortFixedPlayersWindow),
         (FORTIFICATION_ALIASES.FORT_BUILDING_PROCESS_WINDOW_EVENT, self.__showFortBuildingProcessWindow),
         (FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_EVENT, self.__showFortIntelligenceWindow),
         (FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_EVENT, self.__showDemountBuildingWindow),
         (FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW_EVENT, self.__showChoiceDivisionWindow),
         (FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_EVENT, self.__showFortSettingsWindow),
         (FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_EVENT, self.__showFortDisableDefencePeriodWindow),
         (FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_EVENT, self.__showFortBattleResultsWindow),
         (FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_EVENT, self.__showFortNotCommanderFirstEnterWindow)]
        super(FortsBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def _loadUniqueWindow(self, alias, ctx = None):
        if ctx is not None:
            return self.app.loadView(alias, alias, ctx)
        else:
            return self.app.loadView(alias, alias)

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

    def __showFortDisableDefencePeriodWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_DISABLE_DEFENCE_PERIOD_ALIAS)

    def __showFortSettingsWindow(self, event):
        self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS)

    def __showFortBattleResultsWindow(self, event):
        ctx = event.ctx['data']
        self.app.loadView(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, 'fortBattleResults%d' % ctx['battleID'], ctx)

    def __showChoiceDivisionWindow(self, event):
        self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW)

    def __showDemountBuildingWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, event.ctx)

    def __showFortIntelligenceWindow(self, event):
        if not self.app.varsManager.isFortificationBattleAvailable():
            self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW, {'isDefenceHourEnabled': True})
        elif not event.ctx['isDefenceHourEnabled']:
            self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW, event.ctx)
        else:
            self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW)

    def __showFortTransportConfirmationWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_TRANSPORT_CONFIRMATION_WINDOW_ALIAS, event.ctx['fromId'], event.ctx['toId'])

    def __showFortCreationCongratulationsWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS)

    def __showPeriodDefenceWindow(self, event):
        self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_PERIOD_DEFENCE_WINDOW_ALIAS)

    def __showFortCreateDirectionWindow(self, event):
        self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS)

    def __showFortDeclarationOfWarWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_DECLARATION_OF_WAR_WINDOW_ALIAS, event.ctx)

    def __showFortCalendarWindow(self, event):
        self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS, event.ctx)

    def __showFortClanListWindow(self, event):
        self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS)

    def __showFortBuildingCardPopover(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_BUILDING_CARD_POPOVER_ALIAS, event.ctx)

    def __showFortNotCommanderFirstEnterWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS)

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

    @process
    def __showAsyncDataView(self, event):
        data = yield getWindowData()
        if data is not None:
            self._loadUniqueWindow(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS, data)
        return


class FortsDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        super(FortsDialogsHandler, self).__init__([(ShowDialogEvent.SHOW_CONFIRM_ORDER_DIALOG, self.__showFortOrderConfirmationWindow)], EVENT_BUS_SCOPE.DEFAULT)

    def __showFortOrderConfirmationWindow(self, event):
        self._loadView(FORTIFICATION_ALIASES.FORT_ORDER_CONFIRMATION_WINDOW_ALIAS, event.meta, event.handler)
