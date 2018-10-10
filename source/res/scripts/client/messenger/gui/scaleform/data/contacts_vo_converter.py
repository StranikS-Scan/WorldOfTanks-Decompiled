# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/data/contacts_vo_converter.py
from constants import WG_GAMES
from gui import makeHtmlString
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from gui.Scaleform.locale.MESSENGER import MESSENGER as I18N_MESSENGER
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import dependency
from helpers import i18n
from helpers.html import escape
from messenger import g_settings
from messenger.m_constants import USER_TAG
from messenger.storage import storage_getter
from predefined_hosts import g_preDefinedHosts
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
_CATEGORY_I18N_KEY = {CONTACTS_ALIASES.GROUP_FRIENDS_CATEGORY_ID: I18N_MESSENGER.MESSENGER_CONTACTS_MAINGROPS_FRIENDS,
 CONTACTS_ALIASES.GROUP_FORMATIONS_CATEGORY_ID: I18N_MESSENGER.MESSENGER_CONTACTS_MAINGROPS_FORMATIONS,
 CONTACTS_ALIASES.GROUP_OTHER_CATEGORY_ID: I18N_MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER}
_DEF_RULES = CONTACTS_ALIASES.GROUP_IS_RESIZABLE
_MUTABLE_RULE = CONTACTS_ALIASES.GROUP_CAN_BE_MANAGED
_FRIENDS_RULES = CONTACTS_ALIASES.GROUP_IS_DROP_ALLOWED | CONTACTS_ALIASES.GROUP_IS_RESIZABLE
_IGNORED_RULES = CONTACTS_ALIASES.GROUP_IS_DROP_ALLOWED | CONTACTS_ALIASES.GROUP_IS_RESIZABLE

class _WOT_GAME_RESOURCE(object):
    ONLINE = 'user_is_online'
    UNKNOWN = 'unknown'
    BUSY = 'user_is_busy'
    BUSY_BLIND = 'user_is_busy_violet'


def makeClanFullName(clanAbbrev):
    formatted = ''
    if clanAbbrev:
        formatted = '{0} [{1}]'.format(i18n.makeString(I18N_MESSENGER.DIALOGS_CONTACTS_TREE_CLAN), clanAbbrev)
    return formatted


def makeContactStatusDescription(isOnline, tags, clientInfo=None):
    name, description = ('', '')
    if isOnline:
        if clientInfo:
            gameHost = clientInfo.gameHost
            arenaLabel = clientInfo.arenaLabel
        else:
            gameHost, arenaLabel = ('', '')
        if gameHost:
            item = g_preDefinedHosts.byUrl(gameHost)
            name = item.shortName or item.name
        if USER_TAG.PRESENCE_DND in tags:
            key = None
            if arenaLabel:
                key = TOOLTIPS.contact_status_inbattle(arenaLabel)
            if not key:
                key = TOOLTIPS.CONTACT_STATUS_INBATTLE_UNKNOWN
            description = i18n.makeString(key)
        else:
            description = i18n.makeString(TOOLTIPS.CONTACT_STATUS_ONLINE)
        if name:
            description = '{0}, {1}'.format(description, name)
    return description


def _setMutableRule(rules, flag):
    if flag:
        if not rules & _MUTABLE_RULE:
            rules |= _MUTABLE_RULE
    elif rules & _MUTABLE_RULE > 0:
        rules |= _MUTABLE_RULE
    return rules


class CategoryConverter(object):
    __slots__ = ('_categoryID', '_userString', '_rules')

    def __init__(self, categoryID, rules=_DEF_RULES):
        super(CategoryConverter, self).__init__()
        self._categoryID = categoryID
        self._userString = i18n.makeString(_CATEGORY_I18N_KEY[categoryID])
        self._rules = rules

    def getCategoryID(self):
        return self._categoryID

    def setMutable(self, value):
        self._rules = _setMutableRule(self._rules, value)

    def makeVO(self, children=None):
        baseVo = self.makeBaseVO()
        baseVo['isOpened'] = True
        baseVo['data']['title'] = self._userString
        baseVo['children'] = children
        return baseVo

    def makeBaseVO(self):
        return {'gui': {'id': self._categoryID},
         'data': {'rules': self._rules}}


