# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/storage/UsersStorage.py
from collections import deque, defaultdict
import types
from debug_utils import LOG_ERROR
from messenger.m_constants import USER_GUI_TYPE, BREAKERS_MAX_LENGTH, USER_TAG, MESSENGER_SCOPE
from messenger.storage.local_cache import RevCachedStorage

class UsersStorage(RevCachedStorage):
    """
    Storage contains rosters (friends, ignored, muted), clan members and breakers.
    
    It also can include 'temp' users (represented by shared user entity with USER_TAG.TEMP tag).
    Take into account that such users can be removed from the cache at any time for memory usage
    optimisation (for example, when going to battle).
    """
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
        """
        # Removes all data from storage.
        """
        self.__clanMembersIDs.clear()
        self.__breakers.clear()
        self.__emptyGroups.clear()
        self.__openedGroups = {}
        while self.__contacts:
            _, user = self.__contacts.popitem()
            user.clear()

        super(UsersStorage, self).clear()

    def switch(self, scope):
        """
        Updates storage internal state based on the given scope.
        
        :param scope: cope, see MESSENGER_SCOPE enum.
        """
        if scope == MESSENGER_SCOPE.BATTLE:
            self.reduce()
        self.init()

    def reduce(self):
        """
        Removes not critical data to reduce memory usage.
        Currently, removes all temp users (having USER_TAG.TEMP tag)
        """
        dbIDs = self.__contacts.keys()
        for dbID in dbIDs:
            user = self.__contacts[dbID]
            if USER_TAG.TEMP in user.getTags():
                self.__contacts.pop(dbID)

    def all(self):
        """
        Gets all contact list from storage.
        :return: contact list.
        """
        return self.__contacts.values()

    def addUser(self, user):
        """
        Adds user entity to the storage.
        
        :param user: an instance of UserEntity.
        """
        dbID = user.getID()
        if dbID not in self.__contacts:
            self.__contacts[dbID] = user
        else:
            LOG_ERROR('User exists in storage', user)

    def setUser(self, user):
        """
        Sets user entity to storage. If user exists than it overrides if it possible.
        
        :param user: an instance of UserEntity.
        """
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

    def getUser(self, dbID, protoType=None):
        """
        Gets user entity from storage.
        
        :param dbID: player database ID.
        :param protoType: one of PROTO_TYPE or None.
        :return: an instance of UserEntity or None.
        """
        user = None
        if dbID in self.__contacts:
            user = self.__contacts[dbID]
            if protoType is not None and not user.isCurrentPlayer() and user.getProtoType() != protoType:
                user = None
        return user

    def getUserGuiType(self, dbID):
        """
        Gets user GUI type that need to GUI logic: gets color scheme, ...
        Note: this routine wraps UserEntity.getGuiType and includes breakers.
        
        :param dbID: dbID: long containing player's database ID.
        :return: string containing one of USER_GUI_TYPE.*.
        """
        name = USER_GUI_TYPE.OTHER
        if dbID in self.__breakers:
            name = USER_GUI_TYPE.BREAKER
        elif dbID in self.__contacts:
            name = self.__contacts[dbID].getGuiType()
        return name

    def getList(self, criteria, iterator=None):
        """
        Gets list of users by given criteria.
        
        :param criteria: criteria: object that implements IEntityFindCriteria.
        :param iterator: [instance of UserEntity, ...].
        """
        if iterator is None:
            iterator = self.__contacts.itervalues()
        return filter(criteria.filter, iterator)

    def getCount(self, criteria, iterator=None):
        """
        Gets number of users by given criteria.
        
        :param criteria: object that implements IEntityFindCriteria.
        :param iterator:
        :return: number containing number of users.
        """
        if iterator is None:
            iterator = self.__contacts.itervalues()
        return len(filter(criteria.filter, iterator))

    def getClanMembersIterator(self, exCurrent=True):
        """
        Gets iterator for clan members.
        
        :param exCurrent: excludes current player from generator.
        :return: generator object.
        """
        for dbID in self.__clanMembersIDs:
            user = self.__contacts[dbID]
            if exCurrent and user.isCurrentPlayer():
                continue
            yield user

    def isClanMember(self, dbID):
        """
        Is player clan member.
        
        :param dbID: long containing player's database ID.
        :return: bool.
        """
        return dbID in self.__clanMembersIDs

    def removeTags(self, tags, criteria=None):
        """
        Removes tags from all contacts.
        
        :param tags: set of tags. @see USER_TAG.
        :param criteria: instance of find criteria or None.
        """
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
        """
        Adds empty group. If any user has that group than it removes in routine "getGroups".
        
        :param name: name of group.
        """
        self.__emptyGroups.add(name)

    def changeEmptyGroup(self, exclude, include=None):
        """
        Changes empty groups.
        
        :param exclude: name of group that is removed.
        :param include: name of group that is added or None.
        """
        self.__emptyGroups.discard(exclude)
        if include:
            self.__emptyGroups.add(include)

    def getEmptyGroups(self):
        """
        Gets set of empty groups.
        :return: set.
        """
        self._syncEmptyGroups()
        return self.__emptyGroups.copy()

    def isGroupExists(self, name):
        """
        Is group exist. Searches in contacts and empty groups.
        :param name: group name.
        :return: bool.
        """
        for contact in self.__contacts.itervalues():
            if name in contact.getGroups():
                return True

        return True if name in self.__emptyGroups else False

    def isGroupEmpty(self, name):
        """
        Is group empty.
        :param name: group name.
        :return: bool.
        """
        self._syncEmptyGroups()
        return name in self.__emptyGroups

    def getGroups(self):
        """
        Gets all groups in storage.
        
        :return: set.
        """
        groups = self.__emptyGroups.copy()
        for contact in self.__contacts.itervalues():
            groups.union(contact.getGroups())

        return groups

    def getGroupsDict(self, criteria, includeEmpty=False):
        """
        Gets dictionary where each key is group and value list of contacts.
        Note: '' indicates contacts that do not have groups.
        
        :param criteria:
        :param includeEmpty:
        :return: dict( name of group : set(contact1, contact2, ...), ... )
        """
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
                if not categorySet:
                    del self.__openedGroups[category]
        return

    def getOpenedGroups(self):
        return self.__openedGroups

    def setClanMembersList(self, members):
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
        if removed:
            for dbID in removed:
                if dbID in self.__contacts:
                    contact = self.__contacts[dbID]
                    contact.removeTags(tags)
                    contact.update(clanInfo=None)

        self.__clanMembersIDs = membersIDs
        return

    def _markAsBreaker(self, dbID, flag):
        """
        Marks user as breaker in chat.
        
        :param dbID: player database ID.
        :param flag: flag
        :return:
        """
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
        if self.__openedGroups:
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
        if record:
            self.__openedGroups = record.pop(0) or {}
        else:
            self.__openedGroups = {}
        return result

    def _getServerRevKey(self):
        pass
