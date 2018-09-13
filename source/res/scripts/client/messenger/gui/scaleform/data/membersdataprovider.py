# Embedded file name: scripts/client/messenger/gui/Scaleform/data/MembersDataProvider.py
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter

class MembersDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(MembersDataProvider, self).__init__()
        self.__list = []

    @property
    def collection(self):
        return self.__list

    @storage_getter('users')
    def usersStorage(self):
        return None

    def buildList(self, members):
        self.__list = []
        members = sorted(members, key=lambda member: member.getName().lower())
        getUser = self.usersStorage.getUser
        getColor = g_settings.getColorScheme('rosters').getColor
        for member in members:
            dbID = member.getID()
            user = getUser(dbID)
            if user:
                roster = user.getRoster()
                himself = user.isCurrentPlayer()
                color = getColor(user.getGuiType())
            else:
                roster = 0
                himself = False
                color = getColor(USER_GUI_TYPE.OTHER)
            self.__list.append({'uid': dbID,
             'userName': member.getFullName(),
             'color': color,
             'chatRoster': roster,
             'himself': himself,
             'isPlayerSpeaking': False})

    def emptyItem(self):
        return {'uid': 0,
         'userName': '',
         'color': 0,
         'chatRoster': 0,
         'himself': False,
         'isPlayerSpeaking': False}
