# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanProfileStrongholdsViewMeta.py
from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileBaseView import ClanProfileBaseView

class ClanProfileStrongholdsViewMeta(ClanProfileBaseView):

    def as_showBodyDummyS(self, data):
        return self.flashObject.as_showBodyDummy(data) if self._isDAAPIInited() else None

    def as_hideBodyDummyS(self):
        return self.flashObject.as_hideBodyDummy() if self._isDAAPIInited() else None
