# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileFortificationPromoView.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.clans.clan_profile_event import ClanProfileEvent
from gui.Scaleform.daapi.view.meta.ClanProfileFortificationPromoViewMeta import ClanProfileFortificationPromoViewMeta
from gui.shared.event_bus import EVENT_BUS_SCOPE

class ClanProfileFortificationPromoView(ClanProfileFortificationPromoViewMeta):

    def __init__(self):
        super(ClanProfileFortificationPromoView, self).__init__()
        self._clanDossier = None
        self._fortDP = None
        self.proxy = None
        return

    def setProxy(self, proxy, fortDP, clanDossier):
        self._fortDP = fortDP
        self._clanDossier = clanDossier
        self.proxy = proxy

    def _dispose(self):
        self._clanDossier = None
        self._fortDP = None
        super(ClanProfileFortificationPromoView, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.FORT_WELCOME_INFO:
            viewPy.onFortCreationRequested += self.__fortCreationRequestedHandler
            viewPy.onFortCreationDone += self.__fortCreationDoneHandler
            viewPy.setMyClan(self._clanDossier.isMyClan())
            self.proxy.hideWaiting()

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.FORT_WELCOME_INFO:
            viewPy.onFortCreationRequested -= self.__fortCreationRequestedHandler
            viewPy.onFortCreationDone -= self.__fortCreationDoneHandler
        super(ClanProfileFortificationPromoView, self)._onUnregisterFlashComponent(viewPy, alias)

    def __fortCreationRequestedHandler(self):
        if self._fortDP is not None:
            self._fortDP.createFort()
        return

    def __fortCreationDoneHandler(self):
        self.fireEvent(ClanProfileEvent(ClanProfileEvent.CLOSE_CLAN_PROFILE), EVENT_BUS_SCOPE.LOBBY)
