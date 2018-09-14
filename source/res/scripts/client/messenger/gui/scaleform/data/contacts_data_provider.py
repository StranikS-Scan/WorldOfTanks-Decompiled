# Embedded file name: scripts/client/messenger/gui/Scaleform/data/contacts_data_provider.py
import re
import Event
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from messenger.gui.Scaleform.data import contacts_vo_converter as _vo_converter
from messenger.m_constants import USER_TAG as _TAG
from messenger.m_constants import USER_ACTION_ID as _ACTION_ID
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import UserTagsFindCriteria
from messenger.storage import storage_getter
from account_helpers.settings_core.SettingsCore import g_settingsCore

class _Category(object):
    __slots__ = ('_converter', '_visible', '_avoid', '_forced')

    def __init__(self, categoryID, forced = False):
        super(_Category, self).__init__()
        self._converter = _vo_converter.CategoryConverter(categoryID)
        self._visible = True
        self._avoid = False
        self._forced = forced

    def clear(self, full = False):
        self._avoid = False

    def getID(self):
        return self._converter.getCategoryID()

    def isVisible(self):
        return self._visible

    def setVisible(self, value):
        if value != self._visible:
            self._visible = value
            result = True
        else:
            result = False
        return result

    def isAvoid(self):
        return self._avoid

    def isEmpty(self):
        raise NotImplementedError

    def hasContacts(self):
        raise NotImplementedError

    def addContact(self, contact):
        raise NotImplementedError

    def updateContact(self, contact):
        raise NotImplementedError

    def removeContact(self, contact):
        raise NotImplementedError

    def getTags(self):
        raise NotImplementedError

    def toggleGroup(self, name):
        raise NotImplementedError

    def setGroupsMutable(self, value):
        pass

    def setOnlineMode(self, value):
        pass

    def changeGroups(self, include = None, exclude = None):
        return False

    def showEmptyItem(self, value):
        pass

    def getGroups(self, pattern = None):
        raise NotImplementedError

    def getData(self, pattern = None):
        groups = self.getGroups(pattern)
        if groups or self._forced and pattern is None:
            data = self._converter.makeVO(groups)
            self._avoid = False
        else:
            data = None
            self._avoid = True
        if data and len(data) == 1 and self.isEmpty():
            data = []
        return data

    def getContactsDict(self):
        return None

    def setAction(self, actionID, contact):
        return self.updateContact(contact)

    def setStatus(self, contact):
        return self.updateContact(contact)


