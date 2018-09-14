# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
from gui.shared import events, g_eventBus
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName, getUniqueViewName
from gui.battle_results import data_providers
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES

def _showBattleResults(arenaUniqueID, dataProvider):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BATTLE_RESULTS, getViewName(VIEW_ALIAS.BATTLE_RESULTS, str(arenaUniqueID)), ctx={'dataProvider': dataProvider}))


def showBattleResultsFromData(battleResultsData):
    arenaUniqueID = battleResultsData['arenaUniqueID']
    return _showBattleResults(arenaUniqueID, data_providers.DirectDataProvider(arenaUniqueID, battleResultsData))


def showMyBattleResults(arenaUniqueID):
    return _showBattleResults(arenaUniqueID, data_providers.OwnResultsDataProvider(arenaUniqueID))


def showUserBattleResults(arenaUniqueID, svrPackedData):
    return _showBattleResults(arenaUniqueID, data_providers.UserResultsDataProvider(arenaUniqueID, svrPackedData))


def showVehicleInfo(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_INFO_WINDOW, getViewName(VIEW_ALIAS.VEHICLE_INFO_WINDOW, vehTypeCompDescr), ctx={'vehicleCompactDescr': int(vehTypeCompDescr)}))


def showModuleInfo(itemCD, vehicleDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, itemCD), {'moduleCompactDescr': itemCD,
     'vehicleDescr': vehicleDescr}))


def showVehicleSellDialog(vehInvID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_SELL_DIALOG, ctx={'vehInvID': int(vehInvID)}))


def showVehicleBuyDialog(vehicle):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_BUY_WINDOW, ctx={'nationID': vehicle.nationID,
     'itemID': vehicle.innationID}))


def showResearchView(vehTypeCompDescr):
    exitEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR)
    loadEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_RESEARCH, ctx={'rootCD': vehTypeCompDescr,
     'exit': exitEvent})
    g_eventBus.handleEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleStats(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PROFILE, ctx={'itemCD': vehTypeCompDescr}), scope=EVENT_BUS_SCOPE.LOBBY)


def showHangar():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)


def showAwardWindow(award, isUniqueName = True):
    if isUniqueName:
        name = getUniqueViewName(VIEW_ALIAS.AWARD_WINDOW)
    else:
        name = VIEW_ALIAS.AWARD_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.AWARD_WINDOW, name=name, ctx={'award': award}))


def showProfileWindow(databaseID, userName):
    alias = VIEW_ALIAS.PROFILE_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(alias, getViewName(alias, databaseID), ctx={'userName': userName,
     'databaseID': databaseID}), EVENT_BUS_SCOPE.LOBBY)


def showClanProfileWindow(userID):
    pass


def selectVehicleInHangar(itemCD):
    from CurrentVehicle import g_currentVehicle
    veh = g_itemsCache.items.getItemByCD(int(itemCD))
    raise veh.isInInventory or AssertionError('Vehicle must be in inventory.')
    g_currentVehicle.selectVehicle(veh.invID)
    showHangar()


def showPersonalCase(tankmanInvID, tabIndex):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.PERSONAL_CASE, getViewName(VIEW_ALIAS.PERSONAL_CASE, tankmanInvID), {'tankmanID': tankmanInvID,
     'page': tabIndex}))


def showPremiumCongratulationWindow(award):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.PREMIUM_CONGRATULATION_WINDOW, getViewName(VIEW_ALIAS.PREMIUM_CONGRATULATION_WINDOW), ctx={'award': award}))


def showPremiumWindow(arenaUniqueID = 0):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.PREMIUM_WINDOW, getViewName(VIEW_ALIAS.PREMIUM_WINDOW), ctx={'arenaUniqueID': arenaUniqueID}))


def showBoostersWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTERS_WINDOW))


def showChangeDivisionWindow(division):
    g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW, ctx={'isInChangeDivisionMode': True,
     'division': division}), scope=EVENT_BUS_SCOPE.LOBBY)
