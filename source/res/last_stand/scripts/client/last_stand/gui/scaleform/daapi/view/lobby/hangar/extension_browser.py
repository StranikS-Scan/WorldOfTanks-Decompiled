# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/hangar/extension_browser.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebViewTransparent
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import ABOUT_GAME_MODE_ENTER, ABOUT_GAME_MODE_EXIT

class ExtensionBrowser(WebViewTransparent):

    def __init__(self, ctx=None):
        super(ExtensionBrowser, self).__init__(ctx)
        playSound(ABOUT_GAME_MODE_ENTER)

    def _dispose(self):
        playSound(ABOUT_GAME_MODE_EXIT)
        super(ExtensionBrowser, self)._dispose()
