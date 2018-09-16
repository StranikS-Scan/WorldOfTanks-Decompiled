# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/browser_filters.py
from collections import namedtuple
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import g_entitiesFactories
from gui.shared import g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import OpenLinkEvent

def getFilters():
    return {_onShowInExternalBrowser,
     _onGoToHangar,
     _onGoToMissions,
     _onGoToPersonalMissions}


BrowserFilterResult = namedtuple('BrowserFilterResult', 'stopNavigation closeBrowser')
BrowserFilterResult.__new__.__defaults__ = (False, False)

def _onShowInExternalBrowser(url, tags):
    if 'external' in tags:
        LOG_DEBUG('Browser url has been processed', url)
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, url))
        return BrowserFilterResult(stopNavigation=True)
    return BrowserFilterResult()


def _onGoToHangar(url, tags):
    if 'go_to_hangar' in tags:
        LOG_DEBUG('Browser url has been processed: going to hangar. Url: ', url)
        g_eventBus.handleEvent(g_entitiesFactories.makeLoadEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        return BrowserFilterResult(stopNavigation=True)
    return BrowserFilterResult()


def _onGoToMissions(url, tags):
    if 'go_to_missions' in tags:
        LOG_DEBUG('Browser url has been processed: going to missions. Url: ', url)
        g_eventBus.handleEvent(g_entitiesFactories.makeLoadEvent(VIEW_ALIAS.LOBBY_MISSIONS), scope=EVENT_BUS_SCOPE.LOBBY)
        return BrowserFilterResult(stopNavigation=True, closeBrowser=True)
    return BrowserFilterResult()


def _onGoToPersonalMissions(url, tags):
    if 'go_to_campaigns' in tags:
        LOG_DEBUG('Browser url has been processed: going to personal missions. Url: ', url)
        g_eventBus.handleEvent(g_entitiesFactories.makeLoadEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS), scope=EVENT_BUS_SCOPE.LOBBY)
        return BrowserFilterResult(stopNavigation=True, closeBrowser=True)
    return BrowserFilterResult()