class ContactConverter(object):
    _colors = {}
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def getIcons(cls, tags, note):
        icons = []
        if USER_TAG.IGR_BASE in tags:
            icons.append(RES_ICONS.MAPS_ICONS_LIBRARY_BASIC_SMALL)
        elif USER_TAG.IGR_PREMIUM in tags:
            if USER_TAG.SUB_TO not in tags:
                icons.append(RES_ICONS.MAPS_ICONS_LIBRARY_PREMIUM_SMALL)
        if USER_TAG.REFERRAL in tags or USER_TAG.REFERRER in tags:
            icons.append(RES_ICONS.MAPS_ICONS_REFERRAL_REFERRALSMALLHAND)
        if USER_TAG.IGNORED in tags:
            icons.append(RES_ICONS.MAPS_ICONS_MESSENGER_CONTACTIGNORED)
        elif USER_TAG.FRIEND in tags and USER_TAG.SUB_TO not in tags and USER_TAG.SUB_FROM not in tags:
            icons.append(RES_ICONS.MAPS_ICONS_MESSENGER_CONTACTCONFIRMNEEDED)
        if USER_TAG.BAN_CHAT in tags:
            icons.append(RES_ICONS.MAPS_ICONS_MESSENGER_CONTACTMSGSOFF)
        if note:
            icons.append(RES_ICONS.MAPS_ICONS_MESSENGER_CONTACTNOTE)
        return icons

    @classmethod
    def getColor(cls, tags, isOnline):
        if USER_TAG.CURRENT in tags:
            colors = cls._getColors('currentUser')
        elif {USER_TAG.FRIEND, USER_TAG.SUB_TO}.issubset(tags):
            colors = cls._getColors('friend')
        elif {USER_TAG.CLAN_MEMBER, USER_TAG.OTHER_CLAN_MEMBER}.issubset(tags):
            colors = cls._getColors('clanMember')
        else:
            colors = cls._getColors('others')
        if isOnline:
            color = colors[0]
        else:
            color = colors[1]
        return color

    @classmethod
    def makeVO(cls, contact, useBigIcons=False):
        dbID = contact.getID()
        tags = contact.getTags()
        note = contact.getNote()
        isOnline = contact.isOnline()
        if USER_TAG.CLAN_MEMBER in tags:
            pass
        elif contact.getClanAbbrev():
            tags.add(USER_TAG.OTHER_CLAN_MEMBER)
        baseUserProps = cls.makeBaseUserProps(contact)
        baseUserProps['rgb'] = cls.getColor(tags, isOnline)
        baseUserProps['icons'] = cls.getIcons(tags, note)
        baseUserProps['tags'] = list(tags)
        resourceIconId = cls.getGuiResourceID(contact)
        isColorBlind = cls.settingsCore.getSetting('isColorBlind')
        if resourceIconId == WG_GAMES.TANKS:
            if contact.isOnline():
                if USER_TAG.PRESENCE_DND in tags:
                    resourceIconId = _WOT_GAME_RESOURCE.BUSY_BLIND if isColorBlind else _WOT_GAME_RESOURCE.BUSY
                else:
                    resourceIconId = _WOT_GAME_RESOURCE.ONLINE
            else:
                resourceIconId = _WOT_GAME_RESOURCE.UNKNOWN
        return {'userProps': baseUserProps,
         'dbID': dbID,
         'note': escape(note),
         'resource': RES_ICONS.getContactStatusIcon('48x48' if useBigIcons else '24x24', resourceIconId)}

    @classmethod
    def makeBaseUserProps(cls, contact):
        return {'userName': contact.getName(),
         'tags': list(contact.getTags()),
         'region': cls.lobbyContext.getRegionCode(contact.getID()),
         'clanAbbrev': contact.getClanAbbrev()}

    @classmethod
    def makeIconTag(cls, key='imgTag', iconPath=''):
        if iconPath:
            ctx = {'iconName': iconPath}
        else:
            ctx = None
        return makeHtmlString('html_templates:contacts/contact', key, ctx=ctx)

    @classmethod
    def getGuiResourceID(cls, contact):
        resourceId = contact.getResourceID()
        if resourceId:
            for prefix in WG_GAMES.ALL:
                if prefix != WG_GAMES.TANKS:
                    if prefix in resourceId:
                        resourceId = prefix
                        break

        if not resourceId:
            resourceId = WG_GAMES.TANKS
        return resourceId

    @classmethod
    def _getColors(cls, name):
        if not cls._colors:
            scheme = g_settings.getColorScheme('contacts')
            cls._colors = {'friend': scheme.getColors('friend'),
             'clanMember': scheme.getColors('clanMember'),
             'others': scheme.getColors('others'),
             'currentUser': scheme.getColors('currentUser')}
        return cls._colors[name]


