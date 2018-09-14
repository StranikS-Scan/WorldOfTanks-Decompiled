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
        return

    def setProxy(self, proxy, clanDossier):
        self._proxy = weakref.proxy(proxy)
        self._clanDossier = clanDossier
        self.updateData()

    @process
    def updateData(self):
        yield lambda callback: callback(None)
        if self.isDisposed():
            return
        else:
            fortDP = self._proxy.fortDP
            if fortDP is not None and not self._proxy.isShowDataBlocked():
                self._proxy.showWaiting()
                data = yield fortDP.requestFort(self._clanDossier)
                self.as_setFortDataS(data)
                self._proxy.hideWaiting()
            return

    def _populate(self):
        super(ClanProfileFortificationInfoView, self)._populate()
        self.as_setDataS({'tabDataProvider': [{'label': CLANS.SECTION_FORT_BODYBAR_LABEL_SCHEME,
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_FORT_SCHEMA_VIEW_LINKAGE}, {'label': CLANS.SECTION_FORT_BODYBAR_LABEL_STATISTICS,
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_FORT_STATS_VIEW_LINKAGE}]})

    def _dispose(self):
        self._proxy = None
        self._clanDossier = None
        super(ClanProfileFortificationInfoView, self)._dispose()
        return
