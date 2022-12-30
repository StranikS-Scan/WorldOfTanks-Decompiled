# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/tankmen_components.py
import weakref
import itertools
from constants import IS_CLIENT
from items.components import component_constants
from items.components import legacy_stuff
from items.components import shared_components
from items.components import skills_constants
from soft_exception import SoftException

class SPECIAL_VOICE_TAG(object):
    BUFFON = 'buffonSpecialVoice'
    SABATON = 'sabatonSpecialVoice'
    OFFSPRING = 'offspringSpecialVoice'
    RACER = 'racerSpecialVoice'
    RACER_EN = 'racerSpecialVoiceEn'
    CELEBRITY_2021 = 'celebrity21SpecialVoice'
    CELEBRITY_2022 = 'celebrity22SpecialVoice'
    CELEBRITY_2023 = 'celebrity23SpecialVoice'
    DAY_OF_COSMONAUTICS_21 = 'gagarin21_specialVoice'
    MIHO = 'mihoSpecialVoice'
    YHA = 'yhaSpecialVoice'
    QUICKY_BABY = 'quickyBabySpecialVoice'
    WITCHES_CREW = 'witchesSpecialVoice'
    BATTLE_OF_BLOGGERS = ('ru1_LebwaSpecialVoice', 'ru2_YushaSpecialVoice', 'ru3_Amway921SpecialVoice', 'ru4_KorbenDallasSpecialVoice', 'eu1_MailandSpecialVoice', 'eu2_Skill4ltuSpecialVoice', 'eu3_DezgamezSpecialVoice', 'eu4_AwesomeEpicGuysSpecialVoice')
    BATTLE_OF_BLOGGERS_2021 = ('bb21_ru1_Yusha_specialVoice', 'bb21_ru1_Vspishka_specialVoice', 'bb21_ru2_Amway921_specialVoice', 'bb21_ru2_Korbendailas_specialVoice', 'bb21_ru3_Lebwa_specialVoice', 'bb21_ru3_Inspirer_specialVoice', 'bb21_ru4_Evilgranny_specialVoice', 'bb21_ru4_Nearyou_specialVoice', 'bb21_eu1_Circon_specialVoice', 'bb21_eu2_Dakillzor_specialVoice', 'bb21_eu3_Newmulti2k_specialVoice', 'bb21_eu4_Orzanel_specialVoice', 'bb21_na1_Cabbagemechanic_specialVoice', 'bb21_na2_Tragicloss_specialVoice', 'bb21_na3_Cmdraf_specialVoice', 'bb21_asia1_Mastertortoise_specialVoice', 'bb21_asia2_Summertiger_specialVoice', 'bb21_asia3_Maharlika_specialVoice')
    G_I_JOE_TWITCH_2021 = ('duke_specialVoice', 'cobra_specialVoice')
    WHITE_TIGER_EVENT_2021 = ('letov_SpecialVoice', 'armand_SpecialVoice', 'elisa_SpecialVoice', 'krieger_SpecialVoice')
    WHITE_TIGER_EVENT_2022 = ('villanelle_SpecialVoice', 'ermelinda_SpecialVoice')
    SABATON_2021 = 'sabaton21_specialVoice'
    G_I_JOE_2022 = ('baroness22SpecialVoice', 'coverGirl22SpecialVoice')
    ALL = (BUFFON,
     SABATON,
     OFFSPRING,
     RACER,
     RACER_EN,
     CELEBRITY_2021,
     MIHO,
     YHA,
     CELEBRITY_2022,
     DAY_OF_COSMONAUTICS_21,
     SABATON_2021,
     QUICKY_BABY,
     WITCHES_CREW,
     CELEBRITY_2023) + BATTLE_OF_BLOGGERS + BATTLE_OF_BLOGGERS_2021 + G_I_JOE_TWITCH_2021 + WHITE_TIGER_EVENT_2021 + G_I_JOE_2022 + WHITE_TIGER_EVENT_2022


class SPECIAL_CREW_TAG(object):
    SABATON = 'sabatonCrew'
    OFFSPRING = 'offspringCrew'
    MIHO = 'mihoCrew'
    YHA = 'yhaCrew'
    WITCHES_CREW = 'witchesCrew'
    ALL = (SABATON,
     OFFSPRING,
     MIHO,
     YHA,
     WITCHES_CREW)


class GROUP_TAG(object):
    PASSPORT_REPLACEMENT_FORBIDDEN = 'passportReplacementForbidden'
    RESTRICTIONS = (PASSPORT_REPLACEMENT_FORBIDDEN,)
    RANGE = RESTRICTIONS + tuple(skills_constants.ROLES) + SPECIAL_VOICE_TAG.ALL + SPECIAL_CREW_TAG.ALL


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
        raise SoftException('Name of rank "{}" is not found'.format(name))

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
            raise SoftException('Role {} is not found'.format(roleName))
        self.__ranks[roleName] = roleIDs


class NationGroup(legacy_stuff.LegacyStuff):
    __slots__ = ('__name', '__isFemales', '__notInShop', '__firstNamesIDs', '__lastNamesIDs', '__iconsIDs', '__weight', '__tags', '__roles', '__groupID', '__weakref__')

    def __init__(self, groupID, name, isFemales, notInShop, firstNamesIDs, lastNamesIDs, iconsIDs, weight, tags, roles):
        super(NationGroup, self).__init__()
        self.__groupID = groupID
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
        return 'NationGroup(groupID={}, name={}, isFemales={}, notInShop={}, weight={}, tags={}, roles={})'.format(self.__groupID, self.__name, self.__isFemales, self.__notInShop, self.__weight, self.__tags, self.__roles)

    @property
    def groupID(self):
        return self.__groupID

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
    def rolesList(self):
        return list(self.__roles)

    @property
    def isUnique(self):
        return 1 == len(self.__firstNamesIDs) * len(self.__lastNamesIDs) * len(self.__iconsIDs)


class NationConfig(legacy_stuff.LegacyStuff):
    __slots__ = ('__name', '__normalGroups', '__premiumGroups', '__roleRanks', '__firstNames', '__lastNames', '__icons', '__ranks', '__lastNameIndex')

    def __init__(self, name, normalGroups=None, premiumGroups=None, roleRanks=None, firstNames=None, lastNames=None, icons=None, ranks=None):
        super(NationConfig, self).__init__()
        self.__name = name
        self.__normalGroups = normalGroups or component_constants.EMPTY_DICT
        self.__premiumGroups = premiumGroups or component_constants.EMPTY_DICT
        self.__roleRanks = roleRanks
        self.__firstNames = firstNames or {}
        self.__lastNames = lastNames or {}
        self.__icons = icons or {}
        self.__ranks = ranks
        self.__lastNameIndex = {}
        if not IS_CLIENT:
            for gid, g in itertools.chain(normalGroups.iteritems(), premiumGroups.iteritems()):
                for lnid in g.lastNames:
                    self.__lastNameIndex[lnid] = weakref.proxy(g)

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

    def getExtensionLessIcon(self, iconID):
        if iconID in self.__icons:
            return self.__icons[iconID].split('.png')[0]
        else:
            return component_constants.EMPTY_STRING

    def getRank(self, rankID):
        if self.__ranks is not None:
            return self.__ranks.getRankByID(rankID)
        else:
            return
            return

    def getGroupByLastName(self, nameID):
        return self.__lastNameIndex.get(nameID)
