# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/play_streak/play_streak_info_page.py
from frameworks.wulf import ViewFlags, WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyWindow

def showPlayStreakInfoPage(parent=None, closeCallback=None):
    from gui.impl.lobby.common.browser_view import BrowserView, makeSettings
    from web.web_client_api import webApiCollection, ui, request, sound

    def closeCallbackWrapper(*args, **kwargs):
        if closeCallback:
            closeCallback(*args, **kwargs)

    pageUrl = GUI_SETTINGS.lookup('infoPagePlayStreak')
    webHandlers = webApiCollection(request.RequestWebApi, ui.OpenWindowWebApi, ui.CloseWindowWebApi, sound.SoundWebApi, sound.HangarSoundWebApi)
    window = LobbyWindow(content=BrowserView(R.views.lobby.common.BrowserView(), makeSettings(url=pageUrl, isClosable=False, viewFlags=ViewFlags.VIEW, returnClb=closeCallbackWrapper, restoreBackground=True, webHandlers=webHandlers)), wndFlags=WindowFlags.WINDOW_FULLSCREEN, parent=parent, layer=WindowLayer.OVERLAY)
    window.load()