class _FriendsCategory(_Category):
    __slots__ = ('_woGroup', '_groups', '__currentParent', '__showEmptyItems')

    def __init__(self):
        super(_FriendsCategory, self).__init__(CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID)
        self.__currentParent = self._converter.makeBaseVO()
        self._woGroup = _vo_converter.FriendsWoGroupConverter(self.__currentParent)
        self._groups = _vo_converter.FriendsGroupsConverter(self.__currentParent)
        self.__showEmptyItems = False

    def clear(self, full = False):
        self._woGroup.clear(full)
        self._groups.clear(full)
        super(_FriendsCategory, self).clear(full)

    def getTags(self):
        return {_TAG.FRIEND}

    def isEmpty(self):
        return self._woGroup.isEmpty() and self._groups.isEmpty()

    def hasContacts(self):
        return not self._woGroup.isEmpty() or self._groups.hasContacts()

    def toggleGroup(self, name):
        group = self._groups.getGroup(name)
        if group:
            group.toggle()
        return group is not None

    def setGroupsMutable(self, value):
        self._converter.setMutable(value)
        self._groups.setMutable(value)

    def setOnlineMode(self, value):
        if value:
            clazz = _vo_converter.OnlineOnlyCondition
        else:
            clazz = _vo_converter.OnlineTotalCondition
        self._groups.setConditionClass(clazz)
        self._woGroup.setConditionClass(clazz)

    def showEmptyItem(self, value):
        self.__showEmptyItems = value
        self._groups.showEmptyItem(value)
        self._woGroup.showEmptyItem(value)

    def changeGroups(self, include = None, exclude = None, isOpened = False):
        if include:
            self._groups.setGroups(include, isOpened)
        if exclude:
            self._groups.removeGroups(exclude)
        return True

    def addContact(self, contact):
        if _TAG.FRIEND not in contact.getTags():
            return False
        if contact.getGroups():
            self._groups.setContact(contact)
        else:
            self._woGroup.setContact(contact)
        return True

    def updateContact(self, contact):
        dbID = contact.getID()
        for converter in (self._groups, self._woGroup):
            if converter.hasContact(dbID):
                converter.setContact(contact)
                return True

        return False

    def removeContact(self, contact):
        dbID = contact.getID()
        for converter in (self._groups, self._woGroup):
            if converter.hasContact(dbID):
                converter.removeContact(dbID)
                return True

        return False

    def getGroups(self, pattern = None):
        data = self._groups.makeVO(pattern)
        hasWoContacts = self._woGroup.hasContacts()
        if pattern is None and not data and not hasWoContacts:
            if self.__showEmptyItems:
                data.append(self._woGroup.makeEmptyRow(self.__currentParent))
                data.append(self._woGroup.makeEmptyRow(self.__currentParent, False, False))
        else:
            woList = self._woGroup.makeVO(pattern)
            if len(woList) > 0:
                if not hasWoContacts:
                    lastElement = woList[0]
                    if lastElement['gui']['id'] is None:
                        lastElement['data']['isVisible'] = False
                else:
                    woList.append(self._woGroup.makeEmptyRow(self.__currentParent, False, False))
            elif data:
                woList.append(self._woGroup.makeEmptyRow(self.__currentParent, False, True))
            elif pattern is None:
                woList.append(self._woGroup.makeEmptyRow(self.__currentParent, False, False))
            data.extend(woList)
        return data

    def getContactsDict(self):
        resultDict = self._woGroup.getContacts()
        resultDict.update(self._groups.getContacts())
        return resultDict

    def setAction(self, actionID, contact):
        result = False
        checkIsEmptyNeeded = False
        if actionID == _ACTION_ID.FRIEND_REMOVED:
            result = self.removeContact(contact)
        elif actionID == _ACTION_ID.IGNORED_ADDED:
            result = self.removeContact(contact)
            checkIsEmptyNeeded = True
        elif actionID == _ACTION_ID.FRIEND_ADDED:
            result = self.addContact(contact)
        elif actionID == _ACTION_ID.GROUPS_CHANGED:
            result = self.removeContact(contact)
            if result:
                result = self.addContact(contact)
        elif actionID == _ACTION_ID.SUBSCRIPTION_CHANGED:
            result = self.updateContact(contact)
            if not result:
                result = self.addContact(contact)
                checkIsEmptyNeeded = True
        elif actionID == _ACTION_ID.NOTE_CHANGED:
            result = self.updateContact(contact)
        if checkIsEmptyNeeded:
            if not result and self.__showEmptyItems:
                if self.isEmpty() or not self.hasContacts():
                    result = True
        return result


class _FormationCategory(_Category):
    __slots__ = ('_clan', '_club', '__parentItemData')

    def __init__(self):
        super(_FormationCategory, self).__init__(CONTACTS_ALIASES.GROUP_FORMATIONS_CATEGORY_ID)
        self.__parentItemData = self._converter.makeBaseVO()
        self._clan = _vo_converter.ClanConverter(self.__parentItemData, self.playerCtx.getClanAbbrev())
        self._club = _vo_converter.ClubConverter(self.__parentItemData, self.playerCtx.getMyClubName())

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def clear(self, full = False):
        self._clan.clear(full)
        self._club.clear(full)
        super(_FormationCategory, self).clear(full)

    def getContactsDict(self):
        return self._clan.getContacts()

    def getTags(self):
        return {_TAG.CLAN_MEMBER, _TAG.CLUB_MEMBER}

    def isEmpty(self):
        return self._clan.isEmpty() and self._club.isEmpty()

    def hasContacts(self):
        return self._clan.hasContacts() or self._club.hasContacts()

    def toggleGroup(self, name):
        result = False
        if name == self._clan.getName():
            self._clan.toggle()
            result = True
        elif name == self._club.getName():
            self._club.toggle()
            result = True
        return result

    def setOnlineMode(self, value):
        if value:
            clazz = _vo_converter.OnlineOnlyCondition
        else:
            clazz = _vo_converter.OnlineTotalCondition
        self._clan.setConditionClass(clazz)
        self._club.setConditionClass(clazz)

    def updateClanAbbrev(self):
        self._clan.setClanAbbrev(self.playerCtx.getClanAbbrev())

    def updateClubName(self):
        self._club.setClubName(self.playerCtx.getMyClubName())

    def addContact(self, contact):
        result = False
        tags = contact.getTags()
        if _TAG.CLAN_MEMBER in tags:
            result = self._clan.setContact(contact)
        if _TAG.CLUB_MEMBER in tags:
            result |= self._club.setContact(contact)
        return result

    def updateContact(self, contact):
        dbID = contact.getID()
        result = False
        for converter in self._getIterator():
            if converter.hasContact(dbID):
                result |= converter.setContact(contact)

        return result

    def removeContact(self, contact):
        dbID = contact.getID()
        result = False
        for converter in self._getIterator():
            if converter.hasContact(dbID):
                result |= converter.removeContact(dbID)

        return result

    def getGroups(self, pattern = None):
        data = []
        for converter in self._getIterator():
            if not converter.isEmpty():
                vos = converter.makeVO(pattern)
                if vos:
                    data.append(vos)

        if data:
            data.append(self._club.makeEmptyRow(self.__parentItemData, False, False))
        return data

    def _getIterator(self):
        for converter in (self._clan, self._club):
            yield converter


