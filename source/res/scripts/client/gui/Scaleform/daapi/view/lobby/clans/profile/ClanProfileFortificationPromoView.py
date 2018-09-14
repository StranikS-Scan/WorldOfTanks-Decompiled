# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileFortificationPromoView.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.clans.clan_profile_event import ClanProfileEvent
from gui.Scaleform.daapi.view.meta.ClanProfileFortificationPromoViewMeta import ClanProfileFortificationPromoViewMeta
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.fortifications.fort_helpers import FortListener
from gui.shared.fortifications.settings import CLIENT_FORT_STATE

class ClanProfileFortificationPromoView(ClanProfileFortificationPromoViewMeta, FortListener):

    def __init__(self):
        super(ClanProfileFortificationPromoView, self).__init__()
        self.__clanDossier = None
        self.__fortVelcomeView = None
        self.__fortDP = None
        self.__proxy = None
        return

    def setProxy(self, proxy, fortDP, clanDossier):
        self.__fortDP = fortDP
        self.__clanDossier = clanDossier
        self.__proxy = proxy
        self.__updateViewClanInfo()

    def onClientStateChanged(self, state):
        self.__updateViewClanInfo()

    def _populate(self):
        super(ClanProfileFortificationPromoView, self)._populate()
        self.startFortListening()

    def _dispose(self):
        self.__clanDossier = None
        self.__fortVelcomeView = None
        self.__fortDP = None
        self.__proxy = None
        self.stopFortListening()
        super(ClanProfileFortificationPromoView, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.FORT_WELCOME_INFO:
            self.__fortVelcomeView = viewPy
            viewPy.onFortCreationRequested += self.__fortCreationRequestedHandler
            viewPy.onFortCreationDone += self.__fortCreationDoneHandler
            self.__updateViewClanInfo()

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.FORT_WELCOME_INFO:
            viewPy.onFortCreationRequested -= self.__fortCreationRequestedHandler
            viewPy.onFortCreationDone -= self.__fortCreationDoneHandler
        super(ClanProfileFortificationPromoView, self)._onUnregisterFlashComponent(viewPy, alias)

    def __fortCreationRequestedHandler(self):
        if self.__fortDP is not None:
            self.__fortDP.createFort()
        return

    def __fortCreationDoneHandler(self):
        self.fireEvent(ClanProfileEvent(ClanProfileEvent.CLOSE_CLAN_PROFILE), EVENT_BUS_SCOPE.LOBBY)

    def __updateViewClanInfo(self):
        if self.__fortVelcomeView is not None and self.__clanDossier is not None and self.fortState.getStateID() != CLIENT_FORT_STATE.UNSUBSCRIBED:
            self.__fortVelcomeView.setMyClan(self.__clanDossier.isMyClan())
            self.__proxy.hideWaiting()
            self.stopFortListening()
        return