_CACHED_ICONS_TAGS = {'ignored': ContactConverter.makeIconTag(iconPath='contactIgnored.png'),
 'pending': ContactConverter.makeIconTag(iconPath='contactConfirmNeeded.png'),
 'note': ContactConverter.makeIconTag(iconPath='contactNote.png'),
 'refSys': ContactConverter.makeIconTag(key='referrTag')}

class _GroupCondition(object):
    __slots__ = ('_htmlString', '_allIDs')

    def __init__(self):
        super(_GroupCondition, self).__init__()
        self._htmlString = ''
        self._allIDs = set()

    def clear(self):
        self._allIDs.clear()

    def set(self, contact):
        self._allIDs.add(contact.getID())
        self._htmlString = self._makeHtmlString()
        return True

    def validate(self, contact):
        return True

    def exists(self, dbID):
        return dbID in self._allIDs

    def empty(self):
        return not self._allIDs

    def remove(self, dbID):
        result = dbID in self._allIDs
        if result:
            self._allIDs.remove(dbID)
            self._htmlString = self._makeHtmlString()
        return result

    def getHtmlString(self):
        return self._htmlString

    def _makeHtmlString(self):
        pass


class TotalCondition(_GroupCondition):

    def _makeHtmlString(self):
        total = len(self._allIDs)
        if total:
            result = makeHtmlString('html_templates:contacts/group', 'totalUsersCounter', ctx={'totalCount': total})
        else:
            result = ''
        return result


class OnlineTotalCondition(TotalCondition):
    __slots__ = ('_online',)

    def __init__(self):
        super(OnlineTotalCondition, self).__init__()
        self._online = {}

    def clear(self):
        self._online.clear()
        super(OnlineTotalCondition, self).clear()

    def set(self, contact):
        self._online[contact.getID()] = 1 if contact.isOnline() else 0
        super(OnlineTotalCondition, self).set(contact)
        return True

    def validate(self, contact):
        self._online[contact.getID()] = 1 if contact.isOnline() else 0
        return True

    def remove(self, dbID):
        result = self._online.pop(dbID, None) is not None
        super(OnlineTotalCondition, self).remove(dbID)
        return result

    def _makeHtmlString(self):
        total = len(self._allIDs)
        if total:
            result = makeHtmlString('html_templates:contacts/group', 'onlineUsersCounter', ctx={'onlineCount': sum(self._online.values()),
             'totalCount': total})
        else:
            result = ''
        return result


class OnlineOnlyCondition(OnlineTotalCondition):

    def set(self, contact):
        return super(OnlineOnlyCondition, self).set(contact) and contact.isOnline()

    def validate(self, contact):
        return super(OnlineOnlyCondition, self).validate(contact) and contact.isOnline()


class IContactsConverter(object):
    __slots__ = ()

    def clear(self, full=False):
        raise NotImplementedError

    def getContacts(self):
        raise NotImplementedError

    def hasContacts(self):
        return False

    def hasContact(self, dbID):
        raise NotImplementedError

    def setContact(self, contact):
        raise NotImplementedError

    def removeContact(self, dbID):
        raise NotImplementedError

    def makeVO(self, pattern=None):
        raise NotImplementedError