class _OthersCategory(_Category):
    __slots__ = ('_ignored', '_pending', '_referrers', '_referrals')

    def __init__(self):
        super(_OthersCategory, self).__init__(CONTACTS_ALIASES.GROUP_OTHER_CATEGORY_ID)
        self._ignored = _vo_converter.IgnoredConverter(self._converter.makeBaseVO())
        self._pending = _vo_converter.RqFriendshipConverter(self._converter.makeBaseVO())
        self._referrers = _vo_converter.ReferrersConverter(self._converter.makeBaseVO())
        self._referrals = _vo_converter.ReferralsConverter(self._converter.makeBaseVO())

    def clear(self, full = False):
        for group in self._iterGroups():
            group.clear(full)

        super(_OthersCategory, self).clear(full)

    def getTags(self):
        return {_TAG.IGNORED,
         _TAG.REFERRER,
         _TAG.REFERRAL,
         _TAG.SUB_PENDING_IN}

    def isEmpty(self):
        for group in self._iterGroups():
            if not group.isEmpty():
                return False

        return True

    def hasContacts(self):
        pass

    def toggleGroup(self, name):
        for group in self._iterGroups():
            if group.getName() == name:
                group.toggle()
                return True

        return False

    def addContact(self, contact):
        result = False
        tags = contact.getTags()
        if _TAG.IGNORED in tags:
            result = self._ignored.setContact(contact)
        if not contact.isFriend() and _TAG.SUB_PENDING_IN in tags:
            result = self._pending.setContact(contact)
        if _TAG.REFERRER in tags:
            result = self._referrers.setContact(contact)
        if _TAG.REFERRAL in tags:
            result = self._referrals.setContact(contact)
        return result

    def updateContact(self, contact):
        result = False
        for group in self._iterGroups():
            if group.hasContact(contact.getID()):
                group.setContact(contact)
                result = True

        return result

    def removeContact(self, contact):
        dbID = contact.getID()
        result = False
        for group in self._iterGroups():
            if group.removeContact(dbID):
                result = True

        return result

    def getGroups(self, pattern = None):
        data = []
        for group in self._iterGroups():
            if not group.isEmpty():
                vos = group.makeVO(pattern)
                if vos:
                    data.append(vos)

        return data

    def setAction(self, actionID, contact):
        dbID = contact.getID()
        tags = contact.getTags()
        result = False
        if actionID == _ACTION_ID.IGNORED_ADDED:
            result = self._ignored.setContact(contact)
        elif actionID in (_ACTION_ID.IGNORED_REMOVED, _ACTION_ID.FRIEND_ADDED):
            result = self._ignored.removeContact(dbID)
        elif actionID == _ACTION_ID.SUBSCRIPTION_CHANGED:
            if not contact.isFriend() and _TAG.SUB_PENDING_IN in contact.getTags():
                result = self._pending.setContact(contact)
            else:
                result = self._pending.removeContact(dbID)
        if _TAG.REFERRER in tags:
            result = self._referrers.setContact(contact)
        if _TAG.REFERRAL in tags:
            result = self._referrals.setContact(contact)
        if actionID == _ACTION_ID.NOTE_CHANGED:
            result = self.updateContact(contact)
        return result

    def _iterGroups(self):
        for group in (self._pending,
         self._ignored,
         self._referrers,
         self._referrals):
            yield group


