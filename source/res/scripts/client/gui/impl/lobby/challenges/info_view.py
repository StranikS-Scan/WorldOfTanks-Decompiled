# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/challenges/info_view.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.sounds.filters import switchHangarOverlaySoundFilter

class ChallengesInfoBrowserView(WebView):

    def _populate(self):
        super(ChallengesInfoBrowserView, self)._populate()
        switchHangarOverlaySoundFilter(on=True)

    def _dispose(self):
        super(ChallengesInfoBrowserView, self)._dispose()
        switchHangarOverlaySoundFilter(on=False)
