# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileFortificationView.py
from adisp import process
from debug_utils import LOG_DEBUG
from gui.clans import formatters as clans_fmts
from gui.Scaleform.daapi.view.lobby.clans.profile import fort_data_receivers
from gui.Scaleform.daapi.view.meta.ClanProfileFortificationViewMeta import ClanProfileFortificationViewMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.fortifications.fort_listener import FortListener
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from helpers import i18n

class ClanProfileFortificationView(ClanProfileFortificationViewMeta, FortListener):

    def __init__(self):
        super(ClanProfileFortificationView, self).__init__()
        self._fortDP = None
        return

    @property
    def fortDP(self):
        """
        Current fort data provider.
        Expose it to dependant views (ClanProfileFortificationInfoView, ClanProfileFortificationPromoView),
        since it can be changed if our belonging to clan changes and we can not set-and-forget it
        """
        return self._fortDP

    def setClanDossier(self, clanDossier):
        super(ClanProfileFortificationView, self).setClanDossier(clanDossier)
        self.__updateView()

    def showWaiting(self):
        self._showWaiting()

    def hideWaiting(self):
        self._hideWaiting()

    def isShowDataBlocked(self):
        return self.fortState.getStateID() in CLIENT_FORT_STATE.NOT_AVAILABLE_FORT

    def onClientStateChanged(self, state):
        self.__updateView()
        for view in self.components.itervalues():
            view.updateData()

    def _populate(self):
        super(ClanProfileFortificationView, self)._populate()
        self.startFortListening()

    def _dispose(self):
        self._fortDP = None
        self.stopFortListening()
        super(ClanProfileFortificationView, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in (CLANS_ALIASES.CLAN_PROFILE_FORT_INFO_VIEW_ALIAS, CLANS_ALIASES.CLAN_PROFILE_FORT_PROMO_VIEW_ALIAS):
            viewPy.setProxy(self, self._clanDossier)

    @process
    def __updateView(self):
        self._showWaiting()
        clanInfo = yield self._clanDossier.requestClanInfo()
        if not clanInfo.isValid():
            self._dummyMustBeShown = True
            self._updateDummy()
            self._hideWaiting()
            return
        else:
            clsSelector = {True: fort_data_receivers.OwnClanDataReceiver,
             False: fort_data_receivers.ClanDataReceiver}
            isMyClan = self._clanDossier.isMyClan()
            receiverCls = clsSelector[isMyClan]
            if type(self._fortDP) != receiverCls:
                if self._fortDP is not None:
                    LOG_DEBUG('Replacing Fort DP', type(self._fortDP), receiverCls)
                self._fortDP = receiverCls()
            hasFort = yield self._fortDP.hasFort(self._clanDossier)
            if self.isDisposed():
                return
            self._updateClanInfo(clanInfo)
            if hasFort:
                self.__linkage = CLANS_ALIASES.CLAN_PROFILE_FORT_INFO_VIEW_LINKAGE
            else:
                self.__linkage = CLANS_ALIASES.CLAN_PROFILE_FORT_PROMO_VIEW_LINKAGE
            if self.isShowDataBlocked():
                self.__showDummyBody()
                self._hideWaiting()
                return
            self._updateHeaderState()
            self.as_setDataS(self.__linkage)
            self._hideWaiting()
            return

    def __showDummyBody(self):
        self.as_showBodyDummyS({'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
         'htmlText': str().join((text_styles.middleTitle(i18n.makeString(CLANS.CLANPROFILE_FORTIFICATIONINFO_DUMMY_HEADER)), clans_fmts.getHtmlLineDivider(3), text_styles.main(i18n.makeString(CLANS.CLANPROFILE_FORTIFICATIONINFO_DUMMY_BODY)))),
         'alignCenter': False,
         'btnVisible': False,
         'btnLabel': '',
         'btnTooltip': ''})
