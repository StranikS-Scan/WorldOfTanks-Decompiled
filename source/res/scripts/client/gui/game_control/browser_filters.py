# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/browser_filters.py
from debug_utils import LOG_DEBUG
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent

def getFilters():
    return {_onShowInExternalBrowser}


def _onShowInExternalBrowser(url, tags):
    """ Searches for custom tags 'external' and open given url in
    the external system browser. Do not return routine to the
    browser
    """
    if 'external' in tags:
        LOG_DEBUG('Browser url has been proceesed', url)
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, url))
        return True
    return False
