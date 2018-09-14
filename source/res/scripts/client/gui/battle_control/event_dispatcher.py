# Embedded file name: scripts/client/gui/battle_control/event_dispatcher.py
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
_SCOPE = EVENT_BUS_SCOPE.BATTLE

def _makeKeyCtx(key = 0, isDown = False):
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


def setRadialMenuCmd(key, isDown, offset):
    ctx = _makeKeyCtx(key=key, isDown=isDown)
    ctx['offset'] = offset
    g_eventBus.handleEvent(GameEvent(GameEvent.RADIAL_MENU_CMD, ctx), scope=_SCOPE)


def setGUIVisibility(flag):
    g_eventBus.handleEvent(GameEvent(GameEvent.GUI_VISIBILITY, {'visible': flag}), scope=_SCOPE)


def showGUICursor():
    g_eventBus.handleEvent(GameEvent(GameEvent.SHOW_CURSOR), scope=_SCOPE)


def hideGUICursor():
    g_eventBus.handleEvent(GameEvent(GameEvent.HIDE_CURSOR), scope=_SCOPE)


def setPlayingTimeOnArena(playingTime):
    g_eventBus.handleEvent(GameEvent(GameEvent.PLAYING_TIME_ON_ARENA, {'time': playingTime}), scope=_SCOPE)
