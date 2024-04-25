# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/tankmen_components.py
from debug_utils import LOG_ERROR
import typing
import weakref
import itertools
from constants import IS_CLIENT
from items.components import component_constants
from items.components import legacy_stuff
from items.components import shared_components
from items.components import skills_constants
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Set, Union

class SPECIAL_VOICE_TAG(object):
    ARIA_2023 = 'AriaZhorikSpecialVoice'
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
    HAND_OF_BLOOD = 'handOfBloodSpecialVoice'
    HW_CREW = 'crewHWvoice'
    ARIA_CREW = 'ariaCrew'
    BATTLE_OF_BLOGGERS = ('ru1_LebwaSpecialVoice', 'ru2_YushaSpecialVoice', 'ru3_Amway921SpecialVoice', 'ru4_KorbenDallasSpecialVoice', 'eu1_MailandSpecialVoice', 'eu2_Skill4ltuSpecialVoice', 'eu3_DezgamezSpecialVoice', 'eu4_AwesomeEpicGuysSpecialVoice')
    BATTLE_OF_BLOGGERS_2021 = ('bb21_ru1_Yusha_specialVoice', 'bb21_ru1_Vspishka_specialVoice', 'bb21_ru2_Amway921_specialVoice', 'bb21_ru2_Korbendailas_specialVoice', 'bb21_ru3_Lebwa_specialVoice', 'bb21_ru3_Inspirer_specialVoice', 'bb21_ru4_Evilgranny_specialVoice', 'bb21_ru4_Nearyou_specialVoice', 'bb21_eu1_Circon_specialVoice', 'bb21_eu2_Dakillzor_specialVoice', 'bb21_eu3_Newmulti2k_specialVoice', 'bb21_eu4_Orzanel_specialVoice', 'bb21_na1_Cabbagemechanic_specialVoice', 'bb21_na2_Tragicloss_specialVoice', 'bb21_na3_Cmdraf_specialVoice', 'bb21_asia1_Mastertortoise_specialVoice', 'bb21_asia2_Summertiger_specialVoice', 'bb21_asia3_Maharlika_specialVoice')
    G_I_JOE_TWITCH_2021 = ('duke_specialVoice', 'cobra_specialVoice')
    WHITE_TIGER_EVENT_2021 = ('letov_SpecialVoice', 'armand_SpecialVoice', 'elisa_SpecialVoice', 'krieger_SpecialVoice')
    WHITE_TIGER_EVENT_2022 = ('villanelle_SpecialVoice', 'ermelinda_SpecialVoice')
    SABATON_2021 = 'sabaton21_specialVoice'
    G_I_JOE_2022 = ('baroness22SpecialVoice', 'coverGirl22SpecialVoice')
    BPH_2022 = ('commander_bph_2022_1', 'commander_bph_2022_2', 'commander_bph_2022_3', 'commander_bph_2022_4')
    BPH_MT_2022 = ('IvanCarevichSpecialVoice', 'VasilisaSpecialVoice', 'KashcheiSpecialVoice', 'BabaYagaSpecialVoice')
    HW_2023 = ('IvanCarevichHWSpecialVoice', 'VasilisaHWSpecialVoice', 'KashcheiHWSpecialVoice', 'BabaYagaHWSpecialVoice', 'KatrinaHWSpecialVoice')
    MOSFILM_2023 = ('TrusSpecialVoice', 'BalbesSpecialVoice', 'ByvalySpecialVoice')
    KIN_DZA_DZA_2024 = ('UefSpecialVoice', 'BiSpecialVoice', 'DyadyaVovaSpecialVoice', 'ScripachSpecialVoice')
    ALL = (ARIA_2023,
     BUFFON,
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
     HW_CREW,
     CELEBRITY_2023,
     HAND_OF_BLOOD) + BATTLE_OF_BLOGGERS + BATTLE_OF_BLOGGERS_2021 + G_I_JOE_TWITCH_2021 + WHITE_TIGER_EVENT_2021 + G_I_JOE_2022 + WHITE_TIGER_EVENT_2022 + BPH_2022 + BPH_MT_2022 + MOSFILM_2023 + HW_2023 + KIN_DZA_DZA_2024


class SPECIAL_CREW_TAG(object):
    SABATON = 'sabatonCrew'
    OFFSPRING = 'offspringCrew'
    MIHO = 'mihoCrew'
    YHA = 'yhaCrew'
    WITCHES_CREW = 'witchesCrew'
    HW_CREW = 'hwCrew'
    ARIA_CREW = 'ariaCrew'
    ALL = (SABATON,
     OFFSPRING,
     MIHO,
     YHA,
     WITCHES_CREW,
     HW_CREW,
     ARIA_CREW)


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
        return self.__firstNames.get(nameID, component_constants.EMPTY_STRING)

    def getLastName(self, nameID):
        return self.__lastNames.get(nameID, component_constants.EMPTY_STRING)

    def getIcon(self, iconID):
        return self.__icons.get(iconID, component_constants.EMPTY_STRING)

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


class LoreGroupComponent(object):
    __slots__ = 'descr_by_nation'
    DEFAULT = 'default'

    def __init__(self, descr):
        self.descr_by_nation = {}
        self.addDescrForNation(LoreGroupComponent.DEFAULT, descr)

    def addDescrForNation(self, nation, descr):
        if nation in self.descr_by_nation:
            LOG_ERROR('Lore description: {0} for nation: {1}, already exist '.format(descr, nation))
        self.descr_by_nation[nation] = descr

    def getDescrForNation(self, nation):
        return self.descr_by_nation[nation] if nation in self.descr_by_nation else self.descr_by_nation[LoreGroupComponent.DEFAULT]


class LoreComponent(object):
    __slots__ = ('descr_by_group',)
    SECTION = 'descr_by_group'
    NATION_SECTION = 'nations'
    __DEFAULT = 'default'

    def __init__(self):
        self.descr_by_group = {}

    def addDescrForGroup(self, group, descr):
        if group in self.descr_by_group:
            LOG_ERROR('Description: {0} for group: {1}, already exist '.format(group, descr))
        self.descr_by_group[group] = LoreGroupComponent(descr)

    def addNationDescrForGroup(self, group, naiton, descr):
        self.descr_by_group[group].addDescrForNation(naiton, descr)

    def getLoreDescrForGroup(self, group, nation=LoreGroupComponent.DEFAULT, isDefault=False):
        result = ''
        if group in self.descr_by_group:
            result = self.descr_by_group[group].getDescrForNation(nation)
        elif isDefault:
            result = self.descr_by_group[LoreComponent.__DEFAULT].getDescrForNation(LoreGroupComponent.DEFAULT)
        return result

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)
