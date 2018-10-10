# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/ui/layouts.py
from collections import defaultdict
from dossiers2.custom.vehicle_layout import FALLOUT_ACHIEVEMENTS_BLOCK_LAYOUT, EPIC_BATTLE_ACHIEVEMENTS_BLOCK_LAYOUT
import nations
from constants import DOSSIER_TYPE
from dossiers2.ui import achievements
from dossiers2.custom import layouts as com_layouts, records
_AB = achievements.ACHIEVEMENT_BLOCK

def _7x7(achieveName):
    return (_AB.TEAM_7X7, achieveName)


def _total(achieveName):
    return (_AB.TOTAL, achieveName)


def _single(achieveName):
    return (_AB.SINGLE, achieveName)


def _single7x7(achieveName):
    return (_AB.SINGLE_7X7, achieveName)


def _fallout(achieveName):
    return (_AB.FALLOUT, achieveName)


def _epicBattle(achieveName):
    return (_AB.EPIC_BATTLE, achieveName)


_TANK_EXPERT_PREFIX = 'tankExpert'
_MECH_ENGINEER_PREFIX = 'mechanicEngineer'
_HIST_BATTLEFIELD_POSTFIX = 'battlefield'
TANK_EXPERT_GROUP = [_total(_TANK_EXPERT_PREFIX)]
MECH_ENGINEER_GROUP = [_total(_MECH_ENGINEER_PREFIX)]
for _nID, name in enumerate(nations.AVAILABLE_NAMES):
    TANK_EXPERT_GROUP.append(_total('%s%d' % (_TANK_EXPERT_PREFIX, _nID)))
    MECH_ENGINEER_GROUP.append(_total('%s%d' % (_MECH_ENGINEER_PREFIX, _nID)))

HISTORY_BATTLEFIELD_GROUP = []
PERSONAL_MISSIONS_GROUP = [_single('firstMerit'),
 _total('readyForBattleLT'),
 _total('readyForBattleMT'),
 _total('readyForBattleSPG'),
 _total('readyForBattleATSPG'),
 _total('readyForBattleALL'),
 _total('tankwomenProgress'),
 _total('readyForBattleAllianceUSSR'),
 _total('readyForBattleAllianceGermany'),
 _total('readyForBattleAllianceUSA'),
 _total('readyForBattleAllianceFrance'),
 _single('newMeritPM2')]
CHRISTMAS_QUESTS_GROUP = [_single('xmasTreeBronze'), _single('xmasTreeSilver'), _single('xmasTreeGold')]
HE17_QUESTS_GROUP = [_single('HE17A1'), _single('HE17A2'), _single('HE17A3')]
NY18_QUESTS_GROUP = [_single('NY18A1'), _single('NY18A2'), _single('NY18A3')]
IGNORED_BY_BATTLE_RESULTS = [achievements.MARK_OF_MASTERY_RECORD, _single7x7('victoryMarch')]
for record in records.RECORD_DB_IDS:
    if record[1] in ('maxXP', 'maxFrags', 'maxDamage', 'maxWinPoints', 'maxCoins'):
        IGNORED_BY_BATTLE_RESULTS.append(record)

_COMMON_DOSSIERS_TYPE = 0
_EXCLUDED_ACHIEVES = defaultdict(tuple, {})
_CUSTOM_ACHIEVES = defaultdict(tuple, {DOSSIER_TYPE.ACCOUNT: (achievements.WHITE_TIGER_RECORD, achievements.RARE_STORAGE_RECORD)})

def _getComLayoutRecordID(record):
    if record in TANK_EXPERT_GROUP:
        return (record[0], 'tankExpertStrg')
    return (record[0], 'mechanicEngineerStrg') if record in MECH_ENGINEER_GROUP else record


def _buildComLayoutSet(dossierType, comLayout):
    global _EXCLUDED_ACHIEVES
    result = set()
    for layout in comLayout:
        if hasattr(layout, 'recordsLayout'):
            result.update(set(((layout.name, r) for r in layout.recordsLayout)))
        result.add(achievements.makeAchievesStorageName(layout.name))

    for dt in (_COMMON_DOSSIERS_TYPE, dossierType):
        result -= set(_EXCLUDED_ACHIEVES[dt])
        result |= set(_CUSTOM_ACHIEVES[dt])

    return result


ACCOUNT_ACHIEVEMENT_LAYOUT = []
VEHICLE_ACHIEVEMENT_LAYOUT = []
TANKMAN_ACHIEVEMENT_LAYOUT = []
FORT_ACHIEVEMENT_LAYOUT = []
RATED7x7_ACHIEVEMENT_LAYOUT = []
CLUB_ACHIEVEMENT_LAYOUT = []
_layoutsMap = {}

def getAchievementsLayout(dossierType):
    global _layoutsMap
    return _layoutsMap[dossierType][0] if dossierType in _layoutsMap else tuple()


