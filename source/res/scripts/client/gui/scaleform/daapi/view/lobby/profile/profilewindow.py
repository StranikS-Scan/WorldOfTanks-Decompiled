# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileWindow.py
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.ProfileWindowMeta import ProfileWindowMeta
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import getProfileCommonInfo
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.PROFILE import PROFILE
from helpers.i18n import makeString
from gui.shared import g_itemsCache
from PlayerEvents import g_playerEvents
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from gui import game_control

class ProfileWindow(ProfileWindowMeta, AbstractWindowView, View, AppRef):

    def __init__(self, ctx = None):
        super(ProfileWindow, self).__init__()
        self.__userName = ctx.get('userName')
        self.__databaseID = ctx.get('databaseID')

    def _populate(self):
        super(ProfileWindow, self)._populate()
        g_playerEvents.onDossiersResync += self.__dossierResyncHandler
        self.__updateUserInfo()
        g_messengerEvents.users.onUserActionReceived += self._onUserActionReceived
        self.__checkUserRosterInfo()

    def _dispose(self):
        g_messengerEvents.users.onUserActionReceived -= self._onUserActionReceived
        g_playerEvents.onDossiersResync -= self.__dossierResyncHandler
        g_itemsCache.items.unloadUserDossier(self.__databaseID)
        super(ProfileWindow, self)._dispose()

    def __checkUserRosterInfo(self):
        user = self.usersStorage.getUser(self.__databaseID)
        enabledInroaming = self.__isEnabledInRoaming(self.__databaseID)
        isFriend = user is not None and user.isFriend()
        self.as_addFriendAvailableS(enabledInroaming and not isFriend)
        isIgnored = user is not None and user.isIgnored()
        self.as_setIgnoredAvailableS(enabledInroaming and not isIgnored)
        self.as_setCreateChannelAvailableS(enabledInroaming and not isIgnored)
        return

    def __isEnabledInRoaming(self, dbID):
        roamingCtrl = game_control.g_instance.roaming
        if g_settings.server.XMPP.isEnabled():
            isEnabled = roamingCtrl.isSameRealm(dbID)
        else:
            isEnabled = not roamingCtrl.isInRoaming() and not roamingCtrl.isPlayerInRoaming(dbID)
        return isEnabled

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def _onUserActionReceived(self, _, user):
        if user.getID() == self.__databaseID:
            self.__checkUserRosterInfo()

    def __dossierResyncHandler(self, *args):
        self.__updateUserInfo()

    def __updateUserInfo(self):
        dossier = g_itemsCache.items.getAccountDossier(self.__databaseID)
        clanDBID, clanInfo = g_itemsCache.items.getClanInfo(self.__databaseID)
        info = getProfileCommonInfo(self.__userName, dossier.getDossierDescr(), clanInfo, None)
        self.as_setInitDataS({'fullName': g_lobbyContext.getPlayerFullName(info['name'], clanAbbrev=info['clanName'], regionCode=g_lobbyContext.getRegionCode(self.__databaseID))})
        return

    def registerFlashComponent(self, component, alias, *args):
        if alias == VIEW_ALIAS.PROFILE_TAB_NAVIGATOR:
            super(ProfileWindow, self).registerFlashComponent(component, alias, self.__userName, self.__databaseID, self.__databaseID, {'sectionsData': [self.__getSectionDataObject(PROFILE.SECTION_SUMMARY_TITLE, PROFILE.PROFILE_TABS_TOOLTIP_SUMMARY, VIEW_ALIAS.PROFILE_SUMMARY_WINDOW),
                              self.__getSectionDataObject(PROFILE.SECTION_AWARDS_TITLE, PROFILE.PROFILE_TABS_TOOLTIP_AWARDS, VIEW_ALIAS.PROFILE_AWARDS),
                              self.__getSectionDataObject(PROFILE.SECTION_STATISTICS_TITLE, PROFILE.PROFILE_TABS_TOOLTIP_STATISTICS, VIEW_ALIAS.PROFILE_STATISTICS),
                              self.__getSectionDataObject(PROFILE.SECTION_TECHNIQUE_TITLE, PROFILE.PROFILE_TABS_TOOLTIP_TECHNIQUE, VIEW_ALIAS.PROFILE_TECHNIQUE_WINDOW)]})
        else:
            super(ProfileWindow, self).registerFlashComponent(component, alias)

    def __getSectionDataObject(self, label, tooltip, alias):
        return {'label': makeString(label),
         'alias': alias,
         'tooltip': tooltip}

    def userAddFriend(self):
        self.proto.contacts.addFriend(self.__databaseID, self.__userName)

    def userSetIgnored(self):
        self.proto.contacts.addIgnored(self.__databaseID, self.__userName)

    def userCreatePrivateChannel(self):
        self.proto.contacts.createPrivateChannel(self.__databaseID, self.__userName)

    def onWindowClose(self):
        self.destroy()
