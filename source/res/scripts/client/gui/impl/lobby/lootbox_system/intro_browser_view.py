# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/intro_browser_view.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.sounds.filters import switchHangarOverlaySoundFilter

class LootBoxSystemIntroBrowserView(WebView):

    def _populate(self):
        super(LootBoxSystemIntroBrowserView, self)._populate()
        switchHangarOverlaySoundFilter(on=True)

    def _dispose(self):
        switchHangarOverlaySoundFilter(on=False)
        super(LootBoxSystemIntroBrowserView, self)._dispose()
