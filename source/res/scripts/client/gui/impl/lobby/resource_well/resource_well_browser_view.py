# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/resource_well_browser_view.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.sounds.filters import switchHangarFilteredFilter

class ResourceWellBrowserView(WebView):

    def _populate(self):
        super(ResourceWellBrowserView, self)._populate()
        switchHangarFilteredFilter(on=True)

    def _dispose(self):
        switchHangarFilteredFilter(on=False)
        super(ResourceWellBrowserView, self)._dispose()
