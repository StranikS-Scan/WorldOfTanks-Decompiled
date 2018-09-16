# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/tankmen_components.py
from items.components import component_constants
from items.components import legacy_stuff
from items.components import shared_components
from items.components import skills_constants

class GROUP_TAG(object):
    PASSPORT_REPLACEMENT_FORBIDDEN = 'passportReplacementForbidden'
    RESTRICTIONS = (PASSPORT_REPLACEMENT_FORBIDDEN,)
    RANGE = RESTRICTIONS + tuple(skills_constants.ROLES)


class Rank(legacy_stuff.LegacyStuff):
    __slots__ = ('__name', '__i18n', '__icon')

    def __init__(self, name, i18n=None, icon=None):
        super(Rank, self).__init__()
        self.__name = name
        self.__i18n = i18n
        self.__icon = icon or component_constants.EMPTY_STRING

    def __repr__(self):
        return 'Rank({})'.format(self.__name)

    @property
    def name(self):
        return self.__name

    @property
    def userString(self):
        if self.__i18n is not None:
            return self.__i18n.value
        else:
            return component_constants.EMPTY_STRING
            return

    @property
    def icon(self):
        return self.__icon


class RanksSet(object):
    __slots__ = ('__ranks', '__rankIDsByNames')

    def __init__(self):
        super(RanksSet, self).__init__()
        self.__ranks = []
        self.__rankIDsByNames = {}

    def __repr__(self):
        return 'RanksSet({})'.format(self.__rankIDsByNames.keys())

    def add(self, rank):
        self.__rankIDsByNames[rank.name] = len(self.__ranks)
        self.__ranks.append(rank)

    def getRankByID(self, rankID):
        if 0 <= rankID < len(self.__ranks):
            return self.__ranks[rankID]
        else:
            return None
            return None

    def getRankByName(self, name):
        if name in self.__rankIDsByNames:
            return self.__ranks[self.__rankIDsByNames[name]]
        else:
            return None
            return None

    def getIDByName(self, name):
        if name in self.__rankIDsByNames:
            return self.__rankIDsByNames[name]
        raise KeyError('Name of rank "{}" is not found'.format(name))

    def generator(self):
        for rank in self.__ranks:
            yield (self.__rankIDsByNames[rank.name], rank)


class RoleRanks(legacy_stuff.LegacyStuff):
    __slots__ = ('__ranks',)

    def __init__(self):
        super(RoleRanks, self).__init__()
        self.__ranks = {}
        for skill in skills_constants.ROLES:
            self.__ranks[skill] = component_constants.EMPTY_TUPLE

    def __repr__(self):
        return 'RoleRanks(ranks={}, radioman={}, driver={}, gunner={}, loader={})'.format(self.commander, self.radioman, self.driver, self.gunner, self.loader)

    @property
    def commander(self):
        return self.__ranks['commander']

    @property
    def radioman(self):
        return self.__ranks['radioman']

    @property
    def driver(self):
        return self.__ranks['driver']

    @property
    def gunner(self):
        return self.__ranks['gunner']

    @property
    def loader(self):
        return self.__ranks['loader']

    def getRanksIDs(self, roleName):
        if roleName in self.__ranks:
            return self.__ranks[roleName]
        else:
            return component_constants.EMPTY_TUPLE

    def getRankID(self, roleName, rankIdx):
        ranks = self.getRanksIDs(roleName)
        if 0 <= rankIdx < len(ranks):
            return ranks[rankIdx]
        else:
            return None
            return None

    def setRanksIDs(self, roleName, roleIDs):
        if roleName not in skills_constants.ROLES:
            raise KeyError('Role {} is not found'.format(roleName))
        self.__ranks[roleName] = roleIDs