class _ContactsConverter(IContactsConverter):
    __slots__ = ('_contacts', '_condition', '_converter', '_showEmptyItem', '_parent')

    def __init__(self, parent, condition=None, showEmptyItem=False):
        super(_ContactsConverter, self).__init__()
        self._contacts = {}
        self._condition = condition or _GroupCondition()
        self._converter = ContactConverter()
        self._showEmptyItem = showEmptyItem
        self._parent = parent

    def getContacts(self):
        return self._contacts.copy()

    def hasContacts(self):
        return len(self._contacts) > 0

    def clear(self, full=False):
        self._contacts.clear()
        self._condition.clear()
        if full:
            self._parent = None
        return

    def isEmpty(self):
        return not self._contacts

    def showEmptyItem(self, value):
        self._showEmptyItem = value

    def setConditionClass(self, clazz):
        self._condition = clazz()

    def hasContact(self, dbID):
        return self._condition.exists(dbID)

    def setContact(self, contact):
        result = self._condition.set(contact)
        dbID = contact.getID()
        if result:
            self._contacts[dbID] = self._makeContactVO(contact)
        elif not self._condition.validate(contact):
            result = self._contacts.pop(dbID, None) is not None
        return result

    def removeContact(self, dbID):
        result = self._condition.remove(dbID)
        self._contacts.pop(dbID, None)
        return result

    def makeVO(self, pattern=None):
        if pattern:
            contacts = self._matchPattern(pattern, self._contacts.itervalues())
        else:
            if not self._contacts and self._showEmptyItem:
                return [self.makeEmptyRow(self._parent)]
            contacts = self._contacts.itervalues()
        return sorted(contacts, key=lambda item: item['criteria'])

    def _makeContactVO(self, contact):
        dbID = contact.getID()
        return {'data': self._converter.makeVO(contact),
         'criteria': (0 if contact.isOnline() else 1, contact.getName().lower()),
         'gui': {'id': dbID},
         'parentItemData': self._parent}

    @classmethod
    def makeEmptyRow(cls, parent, isVisible=True, isActive=True):
        return {'gui': {'id': None},
         'parentItemData': parent,
         'data': {'isActive': isActive,
                  'isVisible': isVisible}}

    def _matchPattern(self, pattern, contacts):
        return [ vo for vo in contacts if pattern.match(vo['criteria'][1]) ]


class GroupConverter(_ContactsConverter):
    __slots__ = ('_name', '_criteria', '_isOpened', '_rules', '_parentCategory')

    def __init__(self, name, parentCategory, condition=None, rules=_DEF_RULES, showEmptyItem=False, isOpened=False):
        self._name = name
        self._criteria = name.lower()
        self._isOpened = isOpened
        self._rules = rules
        self._parentCategory = parentCategory
        super(GroupConverter, self).__init__(self.__makeBaseVO(parentCategory), condition, showEmptyItem)

    def clear(self, full=False):
        super(GroupConverter, self).clear()
        if full:
            self._parentCategory = None
        return

    def getName(self):
        return self._name

    def getCriteria(self):
        return self._criteria

    def getGuiID(self):
        return self._name

    def setMutable(self, value):
        self._rules = _setMutableRule(self._rules, value)

    def setOpened(self, value):
        self._isOpened = value

    def toggle(self):
        self._isOpened = not self._isOpened

    def makeVO(self, pattern=None):
        contacts = super(GroupConverter, self).makeVO(pattern)
        if pattern:
            isOpened = True
            if not contacts:
                return None
        else:
            isOpened = self._isOpened
        vo = self.__makeBaseVO(self._parentCategory)
        vo['isOpened'] = isOpened
        vo['children'] = contacts
        vo['data']['isOpened'] = isOpened
        vo['data']['headerDisplayTitle'] = escape(self._name)
        vo['data']['headerHtmlPart'] = self._condition.getHtmlString()
        return vo

    def __makeBaseVO(self, parent):
        return {'gui': {'id': self.getGuiID()},
         'parentItemData': parent,
         'data': {'headerTitle': self._name,
                  'rules': self._rules}}


class ClanConverter(GroupConverter):

    def __init__(self, parentCategory, clanAbbrev='', condition=None):
        super(ClanConverter, self).__init__(makeClanFullName(clanAbbrev), parentCategory, condition)

    def isEmpty(self):
        return not self._name or self._condition.empty()

    def getGuiID(self):
        return CONTACTS_ALIASES.CLAN_GROUP_RESERVED_ID

    def setClanAbbrev(self, clanAbbrev):
        self._name = makeClanFullName(clanAbbrev)


class IgnoredConverter(GroupConverter):

    def __init__(self, parentCategory):
        super(IgnoredConverter, self).__init__(i18n.makeString(I18N_MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_IGNORED), parentCategory, TotalCondition(), _IGNORED_RULES)

    def getGuiID(self):
        return CONTACTS_ALIASES.IGNORED_GROUP_RESERVED_ID