def isAchievementRegistered(record):
    return record in achievements.ACHIEVEMENTS


_MODE_ACHIEVEMENTS = defaultdict(set)

def getAchievementsByMode(mode):
    result = set()
    for modeID, achieves in _MODE_ACHIEVEMENTS.iteritems():
        if mode & modeID:
            result |= achieves

    return result


NEAREST_ACHIEVEMENTS = TANK_EXPERT_GROUP + MECH_ENGINEER_GROUP + [_total('mousebane'),
 _total('beasthunter'),
 _total('pattonValley'),
 _total('sinai'),
 _total('medalKnispel'),
 _total('medalCarius'),
 _total('medalAbrams'),
 _total('medalPoppel'),
 _total('medalKay'),
 _total('medalEkins'),
 _total('medalLeClerc'),
 _total('medalLavrinenko'),
 _total('readyForBattleLT'),
 _total('readyForBattleMT'),
 _total('readyForBattleHT'),
 _total('readyForBattleSPG'),
 _total('readyForBattleATSPG'),
 _7x7('geniusForWarMedal'),
 _7x7('wolfAmongSheepMedal'),
 _7x7('fightingReconnaissanceMedal'),
 _7x7('crucialShotMedal'),
 _7x7('forTacticalOperations'),
 _total('readyForBattleAllianceUSSR'),
 _total('readyForBattleAllianceGermany'),
 _total('readyForBattleAllianceUSA'),
 _total('readyForBattleAllianceFrance')]

def init():
    global _EXCLUDED_ACHIEVES
    global _layoutsMap
    global HISTORY_BATTLEFIELD_GROUP
    HISTORY_BATTLEFIELD_GROUP = [ _r for _r in achievements.ACHIEVEMENTS if str(_r[1]).endswith(_HIST_BATTLEFIELD_POSTFIX) ]
    _EXCLUDED_ACHIEVES = defaultdict(tuple, {_COMMON_DOSSIERS_TYPE: (achievements.MARK_OF_MASTERY_RECORD, achievements.MARK_ON_GUN_RECORD),
     DOSSIER_TYPE.VEHICLE: tuple((r for r, v in achievements.ACHIEVEMENTS.iteritems() if v['section'] == achievements.ACHIEVEMENT_TYPE.CLASS)) + (_7x7('wolfAmongSheepMedal'),
                            _7x7('geniusForWarMedal'),
                            _7x7('fightingReconnaissanceMedal'),
                            _7x7('crucialShotMedal'),
                            _7x7('forTacticalOperations'),
                            _7x7('promisingFighterMedal'),
                            _7x7('heavyFireMedal'),
                            _7x7('rangerMedal'),
                            _7x7('guerrillaMedal'),
                            _7x7('infiltratorMedal'),
                            _7x7('sentinelMedal'),
                            _7x7('prematureDetonationMedal'),
                            _7x7('bruteForceMedal')) + tuple(map(_fallout, FALLOUT_ACHIEVEMENTS_BLOCK_LAYOUT))})
    for _r in achievements.ACHIEVEMENTS.iterkeys():
        name = str(_r[1])
        if name.startswith(_TANK_EXPERT_PREFIX) and _r not in TANK_EXPERT_GROUP or name.startswith(_MECH_ENGINEER_PREFIX) and _r not in MECH_ENGINEER_GROUP:
            _EXCLUDED_ACHIEVES[_COMMON_DOSSIERS_TYPE] += (_r,)

    _layoutsMap = {DOSSIER_TYPE.ACCOUNT: (ACCOUNT_ACHIEVEMENT_LAYOUT, _buildComLayoutSet(DOSSIER_TYPE.ACCOUNT, com_layouts.accountDossierLayout)),
     DOSSIER_TYPE.VEHICLE: (VEHICLE_ACHIEVEMENT_LAYOUT, _buildComLayoutSet(DOSSIER_TYPE.VEHICLE, com_layouts.vehicleDossierLayout)),
     DOSSIER_TYPE.TANKMAN: (TANKMAN_ACHIEVEMENT_LAYOUT, _buildComLayoutSet(DOSSIER_TYPE.TANKMAN, com_layouts.tmanDossierLayout)),
     DOSSIER_TYPE.RATED7X7: (RATED7x7_ACHIEVEMENT_LAYOUT, _buildComLayoutSet(DOSSIER_TYPE.RATED7X7, com_layouts.rated7x7DossierLayout)),
     DOSSIER_TYPE.CLUB: (CLUB_ACHIEVEMENT_LAYOUT, _buildComLayoutSet(DOSSIER_TYPE.CLUB, com_layouts.clubDossierLayout))}
    for record, values in achievements.ACHIEVEMENTS.iteritems():
        _MODE_ACHIEVEMENTS[values['mode']].add(record)
        for uiLayout, comLayout in _layoutsMap.itervalues():
            if _getComLayoutRecordID(record) in comLayout:
                uiLayout.append(record)
