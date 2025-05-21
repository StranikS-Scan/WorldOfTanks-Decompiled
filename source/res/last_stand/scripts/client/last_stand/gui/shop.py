# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shop.py
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.store.browser import shop_helpers as helpers
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.game_control.links import URLMacros
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shop import Source
from last_stand.gui import ls_gui_constants
BUNDLE = 'bundle'

def _getParams(reason, price, itemId=None):
    params = {'reason': reason,
     'goldPrice': price,
     'source': Source.EXTERNAL}
    if itemId is not None:
        params['itemId'] = itemId
    return params


def showBuyGoldForBundle(fullPrice, params=None):
    params = params or {}
    params.update(_getParams(BUNDLE, fullPrice))
    showBuyGoldWebOverlay(params)


@adisp_process
def showBuyGoldWebOverlay(params=None, parent=None):
    url = helpers.getBuyMoreGoldUrl()
    if url:
        url = yield URLMacros().parse(url, params=params)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(ls_gui_constants.VIEW_ALIAS.LS_OVERLAY_WEB_STORE, parent=parent), ctx={'url': url}), EVENT_BUS_SCOPE.LOBBY)
