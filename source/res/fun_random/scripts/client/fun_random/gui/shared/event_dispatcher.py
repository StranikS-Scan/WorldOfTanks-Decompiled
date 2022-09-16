# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/event_dispatcher.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import _logger, showBrowserOverlayView
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

def showFunRandomPrimeTimeWindow():
    event = events.LoadViewEvent(SFViewLoadParams(FUNRANDOM_ALIASES.FUN_RANDOM_PRIME_TIME), ctx={})
    g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def showFunRandomInfoPage(funRandomCtrl=None):
    url = funRandomCtrl.getModeSettings().infoPageUrl
    if not url:
        _logger.error('Invalid url to open infoPage about fun random mode')
        return
    showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))
