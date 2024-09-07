# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/Scaleform/daapi/view/lobby/winback_browser_view.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from helpers import dependency
from skeletons.gui.game_control import IWinbackController

class WinbackBrowserView(WebView):
    __winbackController = dependency.descriptor(IWinbackController)

    def _populate(self):
        super(WinbackBrowserView, self)._populate()
        self.__winbackController.onConfigUpdated += self.__onSettingsChange

    def _dispose(self):
        super(WinbackBrowserView, self)._dispose()
        self.__winbackController.onConfigUpdated -= self.__onSettingsChange

    def __onSettingsChange(self, diff):
        if not self.__winbackController.isEnabled():
            self.destroy()
