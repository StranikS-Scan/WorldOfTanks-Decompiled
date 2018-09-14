# Embedded file name: scripts/client/messenger/gui/Scaleform/data/MembersDataProvider.py
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
        getColors = g_settings.getColorScheme('rosters').getColors
        for member in members:
            dbID = member.getID()
            isOnline = member.isOnline()
            user = getUser(dbID)
            if user:
                tags = list(user.getTags())
                colors = getColors(user.getGuiType())
            else:
                tags = []
                colors = getColors(USER_GUI_TYPE.OTHER)
            self.__list.append({'dbID': dbID,
             'userName': member.getFullName(),
             'isOnline': isOnline,
             'color': colors[0 if isOnline else 1],
             'tags': tags,
             'isPlayerSpeaking': False})

    def emptyItem(self):
        return {'dbID': 0,
         'userName': '',
         'isOnline': False,
         'color': 0,
         'tags': [],
         'isPlayerSpeaking': False}
