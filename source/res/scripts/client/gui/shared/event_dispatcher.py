# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
from debug_utils import LOG_DEBUG
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName, getUniqueViewName
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

def showBattleResults(arenaUniqueID, data = None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BATTLE_RESULTS, getViewName(VIEW_ALIAS.BATTLE_RESULTS, arenaUniqueID), ctx={'data': arenaUniqueID,
     'battleResults': data}))


def showVehicleInfo(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_INFO_WINDOW, getViewName(VIEW_ALIAS.VEHICLE_INFO_WINDOW, vehTypeCompDescr), ctx={'vehicleCompactDescr': int(vehTypeCompDescr)}))


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


def showAwardWindow(award):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.AWARD_WINDOW, name=getUniqueViewName(VIEW_ALIAS.AWARD_WINDOW), ctx={'award': award}))
