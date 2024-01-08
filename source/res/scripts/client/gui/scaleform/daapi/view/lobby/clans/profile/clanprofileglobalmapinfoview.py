# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileGlobalMapInfoView.py
import weakref
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.clans.profile.clan_statistics_vos import FortGlobalMapStatistics
from gui.Scaleform.daapi.view.meta.ClanProfileGlobalMapInfoViewMeta import ClanProfileGlobalMapInfoViewMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.clans.data_wrapper.utils import formatField
from gui.impl import backport
from gui.shared.formatters import text_styles
from helpers import time_utils
from helpers.i18n import makeString as _ms

class ClanProfileGlobalMapInfoView(ClanProfileGlobalMapInfoViewMeta):

    def __init__(self):
        super(ClanProfileGlobalMapInfoView, self).__init__()
        self._clanDossier = None
        self._proxy = None
        return

    @adisp_process
    def setProxy(self, proxy, clanDossier):
        self._proxy = weakref.proxy(proxy)
        self._clanDossier = clanDossier
        proxy.showWaiting()
        globalMapStats = yield clanDossier.requestGlobalMapStats()
        ratings = yield clanDossier.requestClanRatings()
        favouriteAttrs = yield clanDossier.requestFavouriteAttributes()
        if self.isDisposed():
            return
        primeTime = formatField(getter=favouriteAttrs.getFavoritePrimetime, formatter=lambda x: backport.getShortTimeFormat(x.hour * time_utils.ONE_HOUR + x.minute * time_utils.ONE_MINUTE))
        primeTime = text_styles.standard(_ms(CLANS.GLOBALMAPVIEW_POPULARPRIMETIME, time=text_styles.main(primeTime)))
        data = FortGlobalMapStatistics({'stats': globalMapStats,
         'ratings': ratings,
         'favouriteAttrs': favouriteAttrs})
        data['primeTimeText'] = primeTime
        self.as_setDataS(data)
        proxy.hideWaiting()

    def _dispose(self):
        self._proxy = None
        self._clanDossier = None
        super(ClanProfileGlobalMapInfoView, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == CLANS_ALIASES.CLAN_PROFILE_TABLE_STATISTICS_VIEW_ALIAS:
            viewPy.setProxy(self._proxy, self._clanDossier)
