# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_views_helpers.py
import logging
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import time_utils
_logger = logging.getLogger(__name__)

def getTimerGameDayLeft():
    return time_utils.getDayTimeLeft() + 1


def showInfoVideo():
    url = GUI_SETTINGS.newYearInfo.get('baseURL')
    if url is None:
        _logger.error('newYearInfo.baseURL is missed')
    showBrowserOverlayView(url, alias=VIEW_ALIAS.NY_BROWSER_VIEW)
    return
