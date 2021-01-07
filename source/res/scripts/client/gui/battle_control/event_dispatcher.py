# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/event_dispatcher.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.avatar_getter import isVehicleAlive
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent, LoadViewEvent
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_SCOPE = EVENT_BUS_SCOPE.BATTLE

def _makeKeyCtx(key=0, isDown=False):
    return {'key': key,
     'isDown': isDown}


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def _killHelpView(appLoader=None):
    battleApp = appLoader.getDefBattleApp()
    if battleApp is None:
        return False
    else:
        for alias in (VIEW_ALIAS.INGAME_HELP, VIEW_ALIAS.INGAME_DETAILS_HELP):
            view = battleApp.containerManager.getViewByKey(ViewKey(alias))
            if view is not None:
                view.destroy()
                return True

        return False


def showExtendedInfo(isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.SHOW_EXTENDED_INFO, _makeKeyCtx(isDown=isDown)), scope=_SCOPE)


def choiceConsumable(key):
    g_eventBus.handleEvent(GameEvent(GameEvent.CHOICE_CONSUMABLE, _makeKeyCtx(key=key)), scope=_SCOPE)


def toggleHelp():
    if _killHelpView():
        return
    g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.INGAME_HELP)), scope=_SCOPE)


def toggleHelpDetailed(ctx):
    if _killHelpView():
        return
    g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.INGAME_DETAILS_HELP), ctx=ctx), scope=_SCOPE)


def setMinimapCmd(key):
    g_eventBus.handleEvent(GameEvent(GameEvent.MINIMAP_CMD, _makeKeyCtx(key=key)), scope=_SCOPE)


def setRadialMenuCmd(key, isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.RADIAL_MENU_CMD, _makeKeyCtx(key=key, isDown=isDown)), scope=_SCOPE)


def setRespondToCalloutCmd(key, isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.RESPOND_TO_CALLOUT, _makeKeyCtx(key=key, isDown=isDown)), scope=_SCOPE)


def toggleGUIVisibility():
    g_eventBus.handleEvent(GameEvent(GameEvent.TOGGLE_GUI), scope=_SCOPE)


def setPlayingTimeOnArena(playingTime):
    g_eventBus.handleEvent(GameEvent(GameEvent.PLAYING_TIME_ON_ARENA, {'time': playingTime}), scope=_SCOPE)


def showIngameMenu():
    g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.INGAME_MENU)), scope=_SCOPE)


def showBattleVehicleConfigurator():
    if isVehicleAlive():
        g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_CONFIGURATOR)), scope=_SCOPE)


def hideBattleVehicleConfigurator():
    g_eventBus.handleEvent(GameEvent(GameEvent.HIDE_VEHICLE_UPGRADE), scope=_SCOPE)


def toggleFullStats(isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.FULL_STATS, _makeKeyCtx(isDown=isDown)), scope=_SCOPE)


def toggleEventStats(isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.EVENT_STATS, _makeKeyCtx(isDown=isDown)), scope=_SCOPE)


def toggleFullStatsQuestProgress(isDown):
    g_eventBus.handleEvent(GameEvent(GameEvent.FULL_STATS_QUEST_PROGRESS, _makeKeyCtx(isDown=isDown)), scope=_SCOPE)


def toggleVoipChannelEnabled():
    g_eventBus.handleEvent(GameEvent(GameEvent.TOGGLE_VOIP_CHANNEL_ENABLED), scope=_SCOPE)


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


def hideAutoAimMarker():
    g_eventBus.handleEvent(GameEvent(GameEvent.HIDE_AUTO_AIM_MARKER), scope=_SCOPE)


def addAutoAimMarker(vehicle):
    g_eventBus.handleEvent(GameEvent(GameEvent.ADD_AUTO_AIM_MARKER, {'vehicle': vehicle}), scope=_SCOPE)


def chargeReleased(keyDown=False):
    g_eventBus.handleEvent(GameEvent(GameEvent.CHARGE_RELEASED, {'keyDown': keyDown}), scope=_SCOPE)


def destroyTimersPanelShown(shown=None):
    g_eventBus.handleEvent(GameEvent(GameEvent.DESTROY_TIMERS_PANEL, {'shown': shown}), scope=_SCOPE)


def dualGunPreCharge():
    g_eventBus.handleEvent(GameEvent(GameEvent.PRE_CHARGE), scope=_SCOPE)


def controlModeChange(mode):
    g_eventBus.handleEvent(GameEvent(GameEvent.CONTROL_MODE_CHANGE, {'mode': mode}), scope=_SCOPE)


def sniperCameraTransition(transitionTime, currentGunIndex):
    g_eventBus.handleEvent(GameEvent(GameEvent.SNIPER_CAMERA_TRANSITION, {'transitionTime': transitionTime,
     'currentGunIndex': currentGunIndex}), scope=_SCOPE)
