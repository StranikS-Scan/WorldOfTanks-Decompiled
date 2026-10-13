# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/ui/achievements.py
import resource_helper
from debug_utils import LOG_CURRENT_EXCEPTION
from constants import IS_WEB
from soft_exception import SoftException
BATTLE_HERO_TEXTS = {'warrior': '#achievements:warrior',
 'invader': '#achievements:invader',
 'sniper': '#achievements:sniper',
 'defender': '#achievements:defender',
 'steelwall': '#achievements:steelwall',
 'supporter': '#achievements:supporter',
 'scout': '#achievements:scout',
 'evileye': '#achievements:evileye'}
BADGES_BLOCK = 'playerBadges'

class ACHIEVEMENT_BLOCK:
    CLIENT = 'client'
    TOTAL = 'achievements'
    TEAM_7X7 = 'achievements7x7'
    HISTORICAL = 'historicalAchievements'
    UNIQUE = 'uniqueAchievements'
    RARE = 'rareAchievements'
    FORT = 'fortAchievements'
    SINGLE = 'singleAchievements'
    SINGLE_7X7 = 'singleAchievementsRated7x7'
    CLAN = 'clanAchievements'
    RATED_7X7 = 'achievementsRated7x7'
    FALLOUT = 'falloutAchievements'
    EPIC_BATTLE = 'epicBattleAchievements'
    STEAM = 'steamAchievements'
    MT = 'mtAchievements'
    ALL = (CLIENT,
     TOTAL,
     TEAM_7X7,
     HISTORICAL,
     UNIQUE,
     RARE,
     FORT,
     SINGLE,
     CLAN,
     RATED_7X7,
     SINGLE_7X7,
     FALLOUT,
     EPIC_BATTLE,
     STEAM,
     MT)


class ACHIEVEMENT_MODE:
    RANDOM = 1
    TEAM_7X7 = 2
    HISTORICAL = 4
    RATED_7X7 = 8
    RANKED = 22
    EPIC_BATTLE = 16
    ALL = RANDOM | TEAM_7X7 | HISTORICAL | RATED_7X7 | RANKED | EPIC_BATTLE


class ACHIEVEMENT_TYPE:
    REPEATABLE = 'repeatable'
    CLASS = 'class'
    CUSTOM = 'custom'
    SERIES = 'series'
    SINGLE = 'single'
    ALL = (REPEATABLE,
     CLASS,
     CUSTOM,
     SERIES,
     SINGLE)


class ACHIEVEMENT_SECTION:
    EPIC = 'epic'
    BATTLE = 'battle'
    SPECIAL = 'special'
    CLASS = 'class'
    ACTION = 'action'
    MEMORIAL = 'memorial'
    GROUP = 'group'
    ALL = (EPIC,
     BATTLE,
     SPECIAL,
     CLASS,
     ACTION,
     MEMORIAL,
     GROUP)


_AT, _AS, _AB, _AM = (ACHIEVEMENT_TYPE,
 ACHIEVEMENT_SECTION,
 ACHIEVEMENT_BLOCK,
 ACHIEVEMENT_MODE)
DEFAULT_WEIGHT = -1

def makeAchievesStorageName(block):
    return (block, '')


RARE_STORAGE_RECORD = makeAchievesStorageName(_AB.RARE)
MARK_OF_MASTERY_RECORD = (_AB.TOTAL, 'markOfMastery')
MARK_ON_GUN_RECORD = (_AB.TOTAL, 'marksOnGun')
HONORED_RANK_RECORD = (_AB.CLIENT, 'honoredRank')
_MODE_CONVERTER = {'random': ACHIEVEMENT_MODE.RANDOM,
 'ranked': ACHIEVEMENT_MODE.RANKED,
 '7x7': ACHIEVEMENT_MODE.TEAM_7X7,
 'historical': ACHIEVEMENT_MODE.HISTORICAL,
 'rated7x7': ACHIEVEMENT_MODE.RATED_7X7,
 'epic_battle': ACHIEVEMENT_MODE.EPIC_BATTLE,
 'all': ACHIEVEMENT_MODE.ALL}
ACHIEVEMENTS = {}
ACHIEVEMENT_SECTIONS_ORDER = (_AS.BATTLE,
 _AS.SPECIAL,
 _AS.EPIC,
 _AS.GROUP,
 _AS.MEMORIAL,
 _AS.CLASS,
 _AS.ACTION)
ACHIEVEMENT_SECTIONS_INDICES = dict(((n, i) for i, n in enumerate(ACHIEVEMENT_SECTIONS_ORDER)))
BATTLE_ACHIEVES_WITH_RIBBON = ()
BATTLE_ACHIEVES_RIGHT = ()
FORT_BATTLE_ACHIEVES_RIGHT = ()
BATTLE_APPROACHABLE_ACHIEVES = ()

def getType(record):
    global ACHIEVEMENTS
    return ACHIEVEMENTS[record]['type'] if record in ACHIEVEMENTS else None


def getSection(record):
    return ACHIEVEMENTS[record]['section'] if record in ACHIEVEMENTS else None


def getMode(record):
    return ACHIEVEMENTS[record]['mode'] if record in ACHIEVEMENTS else None


def getWeight(record):
    return ACHIEVEMENTS[record]['weight'] if record in ACHIEVEMENTS else None


def init(achievesMappingXmlPath):
    global BATTLE_APPROACHABLE_ACHIEVES
    global BATTLE_ACHIEVES_WITH_RIBBON
    global BATTLE_ACHIEVES_RIGHT
    global FORT_BATTLE_ACHIEVES_RIGHT
    if IS_WEB:
        return
    ctx, section = resource_helper.getRoot(achievesMappingXmlPath)
    for ctx, subSection in resource_helper.getIterator(ctx, section['achievements']):
        try:
            item = resource_helper.readItem(ctx, subSection, name='achievement')
            if not item.name:
                continue
            block, name = tuple(item.name.split(':'))
            if block not in ACHIEVEMENT_BLOCK.ALL:
                raise SoftException('Unknown block name', (block, name))
            if 'type' not in item.value or item.value['type'] not in ACHIEVEMENT_TYPE.ALL:
                raise SoftException('Unknown achievement type', (block, name), item.value)
            if 'section' not in item.value or item.value['section'] not in ACHIEVEMENT_SECTION.ALL:
                raise SoftException('Unknown achievement section', (block, name), item.value)
            if 'mode' not in item.value or item.value['mode'] not in _MODE_CONVERTER:
                raise SoftException('Unknown achievement mode', (block, name), item.value)
            value = dict(item.value)
            value['mode'] = _MODE_CONVERTER[item.value['mode']]
            if 'weight' not in value:
                value['weight'] = -1.0
            ACHIEVEMENTS[block, name] = value
        except:
            LOG_CURRENT_EXCEPTION()

    BATTLE_ACHIEVES_WITH_RIBBON = tuple(resource_helper.readList(ctx, section['battleAchievesWithRibbon']).value)
    BATTLE_ACHIEVES_RIGHT = tuple(resource_helper.readList(ctx, section['battleResultsRight']).value)
    FORT_BATTLE_ACHIEVES_RIGHT = tuple(resource_helper.readList(ctx, section['fortBattleResultsRight']).value)
    BATTLE_APPROACHABLE_ACHIEVES = tuple(resource_helper.readList(ctx, section['approachableAchieves']).value)
    resource_helper.purgeResource(achievesMappingXmlPath)
