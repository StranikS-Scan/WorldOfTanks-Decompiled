# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_views_helpers.py
import logging
from collections import namedtuple
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showBrowserOverlayView, showBundlePurchaseDialog
from helpers import time_utils
_logger = logging.getLogger(__name__)
NyExecuteCtx = namedtuple('NyExecuteCtx', ('action', 'args', 'kwargs'))
_EXECUTE_ACTIONS = {'showBundlePurchaseDialog': showBundlePurchaseDialog}

def getTimerGameDayLeft():
    return time_utils.getDayTimeLeft() + 1


def showInfoVideo():
    url = GUI_SETTINGS.newYearInfo.get('baseURL')
    if url is None:
        _logger.error('newYearInfo.baseURL is missed')
    showBrowserOverlayView(url, alias=VIEW_ALIAS.NY_BROWSER_VIEW)
    return


_MARKETPLACE_BONUSES_ORDER = ({'getName': 'customizations',
  'getIcon': 'style'}, {'getName': 'customizations',
  'getIcon': 'projectionDecal'})

def marketPlaceKeySortOrder(bonus, _):
    for index, criteria in enumerate(_MARKETPLACE_BONUSES_ORDER):
        for method, value in criteria.items():
            if not hasattr(bonus, method) or value not in getattr(bonus, method)():
                break
        else:
            return index

    return len(_MARKETPLACE_BONUSES_ORDER)


def executeContext(context):
    if not isinstance(context, NyExecuteCtx):
        if callable(context):
            context()
        return
    action = _EXECUTE_ACTIONS.get(context.action)
    if action:
        action(*context.args, **context.kwargs)
