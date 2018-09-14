# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileFortificationInfoView.py
import weakref
from adisp import process
from gui.Scaleform.daapi.view.meta.ClanProfileFortificationInfoViewMeta import ClanProfileFortificationInfoViewMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS

class ClanProfileFortificationInfoView(ClanProfileFortificationInfoViewMeta):

    def __init__(self):
        super(ClanProfileFortificationInfoView, self).__init__()
        self._clanDossier = None
        self._proxy = None
        self._fortDP = None
        return

    def setProxy(self, proxy, fortDP, clanDossier):
        self._proxy = weakref.proxy(proxy)
        self._clanDossier = clanDossier
        self._fortDP = fortDP
        self.updateData()

    @process
    def updateData(self):
        yield lambda callback: callback(None)
        if self.isDisposed():
            return
        if not self._proxy.isShowDataBlocked():
            self._proxy.showWaiting()
            data = yield self._fortDP.requestFort(self._clanDossier)
            self.as_setFortDataS(data)
            self._proxy.hideWaiting()

    def _populate(self):
        super(ClanProfileFortificationInfoView, self)._populate()
        self.as_setDataS({'tabDataProvider': [{'label': CLANS.SECTION_FORT_BODYBAR_LABEL_SCHEME,
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_FORT_SCHEMA_VIEW_LINKAGE}, {'label': CLANS.SECTION_FORT_BODYBAR_LABEL_STATISTICS,
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_FORT_STATS_VIEW_LINKAGE}]})

    def _dispose(self):
        self._proxy = None
        self._clanDossier = None
        self._fortDP = None
        super(ClanProfileFortificationInfoView, self)._dispose()
        return
