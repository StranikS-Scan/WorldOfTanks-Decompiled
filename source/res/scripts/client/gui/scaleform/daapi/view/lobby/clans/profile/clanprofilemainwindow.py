# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileMainWindow.py
import weakref
from gui.Scaleform.daapi.view.lobby.clans.clan_profile_event import ClanProfileEvent
from gui.clans.clan_helpers import ClanListener
from gui.Scaleform.daapi.view.lobby.clans.profile.ClanProfileBaseView import ClanProfileBaseView
from gui.Scaleform.daapi.view.meta.ClanProfileMainWindowMeta import ClanProfileMainWindowMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.WAITING import WAITING
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import i18n

class ClanProfileMainWindow(ClanProfileMainWindowMeta, ClanListener):

    def __init__(self, ctx):
        super(ClanProfileMainWindow, self).__init__()
        self.__clanDBID = ctx['clanDbID']
        self.__clanDossier = None
        self.__clanAbbrev = ctx['clanAbbrev']
        return

    def onWindowClose(self):
        self.destroy()

    def getClanDossier(self):
        return self.__clanDossier

    def onClanEnableChanged(self, enabled):
        if not enabled:
            self.onWindowClose()

    def _populate(self):
        super(ClanProfileMainWindow, self)._populate()
        self.addListener(ClanProfileEvent.CLOSE_CLAN_PROFILE, self.__closeClanProfileHandler, scope=EVENT_BUS_SCOPE.LOBBY)
        self.startClanListening()
        self.webCtrl.getAccountProfile().resync()
        self.__clanDossier = weakref.proxy(self.webCtrl.getClanDossier(self.__clanDBID))
        self.as_setDataS({'waitingMsg': WAITING.LOADINGDATA,
         'tabDataProvider': [{'label': CLANS.CLANPROFILE_MAINWINDOWTAB_SUMMARY,
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_SUMMARY_VIEW_LINKAGE},
                             {'label': CLANS.CLANPROFILE_MAINWINDOWTAB_PERSONNEL,
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_PERSONNEL_VIEW_LINKAGE},
                             {'label': CLANS.CLANPROFILE_MAINWINDOWTAB_STRONGHOLDS,
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_STRONGHOLDS_VIEW_LINKAGE},
                             {'label': CLANS.CLANPROFILE_MAINWINDOWTAB_GLOBALMAP,
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_GLOBALMAP_VIEW_LINKAGE}]})
        self.as_setWindowTitleS(''.join((i18n.makeString(CLANS.CLANPROFILE_MAINWINDOW_TITLE),
         ' [',
         self.__clanAbbrev,
         ']')))

    def _dispose(self):
        self.stopClanListening()
        self.__clanDossier = None
        self.removeListener(ClanProfileEvent.CLOSE_CLAN_PROFILE, self.__closeClanProfileHandler, scope=EVENT_BUS_SCOPE.LOBBY)
        super(ClanProfileMainWindow, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ClanProfileMainWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, ClanProfileBaseView):
            viewPy.setClanDossier(self.__clanDossier)

    def __closeClanProfileHandler(self, _):
        self.destroy()
