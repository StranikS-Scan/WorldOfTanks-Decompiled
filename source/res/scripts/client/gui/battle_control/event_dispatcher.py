# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/event_dispatcher.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent, LoadViewEvent
_SCOPE = EVENT_BUS_SCOPE.BATTLE

def _makeKeyCtx(key=0, isDown=False):
    return {'key': key,
     'isDown': isDown}


def showExtendedInfo(isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.SHOW_EXTENDED_INFO, _makeKeyCtx(isDown=isDown)), scope=_SCOPE)


def choiceConsumable(key):
    g_eventBus.handleEvent(GameEvent(GameEvent.CHOICE_CONSUMABLE, _makeKeyCtx(key=key)), scope=_SCOPE)


def toggleHelp():
    g_eventBus.handleEvent(GameEvent(GameEvent.HELP), scope=_SCOPE)


def setMinimapCmd(key):
    g_eventBus.handleEvent(GameEvent(GameEvent.MINIMAP_CMD, _makeKeyCtx(key=key)), scope=_SCOPE)


def setRadialMenuCmd(key, isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.RADIAL_MENU_CMD, _makeKeyCtx(key=key, isDown=isDown)), scope=_SCOPE)


def toggleGUIVisibility():
    g_eventBus.handleEvent(GameEvent(GameEvent.TOGGLE_GUI), scope=_SCOPE)


def setPlayingTimeOnArena(playingTime):
    g_eventBus.handleEvent(GameEvent(GameEvent.PLAYING_TIME_ON_ARENA, {'time': playingTime}), scope=_SCOPE)


def showIngameMenu():
    g_eventBus.handleEvent(LoadViewEvent(VIEW_ALIAS.INGAME_MENU), scope=_SCOPE)


def toggleFullStats(isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.FULL_STATS, _makeKeyCtx(isDown=isDown)), scope=_SCOPE)


def setNextPlayerPanelMode():
    g_eventBus.handleEvent(GameEvent(GameEvent.NEXT_PLAYERS_PANEL_MODE), scope=_SCOPE)


def toggleMarkers2DVisibility():
    g_eventBus.handleEvent(GameEvent(GameEvent.MARKERS_2D_VISIBILITY), scope=_SCOPE)


def toggleCrosshairVisibility():
    g_eventBus.handleEvent(GameEvent(GameEvent.CROSSHAIR_VISIBILITY), scope=_SCOPE)


def toggleGunMarkerVisibility():
    g_eventBus.handleEvent(GameEvent(GameEvent.GUN_MARKER_VISIBILITY), scope=_SCOPE)


def overrideCrosshairView(newMode):
    g_eventBus.handleEvent(GameEvent(GameEvent.CROSSHAIR_VIEW, {'ctrlMode': newMode}), scope=_SCOPE)