class _ContactsCriteria(UserTagsFindCriteria):

    def __init__(self, tags):
        super(_ContactsCriteria, self).__init__(tags, None)
        return

    def filter(self, user):
        result = False
        if not user.isCurrentPlayer():
            result = super(_ContactsCriteria, self).filter(user)
        return result


class _ContactsCategories(object):
    __slots__ = ('_categories', '_onlineMode', '_pattern', '_cache')

    def __init__(self):
        super(_ContactsCategories, self).__init__()
        self._categories = [_FriendsCategory(), _FormationCategory()]
        self._onlineMode = None
        self._pattern = None
        self._cache = []
        return

    def clear(self, full = False):
        for category in self._categories:
            category.clear(full)

        self._pattern = None
        return

    def isEmpty(self):
        for category in self._iterCategories():
            if not category.isEmpty():
                return False

        return True

    def setOnlineMode(self, mode):
        for category in self._iterCategories():
            category.setOnlineMode(mode)

    def showOthersCategory(self, value):
        isAlreadyHasOthersCategory = self.__hasOtherCategory()
        if value:
            if not isAlreadyHasOthersCategory:
                self._categories.append(_OthersCategory())
        elif isAlreadyHasOthersCategory:
            self._categories.pop()

    def setVisible(self, categoryID, value):
        for category in self._categories:
            if category.getID() == categoryID:
                category.setVisible(value)
                return True

        return False

    def setAction(self, actionID, contact):
        result = False
        for idx, category in enumerate(self._iterCategories()):
            if idx >= len(self._cache):
                self._cache.append(None)
            if category.setAction(actionID, contact):
                self._cache[idx] = category.getData(self._pattern)
                result = True

        data = filter(lambda item: bool(item), self._cache)
        if len(data) == 1 and self.isEmpty():
            data = []
        return (result, data)

    def setStatus(self, contact):
        result = False
        for idx, category in enumerate(self._iterCategories()):
            if idx >= len(self._cache):
                self._cache.append(None)
            if category.setStatus(contact):
                self._cache[idx] = category.getData(self._pattern)
                result = True

        data = filter(lambda item: bool(item), self._cache)
        if len(data) == 1 and self.isEmpty():
            data = []
        return (result, data)

    def getCriteria(self, full = False):
        tags = set()
        if full:
            categories = self._categories
        else:
            categories = self._iterCategories()
        for category in categories:
            tags.update(category.getTags())

        return _ContactsCriteria(tags)

    def addContact(self, contact):
        for category in self._iterCategories():
            category.addContact(contact)

    def getData(self):
        self._cache = []
        data = []
        for category in self._iterCategories():
            categoryData = category.getData(self._pattern)
            self._cache.append(categoryData)
            if categoryData:
                data.append(categoryData)

        if len(data) == 1 and self.isEmpty():
            data = []
        return data

    def applySearchFilter(self, searchCriteria):
        if searchCriteria:
            self._pattern = re.compile(re.escape(searchCriteria), re.I)
        else:
            self._pattern = None
        return self.getData()

    def toggleGroup(self, categoryID, groupName):
        result = False
        for idx, category in enumerate(self._iterCategories()):
            if idx >= len(self._cache):
                self._cache.append(None)
            if category.getID() != categoryID:
                continue
            if category.toggleGroup(groupName):
                self._cache[idx] = category.getData(self._pattern)
                result = True
                break

        data = filter(lambda item: bool(item), self._cache)
        if len(data) == 1 and self.isEmpty():
            data = []
        return (result, data)

    def changeGroups(self, categoryID, include = None, exclude = None, isOpened = False):
        result = False
        for idx, category in enumerate(self._iterCategories()):
            if idx >= len(self._cache):
                self._cache.append(None)
            if category.getID() != categoryID:
                continue
            if category.changeGroups(include, exclude, isOpened):
                self._cache[idx] = category.getData(self._pattern)
                result = True
                break

        data = filter(lambda item: bool(item), self._cache)
        if len(data) == 1 and self.isEmpty():
            data = []
        return (result, data)

    def findCategory(self, categoryID):
        idx = 0
        for category in self._iterCategories():
            if category.getID() == categoryID:
                return (idx, category)
            idx += 1

        return (-1, None)

    def getContactsList(self):
        resultDict = {}
        for category in self._iterCategories():
            if category.isAvoid():
                continue
            resultDict.update(category.getContactsDict())

        resultList = []
        for contact in resultDict.itervalues():
            if self._pattern is not None:
                if self._pattern.match(contact['criteria'][1]) is not None:
                    resultList.append(contact['data'])
            else:
                resultList.append(contact['data'])

        return resultList

    def _iterCategories(self):
        for category in self._categories:
            if category.isVisible():
                yield category

    def __hasOtherCategory(self):
        return len(self._categories) > 2