class NationGroup(legacy_stuff.LegacyStuff):
    __slots__ = ('__name', '__isFemales', '__notInShop', '__firstNamesIDs', '__lastNamesIDs', '__iconsIDs', '__weight', '__tags', '__roles')

    def __init__(self, name, isFemales, notInShop, firstNamesIDs, lastNamesIDs, iconsIDs, weight, tags, roles):
        super(NationGroup, self).__init__()
        self.__name = name
        self.__isFemales = isFemales
        self.__notInShop = notInShop
        self.__firstNamesIDs = firstNamesIDs
        self.__lastNamesIDs = lastNamesIDs
        self.__iconsIDs = iconsIDs
        self.__weight = weight
        self.__tags = tags
        self.__roles = roles

    def __repr__(self):
        return 'NationGroup(isFemales={}, notInShop={}, weight={})'.format(self.__isFemales, self.__notInShop, self.__weight)

    @property
    def name(self):
        return self.__name

    @property
    def isFemales(self):
        return self.__isFemales

    @property
    def notInShop(self):
        return self.__notInShop

    @property
    def firstNames(self):
        return self.__firstNamesIDs

    @property
    def firstNamesList(self):
        return list(self.__firstNamesIDs)

    @property
    def lastNames(self):
        return self.__lastNamesIDs

    @property
    def lastNamesList(self):
        return list(self.__lastNamesIDs)

    @property
    def icons(self):
        return self.__iconsIDs

    @property
    def iconsList(self):
        return list(self.__iconsIDs)

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value):
        self.__weight = value

    @property
    def tags(self):
        return self.__tags

    @property
    def roles(self):
        return self.__roles

    @property
    def isUnique(self):
        return 1 == len(self.__firstNamesIDs) * len(self.__lastNamesIDs) * len(self.__iconsIDs)


class NationConfig(legacy_stuff.LegacyStuff):
    __slots__ = ('__name', '__normalGroups', '__premiumGroups', '__roleRanks', '__firstNames', '__lastNames', '__icons', '__ranks')

    def __init__(self, name, normalGroups=None, premiumGroups=None, roleRanks=None, firstNames=None, lastNames=None, icons=None, ranks=None):
        super(NationConfig, self).__init__()
        self.__name = name
        self.__normalGroups = normalGroups or component_constants.EMPTY_TUPLE
        self.__premiumGroups = premiumGroups or component_constants.EMPTY_TUPLE
        self.__roleRanks = roleRanks
        self.__firstNames = firstNames or {}
        self.__lastNames = lastNames or {}
        self.__icons = icons or {}
        self.__ranks = ranks

    def __repr__(self):
        return 'NationConfig({})'.format(self.__name)

    @property
    def normalGroups(self):
        return self.__normalGroups

    @property
    def premiumGroups(self):
        return self.__premiumGroups

    @property
    def roleRanks(self):
        return self.__roleRanks

    @property
    def firstNames(self):
        return self.__firstNames

    @property
    def lastNames(self):
        return self.__lastNames

    @property
    def icons(self):
        return self.__icons

    @property
    def ranks(self):
        return self.__ranks

    def hasFirstName(self, nameID):
        return nameID in self.__firstNames

    def hasLastName(self, nameID):
        return nameID in self.__lastNames

    def hasIcon(self, iconID):
        return iconID in self.__icons

    def getGroups(self, isPremium):
        if isPremium:
            return self.__premiumGroups
        else:
            return self.__normalGroups

    def getRoleRanks(self, roleName):
        if self.__roleRanks is not None:
            return self.__roleRanks.getRanksIDs(roleName)
        else:
            return component_constants.EMPTY_TUPLE
            return

    def getFirstName(self, nameID):
        if nameID in self.__firstNames:
            return self.__firstNames[nameID]
        else:
            return component_constants.EMPTY_STRING

    def getLastName(self, nameID):
        if nameID in self.__lastNames:
            return self.__lastNames[nameID]
        else:
            return component_constants.EMPTY_STRING

    def getIcon(self, iconID):
        if iconID in self.__icons:
            return self.__icons[iconID]
        else:
            return component_constants.EMPTY_STRING

    def getRank(self, rankID):
        if self.__ranks is not None:
            return self.__ranks.getRankByID(rankID)
        else:
            return
            return
