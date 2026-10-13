# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/hangar/halloween_browser.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebViewTransparent
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import ABOUT_GAME_MODE_ENTER, ABOUT_GAME_MODE_EXIT
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys, HWLogActions

class HalloweenBrowser(WebViewTransparent):

    def __init__(self, ctx=None):
        super(HalloweenBrowser, self).__init__(ctx)
        playSound(ABOUT_GAME_MODE_ENTER)
        self.__uiLogger = HWMetricsLogger(HWLogKeys.HW_WEB_VIEW)

    def _populate(self):
        super(HalloweenBrowser, self)._populate()
        self.__uiLogger.onStartView(HWLogActions.LIFETIME)

    def _dispose(self):
        playSound(ABOUT_GAME_MODE_EXIT)
        self.__uiLogger.onStopView(HWLogActions.LIFETIME, self._url)
        super(HalloweenBrowser, self)._dispose()
