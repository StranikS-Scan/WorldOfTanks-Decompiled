# Embedded file name: scripts/client/messenger/storage/UsersStorage.py
from collections import deque
from debug_utils import LOG_ERROR
from messenger.m_constants import USER_GUI_TYPE, BREAKERS_MAX_LENGTH

class UsersStorage(object):
    __slots__ = ('__contacts', '__clanMembersIDs', '__breakers')

    def __init__(self):
        super(UsersStorage, self).__init__()
        self.__contacts = {}
        self.__clanMembersIDs = set()
        self.__breakers = deque([], BREAKERS_MAX_LENGTH)

    def __repr__(self):
        return 'UsersStorage(id=0x{0:08X}, len={1:n})'.format(id(self), len(self.__contacts))

    def clear(self):
        self.__clanMembersIDs.clear()
        self.__breakers.clear()
        while len(self.__contacts):
            _, user = self.__contacts.popitem()
            user.clear()

    def all(self):
        return self.__contacts.values()

    def addUser(self, user):
        dbID = user.getID()
        if dbID not in self.__contacts:
            self.__contacts[dbID] = user
        else:
            LOG_ERROR('User exists in storage', user)

    def getUser(self, dbID):
        user = None
        if dbID in self.__contacts:
            user = self.__contacts[dbID]
        return user

    def getUserGuiType(self, dbID):
        name = USER_GUI_TYPE.OTHER
        if dbID in self.__breakers:
            name = USER_GUI_TYPE.BREAKER
        elif dbID in self.__contacts:
            name = self.__contacts[dbID].getGuiType()
        return name

    def getList(self, criteria, iterator = None):
        if iterator is None:
            iterator = self.__contacts.itervalues()
        return filter(criteria.filter, iterator)

    def getCount(self, criteria, iterator = None):
        if iterator is None:
            iterator = self.__contacts.itervalues()
        return len(filter(criteria.filter, iterator))

    def getClanMembersIterator(self, exCurrent = True):
        for dbID in self.__clanMembersIDs:
            user = self.__contacts[dbID]
            if exCurrent and user.isCurrentPlayer():
                continue
            yield user

    def isClanMember(self, dbID):
        return dbID in self.__clanMembersIDs

    def _setClanMembersList(self, members):
        membersIDs = set()
        for member in members:
            dbID = member.getID()
            if dbID not in self.__contacts:
                self.__contacts[dbID] = member
            else:
                self.__contacts[dbID].update(clanMember=member)
            membersIDs.add(dbID)

        removed = self.__clanMembersIDs.difference(membersIDs)
        if len(removed):
            for dbID in removed:
                if dbID in self.__contacts:
                    self.__contacts[dbID].update(noClan=True)

        self.__clanMembersIDs = membersIDs

    def _markAsBreaker(self, dbID, flag):
        if flag:
            if dbID not in self.__breakers:
                self.__breakers.append(dbID)
        elif dbID in self.__breakers:
            self.__breakers.remove(dbID)

    def _clearBreakers(self):
        self.__breakers.clear()

    def _clearRosters(self):
        frozen = {}
        for dbID, user in self.__contacts.iteritems():
            if dbID in self.__clanMembersIDs or user.isCurrentPlayer():
                user.update(roster=0)
                frozen[dbID] = user
            else:
                user.clear()

        self.__contacts = frozen
