# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/tankmen_components.py
from items.components import component_constants
from items.components import legacy_stuff
from items.components import shared_components
from items.components import skills_constants

class GROUP_TAG(object):
    """Class contains all available tags in group configuration."""
    PASSPORT_REPLACEMENT_FORBIDDEN = 'passportReplacementForbidden'
    RESTRICTIONS = (PASSPORT_REPLACEMENT_FORBIDDEN,)
    RANGE = RESTRICTIONS


class Rank(legacy_stuff.LegacyStuff):
    """Class to provide information about rank. It is used on the client-side only."""
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
        """Gets name of rank. It equals name of section in xml file."""
        return self.__name

    @property
    def userString(self):
        """Get UTF-8 user-friendly name of rank or empty string."""
        if self.__i18n is not None:
            return self.__i18n.value
        else:
            return component_constants.EMPTY_STRING
            return

    @property
    def icon(self):
        """Get name of rank's icon with extension or empty string."""
        return self.__icon


class RanksSet(object):
    """Class contains set of ranks for specified nation. ID of rank equals index within internal list,
    and this component must be created at first time bacause of those IDs are used in other components."""
    __slots__ = ('__ranks', '__rankIDsByNames')

    def __init__(self):
        super(RanksSet, self).__init__()
        self.__ranks = []
        self.__rankIDsByNames = {}

    def __repr__(self):
        return 'RanksSet({})'.format(self.__rankIDsByNames.keys())

    def add(self, rank):
        """Adds rank to nation set.
        :param rank: instance of Rank.
        """
        self.__rankIDsByNames[rank.name] = len(self.__ranks)
        self.__ranks.append(rank)

    def getRankByID(self, rankID):
        """Gets instance of Rank by ID (index).
        :param rankID: integer containing index within internal list (ID).
        :return: instance of Rank or None.
        """
        if 0 <= rankID < len(self.__ranks):
            return self.__ranks[rankID]
        else:
            return None
            return None

    def getRankByName(self, name):
        """Gets instance of Rank by name.
        :param name: string containing name of rank.
        :return: instance of Rank or None.
        """
        if name in self.__rankIDsByNames:
            return self.__ranks[self.__rankIDsByNames[name]]
        else:
            return None
            return None

    def getIDByName(self, name):
        """Gets ID of rank by name.
        :param name: string containing name of rank.
        :return: integer containing index within internal list (ID).
        """
        if name in self.__rankIDsByNames:
            return self.__rankIDsByNames[name]
        raise KeyError('Name of rank "{}" is not found'.format(name))

    def generator(self):
        """Gets generator to iterate ranks."""
        for rank in self.__ranks:
            yield (self.__rankIDsByNames[rank.name], rank)


class RoleRanks(legacy_stuff.LegacyStuff):
    """Class to provide available ranks by role of tankman.
    Note: order in available ranks is fixed and used to pack/unpack to/from compact descriptor."""
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
        """Gets commander's available ranks."""
        return self.__ranks['commander']

    @property
    def radioman(self):
        """Gets radioman's available ranks."""
        return self.__ranks['radioman']

    @property
    def driver(self):
        """Gets driver's available ranks."""
        return self.__ranks['driver']

    @property
    def gunner(self):
        """Gets gunner's available ranks."""
        return self.__ranks['gunner']

    @property
    def loader(self):
        """Gets loader's available ranks."""
        return self.__ranks['loader']

    def getRanksIDs(self, roleName):
        """Gets tuple containing ID of ranks by name of tankman role.
        :param roleName: string containing name of tankman role.
        :return: tuple containing ID of ranks.
        """
        if roleName in self.__ranks:
            return self.__ranks[roleName]
        else:
            return component_constants.EMPTY_TUPLE

    def getRankID(self, roleName, rankIdx):
        """Gets integer containing ID of rank by name of role and index.
        :param roleName: string containing name of tankman role.
        :param rankIdx: index within internal list.
        :return: integer containing ID of rank or None.
        """
        ranks = self.getRanksIDs(roleName)
        if 0 <= rankIdx < len(ranks):
            return ranks[rankIdx]
        else:
            return None
            return None

    def setRanksIDs(self, roleName, roleIDs):
        """Sets tuple containing ID of ranks by name of tankman role.
        :param roleName: string containing name of tankman role.
        :param roleIDs: tuple containing ID of ranks.
        """
        if roleName not in skills_constants.ROLES:
            raise KeyError('Role {} is not found'.format(roleName))
        self.__ranks[roleName] = roleIDs


class NationGroup(legacy_stuff.LegacyStuff):
    """Class contains information about group of tankmen."""
    __slots__ = ('__isFemales', '__notInShop', '__firstNamesIDs', '__lastNamesIDs', '__iconsIDs', '__weight', '__tags')

    def __init__(self, isFemales, notInShop, firstNamesIDs, lastNamesIDs, iconsIDs, weight, tags):
        super(NationGroup, self).__init__()
        self.__isFemales = isFemales
        self.__notInShop = notInShop
        self.__firstNamesIDs = firstNamesIDs
        self.__lastNamesIDs = lastNamesIDs
        self.__iconsIDs = iconsIDs
        self.__weight = weight
        self.__tags = tags

    def __repr__(self):
        return 'NationGroup(isFemales={}, notInShop={}, weight={})'.format(self.__isFemales, self.__notInShop, self.__weight)

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


class NationConfig(legacy_stuff.LegacyStuff):
    """Class to holds nation-specific configuration of tankmen that are read
    from item_def/tankmen/<nation_name>.xml."""
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
        """Does config have first name by ID of name (index)."""
        return nameID in self.__firstNames

    def hasLastName(self, nameID):
        """Does config have last name by ID of name (index)."""
        return nameID in self.__lastNames

    def hasIcon(self, iconID):
        """Does config have icon by ID (index)."""
        return iconID in self.__icons

    def getGroups(self, isPremium):
        """Gets tuple of groups by premium flag."""
        if isPremium:
            return self.__premiumGroups
        else:
            return self.__normalGroups

    def getRoleRanks(self, roleName):
        """Gets tuple containing ID of ranks by name of role (commander, ...)."""
        if self.__roleRanks is not None:
            return self.__roleRanks.getRanksIDs(roleName)
        else:
            return component_constants.EMPTY_TUPLE
            return

    def getFirstName(self, nameID):
        """Gets string containing i18n key by ID of first name or empty string.
        This routine is used on the client-side only."""
        if nameID in self.__firstNames:
            return self.__firstNames[nameID]
        else:
            return component_constants.EMPTY_STRING

    def getLastName(self, nameID):
        """Gets string containing i18n key by ID of last name or empty string.
        This routine is used on the client-side only."""
        if nameID in self.__lastNames:
            return self.__lastNames[nameID]
        else:
            return component_constants.EMPTY_STRING

    def getIcon(self, iconID):
        """Gets string containing name of file with extension by ID of icon or empty string.
        This routine is used on the client-side only."""
        if iconID in self.__icons:
            return self.__icons[iconID]
        else:
            return component_constants.EMPTY_STRING

    def getRank(self, rankID):
        """Gets instance of Rank containing information about rank (user-friendly name, icon, ...) or None."""
        if self.__ranks is not None:
            return self.__ranks.getRankByID(rankID)
        else:
            return
            return