class RqFriendshipConverter(GroupConverter):

    def __init__(self, parentCategory):
        super(RqFriendshipConverter, self).__init__(i18n.makeString(I18N_MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_FRIENDSHIPREQUEST), parentCategory, TotalCondition())

    def getGuiID(self):
        return CONTACTS_ALIASES.PENDING_FRIENDS_GROUP_RESERVED_ID


class ReferralsConverter(GroupConverter):

    def __init__(self, parentCategory):
        super(ReferralsConverter, self).__init__(i18n.makeString(I18N_MESSENGER.MESSENGER_CONTACTS_MAINGROUPS_OTHER_REFERRALS), parentCategory, TotalCondition())

    def getGuiID(self):
        return CONTACTS_ALIASES.REFERRALS_GROUP_RESERVED_ID


class ReferrersConverter(GroupConverter):

    def __init__(self, parentCategory):
        super(ReferrersConverter, self).__init__(i18n.makeString(I18N_MESSENGER.MESSENGER_CONTACTS_MAINGROUPS_OTHER_REFERRERS), parentCategory, TotalCondition())

    def getGuiID(self):
        return CONTACTS_ALIASES.REFERRERS_GROUP_RESERVED_ID


class FriendsWoGroupConverter(_ContactsConverter):
    pass


class FriendsGroupsConverter(IContactsConverter):
    __slots__ = ('_groups', '_mapping', '_rules', '_showEmptyItem', '_conditionClass', '__parentCategory')

    def __init__(self, parent):
        super(FriendsGroupsConverter, self).__init__()
        self._mapping = {}
        self._groups = {}
        self._rules = _FRIENDS_RULES
        self._showEmptyItem = False
        self._conditionClass = OnlineTotalCondition
        self.__parentCategory = parent

    @storage_getter('users')
    def userStorage(self):
        return None

    def getContacts(self):
        result = {}
        for frGroupConverter in self._groups.itervalues():
            result.update(frGroupConverter.getContacts())

        return result

    def hasContacts(self):
        for frGroupConverter in self._groups.itervalues():
            if frGroupConverter.getContacts():
                return True

        return False

    def clear(self, full=False):
        while self._groups:
            _, group = self._groups.popitem()
            group.clear()

        self._mapping.clear()
        if full:
            self.__parentCategory = None
        return

    def isEmpty(self):
        return not self._groups

    def showEmptyItem(self, value):
        for group in self._groups.itervalues():
            group.showEmptyItem(value)

        self._showEmptyItem = value

    def setConditionClass(self, clazz):
        for group in self._groups.itervalues():
            group.setConditionClass(clazz)

        self._conditionClass = clazz

    def hasContact(self, dbID):
        return dbID in self._mapping

    def setContact(self, contact):
        groups = contact.getGroups()
        self._mapping[contact.getID()] = groups
        for group in groups:
            if group not in self._groups:
                self._groups[group] = GroupConverter(group, self.__parentCategory, self._conditionClass(), self._rules, self._showEmptyItem)
            self._groups[group].setContact(contact)

    def removeContact(self, dbID):
        groups = self._mapping.pop(dbID, set())
        isExists = self.userStorage.isGroupExists
        for group in groups:
            if group in self._groups:
                converter = self._groups[group]
                if converter.removeContact(dbID) and converter.isEmpty() and not isExists(group):
                    self._groups.pop(group)

    def setMutable(self, value):
        for group in self._groups.itervalues():
            group.setMutable(value)

        self._rules = _setMutableRule(self._rules, value)

    def getGroup(self, name):
        group = None
        if name in self._groups:
            group = self._groups[name]
        return group

    def removeGroups(self, groups):
        for group in groups:
            self._groups.pop(group, None)

        return

    def setGroups(self, groups, isOpened=False):
        self._groups.update([ (group, GroupConverter(group, self.__parentCategory, self._conditionClass(), self._rules, self._showEmptyItem, isOpened)) for group in groups ])

    def makeVO(self, pattern=None):
        vos = []
        for group in sorted(self._groups.itervalues(), key=lambda group: group.getCriteria()):
            vo = group.makeVO(pattern)
            if vo:
                vos.append(vo)

        return vos