class _OpenedTreeCreator():

    def __init__(self):
        self.__openedTree = None
        return

    def build(self, targetList):
        self.__openedTree = []
        for iCategory in targetList:
            self.__openTree(iCategory, None, True)

        return self.__openedTree

    def __openTree(self, targetTreeItem, parent, isOpened):
        children = targetTreeItem.get('children', None)
        if isOpened:
            self.__openedTree.append(targetTreeItem)
        if children is not None:
            for child in children:
                self.__openTree(child, targetTreeItem, targetTreeItem.get('isOpened', False))

        return


class ContactsDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(ContactsDataProvider, self).__init__()
        self.__categories = _ContactsCategories()
        self.__showEmptyGroups = True
        self.__isEmpty = True
        self.__list = []
        self.onTotalStatusChanged = Event.Event()
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged

    @storage_getter('users')
    def usersStorage(self):
        return None

    def refresh(self):
        super(ContactsDataProvider, self).refresh()

    @property
    def collection(self):
        return self.__list

    def buildList(self):
        self.__categories.clear()
        self.__list = []
        self.__setEmpty()
        if self.__isEmpty:
            return
        contacts = self.usersStorage.getList(self.__categories.getCriteria())
        if self.__showEmptyGroups:
            _, friendsCategory = self.__categories.findCategory(CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID)
            if friendsCategory:
                friendsCategory.showEmptyItem(True)
                friendsCategory.changeGroups(self.usersStorage.getEmptyGroups())
        for contact in contacts:
            if _TAG.CACHED not in contact.getTags():
                self.__categories.addContact(contact)

        self.__updateCollection(self.__categories.getData())

    def emptyItem(self):
        return None

    def pyRequestItemRange(self, startIndex, endIndex):
        item_range = super(ContactsDataProvider, self).pyRequestItemRange(startIndex, endIndex)
        return item_range

    def getContactsList(self):
        return self.__categories.getContactsList()

    def isEmpty(self):
        return self.__isEmpty

    def hasDisplayingContacts(self):
        for cName in (CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID, CONTACTS_ALIASES.GROUP_FORMATIONS_CATEGORY_ID, CONTACTS_ALIASES.GROUP_OTHER_CATEGORY_ID):
            _, category = self.__categories.findCategory(cName)
            if category and category.hasContacts():
                return True

        return False

    def setShowEmptyGroups(self, value):
        self.__showEmptyGroups = value
        _, friendsCategory = self.__categories.findCategory(CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID)
        if friendsCategory:
            friendsCategory.showEmptyItem(self.__showEmptyGroups)

    def setOnlineMode(self, value):
        self.__categories.setOnlineMode(value)

    def setFriendsVisible(self, value):
        self.__categories.setVisible(CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID, value)

    def setFormationsVisible(self, value):
        self.__categories.setVisible(CONTACTS_ALIASES.GROUP_FORMATIONS_CATEGORY_ID, value)

    def setOthersVisible(self, value):
        if value is None:
            self.__categories.showOthersCategory(False)
        else:
            self.__categories.showOthersCategory(True)
            self.__categories.setVisible(CONTACTS_ALIASES.GROUP_OTHER_CATEGORY_ID, value)
        return

    def setFriendsGroupMutable(self, value):
        _, category = self.__categories.findCategory(CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID)
        if category:
            category.setGroupsMutable(value)

    def setSearchFilter(self, searchCriteria):
        if not self.__isEmpty:
            self.__updateCollection(self.__categories.applySearchFilter(searchCriteria))
            return True
        else:
            return False

    def toggleGroup(self, categoryID, groupName):
        result, data = self.__categories.toggleGroup(categoryID, groupName)
        if result:
            self.__updateCollection(data)
            self.refresh()

    def addContactsListeners(self):
        events = g_messengerEvents.users
        events.onUsersListReceived += self.__me_onUsersListReceived
        events.onUserActionReceived += self.__me_onUserActionReceived
        events.onUserStatusUpdated += self.__me_onUserStatusUpdated
        events.onClanMembersListChanged += self.__me_onClanMembersListChanged
        events.onFriendshipRequestsAdded += self.__me_onFriendshipRequestsAdded
        events.onFriendshipRequestsUpdated += self.__me_onFriendshipRequestsUpdated
        events.onEmptyGroupsChanged += self.__me_onEmptyGroupsChanged
        events.onNotesListReceived += self.__me_onNotesListReceived

    def removeContactsListeners(self):
        events = g_messengerEvents.users
        events.onUsersListReceived -= self.__me_onUsersListReceived
        events.onUserActionReceived -= self.__me_onUserActionReceived
        events.onUserStatusUpdated -= self.__me_onUserStatusUpdated
        events.onClanMembersListChanged -= self.__me_onClanMembersListChanged
        events.onFriendshipRequestsAdded -= self.__me_onFriendshipRequestsAdded
        events.onFriendshipRequestsUpdated -= self.__me_onFriendshipRequestsUpdated
        events.onEmptyGroupsChanged -= self.__me_onEmptyGroupsChanged
        events.onNotesListReceived -= self.__me_onNotesListReceived

    def _dispose(self):
        self.__categories.clear(True)
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(ContactsDataProvider, self)._dispose()

    def __setEmpty(self):
        groups = self.usersStorage.getEmptyGroups()
        if groups and self.__showEmptyGroups:
            isEmpty = False
        else:
            isEmpty = not self.usersStorage.getCount(self.__categories.getCriteria(True))
        if self.__isEmpty != isEmpty:
            self.__isEmpty = isEmpty
            return True
        else:
            return False

    def __updateContacts(self, actionID, contacts):
        setAction = self.__categories.setAction
        result, data = False, []
        for contact in contacts:
            updated, data = setAction(actionID, contact)
            result |= updated

        if result:
            self.__updateCollection(data)
            self.refresh()
        self.__setEmpty()
        self.onTotalStatusChanged()

    def __updateCollection(self, targetList):
        self.__list = _OpenedTreeCreator().build(targetList)

    def __onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            self.buildList()
            self.refresh()

    def __me_onUsersListReceived(self, tags):
        if _TAG.CACHED not in tags:
            if _TAG.CLUB_MEMBER in tags:
                _, category = self.__categories.findCategory(CONTACTS_ALIASES.GROUP_FORMATIONS_CATEGORY_ID)
                if category:
                    category.updateClubName()
            self.buildList()
            self.refresh()
            self.onTotalStatusChanged()

    def __me_onUserActionReceived(self, actionID, contact):
        result, data = self.__categories.setAction(actionID, contact)
        if result:
            self.__updateCollection(data)
            self.refresh()
        self.__setEmpty()
        self.onTotalStatusChanged()

    def __me_onUserStatusUpdated(self, contact):
        isEmpty = len(self.__list) > 0
        result, data = self.__categories.setStatus(contact)
        if result:
            self.__updateCollection(data)
            self.refresh()
            if isEmpty != (len(self.__list) > 0):
                self.onTotalStatusChanged()

    def __me_onClanMembersListChanged(self):
        _, category = self.__categories.findCategory(CONTACTS_ALIASES.GROUP_FORMATIONS_CATEGORY_ID)
        if category:
            category.updateClanAbbrev()
        self.buildList()
        self.refresh()
        self.onTotalStatusChanged()

    def __me_onFriendshipRequestsAdded(self, contacts):
        self.__updateContacts(_ACTION_ID.SUBSCRIPTION_CHANGED, contacts)

    def __me_onFriendshipRequestsUpdated(self, contacts):
        self.__updateContacts(_ACTION_ID.SUBSCRIPTION_CHANGED, contacts)

    def __me_onEmptyGroupsChanged(self, include, exclude):
        if not self.__showEmptyGroups:
            return
        result, data = self.__categories.changeGroups(CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID, include, exclude, True)
        if result:
            isEmpty = len(self.__list) > 0
            self.__updateCollection(data)
            self.refresh()
            if isEmpty != (len(self.__list) > 0):
                self.__setEmpty()
                self.onTotalStatusChanged()

    def __me_onNotesListReceived(self):
        self.buildList()
        self.refresh()
