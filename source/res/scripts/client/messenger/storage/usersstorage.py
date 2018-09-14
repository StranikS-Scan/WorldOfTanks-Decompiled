# Embedded file name: scripts/client/messenger/storage/UsersStorage.py
from collections import deque, defaultdict
import types
from debug_utils import LOG_ERROR
from messenger.m_constants import USER_GUI_TYPE, BREAKERS_MAX_LENGTH, USER_TAG
from messenger.storage.local_cache import RevCachedStorage

class UsersStorage(RevCachedStorage):
    __slots__ = ('__contacts', '__emptyGroups', '__openedGroups', '__clanMembersIDs', '__breakers')

    def __init__(self):
        super(UsersStorage, self).__init__()
        self.__contacts = {}
        self.__emptyGroups = set()
        self.__openedGroups = {}
        self.__clanMembersIDs = set()
        self.__breakers = deque([], BREAKERS_MAX_LENGTH)

    def __repr__(self):
        return 'UsersStorage(id=0x{0:08X}, len={1:n})'.format(id(self), len(self.__contacts))

    def clear(self):
        self.__clanMembersIDs.clear()
        self.__breakers.clear()
        self.__emptyGroups.clear()
        self.__openedGroups = {}
        while len(self.__contacts):
            _, user = self.__contacts.popitem()
            user.clear()

        super(UsersStorage, self).clear()

    def all(self):
        return self.__contacts.values()

    def addUser(self, user):
        dbID = user.getID()
        if dbID not in self.__contacts:
            self.__contacts[dbID] = user
        else:
            LOG_ERROR('User exists in storage', user)

    def setUser(self, user):
        dbID = user.getID()
        if dbID not in self.__contacts:
            self.__contacts[dbID] = user
        else:
            exists = self.__contacts[dbID]
            if exists.isCurrentPlayer():
                return
            if not user.setSharedProps(exists):
                LOG_ERROR('User entity can not be replaced', user, exists)
                return
            self.__contacts[dbID] = user

    def getUser(self, dbID, protoType = None):
        user = None
        if dbID in self.__contacts:
            user = self.__contacts[dbID]
            if protoType is not None and not user.isCurrentPlayer() and user.getProtoType() != protoType:
                user = None
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

    def removeTags(self, tags, criteria = None):
        if criteria is None:
            users = self.__contacts.itervalues()
        else:
            users = self.getList(criteria=criteria)
        for user in users:
            if user.isCurrentPlayer():
                continue
            user.removeTags(tags)

        return

    def addEmptyGroup(self, name):
        self.__emptyGroups.add(name)

    def changeEmptyGroup(self, exclude, include = None):
        self.__emptyGroups.discard(exclude)
        if include:
            self.__emptyGroups.add(include)

    def getEmptyGroups(self):
        self._syncEmptyGroups()
        return self.__emptyGroups.copy()

    def isGroupExists(self, name):
        for contact in self.__contacts.itervalues():
            if name in contact.getGroups():
                return True

        if name in self.__emptyGroups:
            return True
        return False

    def isGroupEmpty(self, name):
        self._syncEmptyGroups()
        return name in self.__emptyGroups

    def getGroups(self):
        groups = self.__emptyGroups.copy()
        for contact in self.__contacts.itervalues():
            groups.union(contact.getGroups())

        return groups

    def getGroupsDict(self, criteria, includeEmpty = False):
        result = defaultdict(set)
        self._syncEmptyGroups()
        for contact in filter(criteria.filter, self.__contacts.itervalues()):
            groups = contact.getGroups()
            for group in groups:
                result[group].add(contact)
            else:
                result[''].add(contact)

        if includeEmpty:
            for group in self.__emptyGroups:
                if group not in result:
                    result[group] = set()

        return result

    def setOpenedGroups(self, category, name, isOpened):
        if isOpened:
            if not self.__openedGroups.get(category):
                self.__openedGroups[category] = set()
            self.__openedGroups[category].add(name)
        else:
            categorySet = self.__openedGroups.get(category, None)
            if categorySet:
                if name in categorySet:
                    categorySet.remove(name)
                if len(categorySet) == 0:
                    del self.__openedGroups[category]
        return

    def getOpenedGroups(self):
        return self.__openedGroups

    def _setClanMembersList(self, members):
        membersIDs = set()
        tags = {USER_TAG.CLAN_MEMBER}
        for member in members:
            dbID = member.getID()
            if dbID not in self.__contacts:
                self.__contacts[dbID] = member
            else:
                contact = self.__contacts[dbID]
                contact.update(name=member.getName(), clanInfo=member.getClanInfo())
                contact.addTags(tags)
            membersIDs.add(dbID)

        removed = self.__clanMembersIDs.difference(membersIDs)
        if len(removed):
            for dbID in removed:
                if dbID in self.__contacts:
                    contact = self.__contacts[dbID]
                    contact.removeTags(tags)
                    contact.update(clanInfo=None)

        self.__clanMembersIDs = membersIDs
        return

    def _markAsBreaker(self, dbID, flag):
        if flag:
            if dbID not in self.__breakers:
                self.__breakers.append(dbID)
        elif dbID in self.__breakers:
            self.__breakers.remove(dbID)

    def _clearBreakers(self):
        self.__breakers.clear()

    def _syncEmptyGroups(self):
        if not self.__emptyGroups:
            return
        for contact in self.__contacts.itervalues():
            groups = contact.getGroups()
            if groups & self.__emptyGroups:
                self.__emptyGroups = self.__emptyGroups.difference(groups)

    def _getCachedData(self):
        data = []
        if self.__emptyGroups:
            data.append(tuple(self.__emptyGroups))
        else:
            data.append(None)
        contacts = []
        for contact in self.__contacts.itervalues():
            state = contact.getPersistentState()
            if state:
                contacts.append((contact.getProtoType(), contact.getID(), state))

        if contacts:
            data.append(contacts)
        else:
            data.append(None)
        if len(self.__openedGroups) > 0:
            data.append(self.__openedGroups)
        else:
            data.append(None)
        return data

    def _setCachedData(self, record):
        result = None
        emptyGroups = record.pop(0)
        if type(emptyGroups) is types.TupleType:
            self.__emptyGroups = set(filter(lambda group: type(group) in types.StringTypes, emptyGroups))
        contacts = record.pop(0)
        if type(contacts) is types.ListType:

            def stateGenerator(requiredType):
                for item in contacts:
                    if type(item) is not types.TupleType:
                        continue
                    if len(item) != 3:
                        continue
                    protoType, dbID, state = item
                    if requiredType != protoType:
                        continue
                    yield (dbID, state)

            result = stateGenerator
        if len(record) > 0:
            self.__openedGroups = record.pop(0) or {}
        else:
            self.__openedGroups = {}
        return result

    def _getServerRevKey(self):
        return 'USERS_STORAGE_REV'
