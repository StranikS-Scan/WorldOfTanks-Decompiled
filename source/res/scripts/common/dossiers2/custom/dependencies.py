# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/dependencies.py
import time
from functools import partial
from dossiers2.custom.config import RECORD_CONFIGS
from dossiers2.custom.cache import getCache
from dossiers2.custom.utils import getVehicleNationID
from items.components.ny_constants import CURRENT_YEAR_BADGE_ID, PREVIOUS_YEARS_BADGE_IDS
_SECONDS_IN_DAY = 86400
A15X15_STATS_DEPENDENCIES = {}

def _set_A15X15_STATS_DEPENDENCIES():
    global A15X15_STATS_DEPENDENCIES
    A15X15_STATS_DEPENDENCIES.update({'winAndSurvived': [_updateMedalAbrams],
     'frags': [_updateMedalCarius],
     'frags8p': [_updateMedalEkins],
     'damageDealt': [_updateMedalKnispel],
     'damageReceived': [_updateMedalKnispel],
     'spotted': [_updateMedalPoppel],
     'capturePoints': [_updateMedalLeClerc],
     'droppedCapturePoints': [_updateMedalLavrinenko]})


A30X30_STATS_DEPENDENCIES = {}

def _set_A30X30_STATS_DEPENDENCIES():
    global A30X30_STATS_DEPENDENCIES
    A30X30_STATS_DEPENDENCIES.update({'winAndSurvived': [_updateMedalAbrams],
     'frags': [_updateMedalCarius],
     'frags8p': [_updateMedalEkins],
     'damageDealt': [_updateMedalKnispel],
     'damageReceived': [_updateMedalKnispel],
     'spotted': [_updateMedalPoppel],
     'capturePoints': [_updateMedalLeClerc],
     'droppedCapturePoints': [_updateMedalLavrinenko]})


A7X7_STATS_DEPENDENCIES = {}

def _set_A7X7_STATS_DEPENDENCIES():
    global A7X7_STATS_DEPENDENCIES
    A7X7_STATS_DEPENDENCIES.update({'winAndSurvived': [_updateMedalAbrams],
     'frags': [_updateMedalCarius],
     'frags8p': [_updateMedalEkins],
     'damageDealt': [_updateMedalKnispel],
     'damageReceived': [_updateMedalKnispel],
     'spotted': [_updateMedalPoppel],
     'capturePoints': [_updateMedalLeClerc],
     'droppedCapturePoints': [_updateMedalLavrinenko],
     'wins': [_updateForTacticalOperations]})


ACHIEVEMENT15X15_DEPENDENCIES = {}

def _set_ACHIEVEMENT15X15_DEPENDENCIES():
    global ACHIEVEMENT15X15_DEPENDENCIES
    ACHIEVEMENT15X15_DEPENDENCIES.update({'warrior': [_updateBattleHeroes, _updateSteamForWarriorMedal],
     'invader': [_updateBattleHeroes],
     'sniper': [_updateBattleHeroes],
     'defender': [_updateBattleHeroes],
     'steelwall': [_updateBattleHeroes, _updateSteamForSteelWallMedal],
     'supporter': [_updateBattleHeroes],
     'scout': [_updateBattleHeroes],
     'evileye': [_updateBattleHeroes],
     'battleHeroes': [_updateMedalKay, _updateSteamBattleHeroes],
     'fragsBeast': [_updateBeasthunter],
     'fragsSinai': [_updateSinai],
     'fragsPatton': [_updatePattonValley],
     'sniperSeries': [_updateMaxSniperSeries],
     'maxSniperSeries': [_updateTitleSniper],
     'invincibleSeries': [_updateMaxInvincibleSeries],
     'maxInvincibleSeries': [_updateInvincible],
     'diehardSeries': [_updateMaxDiehardSeries],
     'maxDiehardSeries': [_updateDiehard],
     'killingSeries': [_updateMaxKillingSeries],
     'maxKillingSeries': [_updateHandOfDeath],
     'piercingSeries': [_updateMaxPiercingSeries],
     'maxPiercingSeries': [_updateArmorPiercer],
     'maxAimerSeries': [_updateAimer],
     'sniper2': [_updateBattleHeroes],
     'mainGun': [_updateBattleHeroes],
     'WFC2014WinSeries': [_updateMaxWFC2014WinSeries],
     'deathTrackWinSeries': [_updateMaxDeathTrackWinSeries],
     'tankwomenProgress': [_updateTankwomen],
     'EFC2016WinSeries': [_updateMaxEFC2016WinSeries],
     'rankedBattlesHeroProgress': [_updateRankedBattlesHeroProgress],
     'rankedStayingCounter': [_updateRankedStayingPower],
     'rankedDivisionCounter': [_updateRankedDivisionFighter],
     'RP2018sergeantCounter': [_updateRP2018sergeant],
     'bonecrusher': [_updateSteamForBonecrusherMedal]})


ACHIEVEMENT7X7_DEPENDENCIES = {}

def _set_ACHIEVEMENT7X7_DEPENDENCIES():
    global ACHIEVEMENT7X7_DEPENDENCIES
    ACHIEVEMENT7X7_DEPENDENCIES.update({'wolfAmongSheep': [_updateWolfAmongSheepMedal],
     'geniusForWar': [_updateGeniusForWarMedal],
     'crucialShot': [_updateCrucialShotMedal],
     'tacticalBreakthroughSeries': [_updateMaxTacticalBreakthroughSeries],
     'maxTacticalBreakthroughSeries': [_updateTacticalBreakthrough, _updateAwardCount],
     'fightingReconnaissance': [_updateFightingReconnaissanceMedal],
     'pyromaniac': [_updatePyromaniacMedal],
     'ranger': [_updateRangerMedal],
     'promisingFighter': [_updatePromisingFighterMedal],
     'heavyFire': [_updateHeavyFireMedal],
     'fireAndSteel': [_updateFireAndSteelMedal],
     'guerrilla': [_updateGuerrillaMedal],
     'bruteForce': [_updateBruteForceMedal],
     'prematureDetonation': [_updatePrematureDetonationMedal],
     'sentinel': [_updateSentinelMedal],
     'infiltrator': [_updateInfiltratorMedal],
     'wolfAmongSheepMedal': [_updateAwardCount, _updateBattleHeroes],
     'geniusForWarMedal': [_updateAwardCount, _updateBattleHeroes],
     'fightingReconnaissanceMedal': [_updateAwardCount],
     'crucialShotMedal': [_updateAwardCount],
     'promisingFighterMedal': [_updateAwardCount],
     'heavyFireMedal': [_updateAwardCount],
     'rangerMedal': [_updateAwardCount],
     'fireAndSteelMedal': [_updateAwardCount],
     'pyromaniacMedal': [_updateAwardCount],
     'guerrillaMedal': [_updateAwardCount],
     'infiltratorMedal': [_updateAwardCount],
     'sentinelMedal': [_updateAwardCount],
     'prematureDetonationMedal': [_updateAwardCount],
     'bruteForceMedal': [_updateAwardCount],
     'kingOfTheHill': [_updateAwardCount],
     'armoredFist': [_updateAwardCount],
     'godOfWar': [_updateAwardCount],
     'willToWinSpirit': [_updateAwardCount],
     'noMansLand': [_updateAwardCount],
     'forTacticalOperations': [_updateAwardCount],
     'awardCount': [_updateBattleTested]})


ACHIEVEMENTRATED7X7_DEPENDENCIES = {}

def _set_ACHIEVEMENTRATED7X7_DEPENDENCIES():
    global ACHIEVEMENTRATED7X7_DEPENDENCIES
    ACHIEVEMENTRATED7X7_DEPENDENCIES.update({'victoryMarchSeries': [_updateMaxVictoryMarchSeries, _updateVictoryMarch]})


HISTORICAL_ACHIEVEMENTS_DEPENDENCIES = {}

def _set_HISTORICAL_ACHIEVEMENTS_DEPENDENCIES():
    global HISTORICAL_ACHIEVEMENTS_DEPENDENCIES
    HISTORICAL_ACHIEVEMENTS_DEPENDENCIES.update({'bothSidesWins': [_updateMakerOfHistoryMedal],
     'weakVehiclesWins': [_updateGuardsManMedal]})


HISTORICAL_STATS_DEPENDENCIES = {}

def _set_HISTORICAL_STATS_DEPENDENCIES():
    global HISTORICAL_STATS_DEPENDENCIES
    HISTORICAL_STATS_DEPENDENCIES.update({'winAndSurvived': [_updateMedalAbrams],
     'frags': [_updateMedalCarius],
     'frags8p': [_updateMedalEkins],
     'damageDealt': [_updateMedalKnispel],
     'damageReceived': [_updateMedalKnispel],
     'spotted': [_updateMedalPoppel],
     'capturePoints': [_updateMedalLeClerc],
     'droppedCapturePoints': [_updateMedalLavrinenko]})


FORT_BATTLES_STATS_DEPENDENCIES = {}

def _set_FORT_BATTLES_STATS_DEPENDENCIES():
    global FORT_BATTLES_STATS_DEPENDENCIES
    FORT_BATTLES_STATS_DEPENDENCIES.update({'winAndSurvived': [_updateMedalAbrams],
     'frags': [_updateMedalCarius],
     'frags8p': [_updateMedalEkins],
     'damageDealt': [_updateMedalKnispel],
     'damageReceived': [_updateMedalKnispel],
     'spotted': [_updateMedalPoppel],
     'capturePoints': [_updateMedalLeClerc],
     'droppedCapturePoints': [_updateMedalLavrinenko]})


FORT_SORTIES_STATS_DEPENDENCIES = {}

def _set_FORT_SORTIES_STATS_DEPENDENCIES():
    global FORT_SORTIES_STATS_DEPENDENCIES
    FORT_SORTIES_STATS_DEPENDENCIES.update({'winAndSurvived': [_updateMedalAbrams],
     'frags': [_updateMedalCarius],
     'frags8p': [_updateMedalEkins],
     'damageDealt': [_updateMedalKnispel],
     'damageReceived': [_updateMedalKnispel],
     'spotted': [_updateMedalPoppel],
     'capturePoints': [_updateMedalLeClerc],
     'droppedCapturePoints': [_updateMedalLavrinenko],
     'wins': [_updateSoldierOfFortune]})


FORT_ACHIEVEMENTS_DEPENDENCIES = {}

def _set_FORT_ACHIEVEMENTS_DEPENDENCIES():
    pass


SINGLE_ACHIEVEMENTS_DEPENDENCIES = {}

def _set_SINGLE_ACHIEVEMENTS_DEPENDENCIES():
    global SINGLE_ACHIEVEMENTS_DEPENDENCIES
    SINGLE_ACHIEVEMENTS_DEPENDENCIES.update({'bootcampMedal': [_updateSteamBootcamp]})


STEAM_ACHIEVEMENT_DEPENDENCIES = {}

def _set_STEAM_ACHIEVEMENT_DEPENDENCIES():
    global STEAM_ACHIEVEMENT_DEPENDENCIES
    STEAM_ACHIEVEMENT_DEPENDENCIES.update({'steamBattleCredits': [_updateSteamBattleCredits],
     'steamBattleXP': [_updateSteamBattleXP],
     'steamFreeXP': [_updateSteamFreeXP],
     'steamMasteryMarks': [_updateSteamMasteryMarksMedals],
     'steamBasePoints': [_updateSteamBasePoints],
     'steamHardCharacter': [_updateSteamHardCharacterMedal],
     'steamMedium': [_updatesteamMediumMedal],
     'steamATSPG': [_updateSteamATSPGMedal],
     'steamBreakThrough': [_updateSteamBreakThroughMedal],
     'steamStop': [_updateSteamStopMedal],
     'steamReconnoiter': [_updateSteamReconnoiterMedal],
     'steamPotentialStun': [_updateSteamPotentialStunMedal],
     'steamMileage': [_updateSteamMileageMedal],
     'steamTopLeague': [_updateSteamTopLeagueMedal],
     'steamSpotted': [_updateSteamSpottedMedal],
     'steamFrags': [_updateSteamFragsMedals],
     'steamBattleHeroes': [_updateSteamOrderMedal]})


VEH_TYPE_FRAGS_DEPENDENCIES = {}

def _set_VEH_TYPE_FRAGS_DEPENDENCIES():
    global VEH_TYPE_FRAGS_DEPENDENCIES
    cache = getCache()
    VEH_TYPE_FRAGS_DEPENDENCIES.update({cache['mausTypeCompDescr']: [_updateMousebane],
     '_insert_': [_updateTankExpert]})


CLAN_STATS_DEPENDENCIES = {}

def _set_CLAN_STATS_DEPENDENCIES():
    global CLAN_STATS_DEPENDENCIES
    CLAN_STATS_DEPENDENCIES.update({'battlesCount': [_updateMedalRotmistrov]})


CLUB_BATTLES_STAT_DEPENDENCIES = {}

def _set_CLUB_BATTLES_STAT_DEPENDENCIES():
    global CLUB_BATTLES_STAT_DEPENDENCIES
    CLUB_BATTLES_STAT_DEPENDENCIES.update({'wins': [_updateStrategicOperations]})


CLUB_ACHIEVEMENTS_DEPENDENCIES = {}

def _set_CLUB_ACHIEVEMENTS_DEPENDENCIES():
    global CLUB_ACHIEVEMENTS_DEPENDENCIES
    CLUB_ACHIEVEMENTS_DEPENDENCIES.update({'victoryMarchSeries': [_updateMaxVictoryMarchSeries, _updateClubVictoryMarch]})


GLOBAL_MAP_STATS_DEPENDENCIES = {}

def _set_GLOBAL_MAP_STATS_DEPENDENCIES():
    global GLOBAL_MAP_STATS_DEPENDENCIES
    GLOBAL_MAP_STATS_DEPENDENCIES.update({'battlesCount': [_updateMedalRotmistrov],
     'winAndSurvived': [_updateMedalAbrams],
     'frags': [_updateMedalCarius],
     'frags8p': [_updateMedalEkins],
     'damageDealt': [_updateMedalKnispel],
     'damageReceived': [_updateMedalKnispel],
     'spotted': [_updateMedalPoppel],
     'capturePoints': [_updateMedalLeClerc],
     'droppedCapturePoints': [_updateMedalLavrinenko]})


FALLOUT_STATS_DEPENDENCIES = {}

def _set_FALLOUT_STATS_DEPENDENCIES():
    global FALLOUT_STATS_DEPENDENCIES
    FALLOUT_STATS_DEPENDENCIES.update({'avatarKills': [_updateStormLord],
     'winPoints': [_updateWinnerLaurels]})


def _updateRankedBadge(dossierDescr, dossierBlockDescr, key, value, prevValue):
    eventsEnabled = dossierBlockDescr.eventsEnabled
    if eventsEnabled:
        dossierBlockDescr.eventsEnabled = False
    dossierBlockDescr[key] = int(time.time()) / _SECONDS_IN_DAY if value == 1 else 0
    if eventsEnabled:
        dossierBlockDescr.eventsEnabled = True


RANKED_STATS_DEPENDENCIES = {}

def _set_RANKED_STATS_DEPENDENCIES():
    global RANKED_STATS_DEPENDENCIES
    RANKED_STATS_DEPENDENCIES.update({'winAndSurvived': [_updateMedalAbrams],
     'frags': [_updateMedalCarius],
     'frags8p': [_updateMedalEkins],
     'damageDealt': [_updateMedalKnispel],
     'damageReceived': [_updateMedalKnispel],
     'spotted': [_updateMedalPoppel],
     'capturePoints': [_updateMedalLeClerc],
     'droppedCapturePoints': [_updateMedalLavrinenko]})


EPIC_BATTLE_STATS_DEPENDENCIES = {}

def _set_EPIC_BATTLE_STATS_DEPENDENCIES():
    pass


PLAYER_BADGES_DEPENDENCIES = {}

def _set_PLAYER_BADGES_DEPENDENCIES():
    PLAYER_BADGES_DEPENDENCIES.update({CURRENT_YEAR_BADGE_ID: [_updateNYBadges]})


def _updateMedalCarius(dossierDescr, dossierBlockDescr, key, value, prevValue):
    frags = 0
    for block in ('a15x15', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'globalMapCommon', 'globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute', 'a30x30'):
        if dossierDescr.isBlockInLayout(block):
            if block in dossierDescr:
                frags += dossierDescr[block]['frags']

    medalCariusCfg = RECORD_CONFIGS['medalCarius']
    maxMedalClass = len(medalCariusCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if frags >= medalCariusCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['achievements']['medalCarius']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['achievements']['medalCarius'] = medalClass


def _updateMedalKnispel(dossierDescr, dossierBlockDescr, key, value, prevValue):
    damage = 0
    for block in ('a15x15', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'globalMapCommon', 'globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute', 'a30x30'):
        if dossierDescr.isBlockInLayout(block):
            if block in dossierDescr:
                damage += dossierDescr[block]['damageDealt']
                damage += dossierDescr[block]['damageReceived']

    medalKnispelCfg = RECORD_CONFIGS['medalKnispel']
    maxMedalClass = len(medalKnispelCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if damage >= medalKnispelCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['achievements']['medalKnispel']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['achievements']['medalKnispel'] = medalClass


def _updateMedalPoppel(dossierDescr, dossierBlockDescr, key, value, prevValue):
    spotted = 0
    for block in ('a15x15', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'globalMapCommon', 'globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute', 'a30x30'):
        if dossierDescr.isBlockInLayout(block):
            if block in dossierDescr:
                spotted += dossierDescr[block]['spotted']

    medalPoppelCfg = RECORD_CONFIGS['medalPoppel']
    maxMedalClass = len(medalPoppelCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if spotted >= medalPoppelCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['achievements']['medalPoppel']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['achievements']['medalPoppel'] = medalClass


def _updateMedalLeClerc(dossierDescr, dossierBlockDescr, key, value, prevValue):
    capturePoints = 0
    for block in ('a15x15', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'globalMapCommon', 'globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute', 'a30x30'):
        if dossierDescr.isBlockInLayout(block):
            if block in dossierDescr:
                capturePoints += dossierDescr[block]['capturePoints']

    medalLeClercCfg = RECORD_CONFIGS['medalLeClerc']
    maxMedalClass = len(medalLeClercCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if capturePoints >= medalLeClercCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['achievements']['medalLeClerc']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['achievements']['medalLeClerc'] = medalClass


def _updateMedalLavrinenko(dossierDescr, dossierBlockDescr, key, value, prevValue):
    droppedCapturePoints = 0
    for block in ('a15x15', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'globalMapCommon', 'globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute', 'a30x30'):
        if dossierDescr.isBlockInLayout(block):
            if block in dossierDescr:
                droppedCapturePoints += dossierDescr[block]['droppedCapturePoints']

    medalLavrinenkoCfg = RECORD_CONFIGS['medalLavrinenko']
    maxMedalClass = len(medalLavrinenkoCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if droppedCapturePoints >= medalLavrinenkoCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['achievements']['medalLavrinenko']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['achievements']['medalLavrinenko'] = medalClass


def _updateBattleHeroes(dossierDescr, dossierBlockDescr, key, value, prevValue):
    dossierDescr['achievements']['battleHeroes'] += value - prevValue


def _updateSteamBattleHeroes(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if dossierDescr.isBlockInLayout('steamAchievements') and not dossierDescr['steamAchievements']['steamOrderMedal']:
        dossierDescr['steamAchievements']['steamBattleHeroes'] += value - prevValue


def _updateTankwomen(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['tankwomen']:
        dossierDescr['singleAchievements']['tankwomen'] = 1
        dossierDescr.addPopUp('singleAchievements', 'tankwomen', 1)


def _updateMedalKay(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalKayCfg = RECORD_CONFIGS['medalKay']
    maxMedalClass = len(medalKayCfg)
    battleHeroes = dossierBlockDescr['battleHeroes']
    for medalClass in xrange(1, maxMedalClass + 1):
        if battleHeroes >= medalKayCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierBlockDescr['medalKay']
    if curClass == 0 or curClass > medalClass:
        dossierBlockDescr['medalKay'] = medalClass


def _updateMedalAbrams(dossierDescr, dossierBlockDescr, key, value, prevValue):
    winAndSurvived = 0
    for block in ('a15x15', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'globalMapCommon', 'globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute', 'a30x30'):
        if dossierDescr.isBlockInLayout(block):
            if block in dossierDescr:
                winAndSurvived += dossierDescr[block]['winAndSurvived']

    medalAbramsCfg = RECORD_CONFIGS['medalAbrams']
    maxMedalClass = len(medalAbramsCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if winAndSurvived >= medalAbramsCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['achievements']['medalAbrams']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['achievements']['medalAbrams'] = medalClass


def _updateMedalEkins(dossierDescr, dossierBlockDescr, key, value, prevValue):
    frags8p = 0
    for block in ('a15x15', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'globalMapCommon', 'globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute', 'a30x30'):
        if dossierDescr.isBlockInLayout(block):
            if block in dossierDescr:
                frags8p += dossierDescr[block]['frags8p']

    medalEkinsCfg = RECORD_CONFIGS['medalEkins']
    maxMedalClass = len(medalEkinsCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if frags8p >= medalEkinsCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['achievements']['medalEkins']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['achievements']['medalEkins'] = medalClass


def _updateBeasthunter(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medals, series = divmod(value, RECORD_CONFIGS['beasthunter'])
    if dossierBlockDescr['beasthunter'] != medals:
        dossierBlockDescr['beasthunter'] = medals


def _updateSinai(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medals, series = divmod(value, RECORD_CONFIGS['sinai'])
    if dossierBlockDescr['sinai'] != medals:
        dossierBlockDescr['sinai'] = medals


def _updatePattonValley(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medals, series = divmod(value, RECORD_CONFIGS['pattonValley'])
    if dossierBlockDescr['pattonValley'] != medals:
        dossierBlockDescr['pattonValley'] = medals


def _updateMaxSniperSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxSniperSeries']:
        dossierBlockDescr['maxSniperSeries'] = value


def _updateTitleSniper(dossierDescr, dossierBlockDescr, key, value, prevValue, block='singleAchievements'):
    if value >= RECORD_CONFIGS['titleSniper']:
        dossierDescr[block]['titleSniper'] = 1
        dossierDescr.addPopUp(block, 'titleSniper', 1)


def _updateMaxInvincibleSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxInvincibleSeries']:
        dossierBlockDescr['maxInvincibleSeries'] = value


def _updateInvincible(dossierDescr, dossierBlockDescr, key, value, prevValue, block='singleAchievements'):
    if value >= RECORD_CONFIGS['invincible']:
        dossierDescr[block]['invincible'] = 1
        dossierDescr.addPopUp(block, 'invincible', 1)


def _updateMaxDiehardSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxDiehardSeries']:
        dossierBlockDescr['maxDiehardSeries'] = value


def _updateDiehard(dossierDescr, dossierBlockDescr, key, value, prevValue, block='singleAchievements'):
    if value >= RECORD_CONFIGS['diehard']:
        dossierDescr[block]['diehard'] = 1
        dossierDescr.addPopUp(block, 'diehard', 1)


def _updateMaxKillingSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxKillingSeries']:
        dossierBlockDescr['maxKillingSeries'] = value


def _updateHandOfDeath(dossierDescr, dossierBlockDescr, key, value, prevValue, block='singleAchievements'):
    if value >= RECORD_CONFIGS['handOfDeath']:
        dossierDescr[block]['handOfDeath'] = 1
        dossierDescr.addPopUp(block, 'handOfDeath', 1)


def _updateMaxPiercingSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxPiercingSeries']:
        dossierBlockDescr['maxPiercingSeries'] = value


def _updateArmorPiercer(dossierDescr, dossierBlockDescr, key, value, prevValue, block='singleAchievements'):
    if value >= RECORD_CONFIGS['armorPiercer']:
        dossierDescr[block]['armorPiercer'] = 1
        dossierDescr.addPopUp(block, 'armorPiercer', 1)


def _updateAimer(dossierDescr, dossierBlockDescr, key, value, prevValue, block='singleAchievements'):
    dossierDescr[block]['aimer'] = 1


def _updateMaxWFC2014WinSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxWFC2014WinSeries']:
        dossierBlockDescr['maxWFC2014WinSeries'] = value
    if value >= 1:
        dossierDescr['singleAchievements']['WFC2014'] = 1
        dossierDescr.addPopUp('singleAchievements', 'WFC2014', 1)


def _updateMaxEFC2016WinSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxEFC2016WinSeries']:
        dossierBlockDescr['maxEFC2016WinSeries'] = value


def _updateRankedBattlesHeroProgress(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= 1:
        dossierDescr['singleAchievements']['rankedBattlesHero'] = 1
        dossierDescr.addPopUp('singleAchievements', 'rankedBattlesHero', 1)
    elif value == 0:
        dossierDescr['singleAchievements']['rankedBattlesHero'] = 0


def _updateRankedDivisionFighter(dossierDescr, dossierBlockDescr, key, value, prevValue):
    achievmentName = 'rankedDivisionFighter'
    prevClass = __getNewMedalClass(achievmentName, prevValue, 0)
    curClass = __getNewMedalClass(achievmentName, value, 0)
    if prevClass != curClass:
        dossierBlockDescr[achievmentName] = curClass
        dossierDescr.addPopUp('achievements', achievmentName, curClass)


def _updateRankedStayingPower(dossierDescr, dossierBlockDescr, key, value, prevValue):
    achievmentName = 'rankedStayingPower'
    prevClass = __getNewMedalClass(achievmentName, prevValue, 0)
    curClass = __getNewMedalClass(achievmentName, value, 0)
    if prevClass != curClass:
        dossierBlockDescr[achievmentName] = curClass
        dossierDescr.addPopUp('achievements', achievmentName, curClass)


def _updateMaxDeathTrackWinSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxDeathTrackWinSeries']:
        dossierBlockDescr['maxDeathTrackWinSeries'] = value
    if value >= 1:
        dossierDescr['singleAchievements']['deathTrack'] = 1
        dossierDescr.addPopUp('singleAchievements', 'deathTrack', 1)


def _updateMousebane(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medals, series = divmod(value, RECORD_CONFIGS['mousebane'])
    if dossierDescr['achievements']['mousebane'] != medals:
        dossierDescr['achievements']['mousebane'] = medals


def _updateTankExpert(dossierDescr, dossierBlockDescr, key, value):
    cache = getCache()
    killedVehTypes = set(dossierBlockDescr.iterkeys())
    vehiclesInTrees = cache['vehiclesInTrees']
    if key not in vehiclesInTrees:
        return
    if not bool(vehiclesInTrees - killedVehTypes):
        dossierDescr['achievements']['tankExpert'] = True
        dossierDescr.addPopUp('achievements', 'tankExpert', True)
    nationID = getVehicleNationID(key)
    if not bool(cache['vehiclesInTreesByNation'][nationID] - killedVehTypes):
        record = ''.join(['tankExpert', str(nationID)])
        dossierDescr['achievements'][record] = True
        dossierDescr.addPopUp('achievements', record, True)


def _updateWolfAmongSheepMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['wolfAmongSheepMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['wolfAmongSheepMedal'] += medals
        dossierBlockDescr['wolfAmongSheep'] = amountLeft


def _updateGeniusForWarMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['geniusForWarMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['geniusForWarMedal'] += medals
        dossierBlockDescr['geniusForWar'] = amountLeft


def _updateCrucialShotMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['crucialShotMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['crucialShotMedal'] += medals
        dossierBlockDescr['crucialShot'] = amountLeft


def _updateMaxTacticalBreakthroughSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxTacticalBreakthroughSeries']:
        dossierBlockDescr['maxTacticalBreakthroughSeries'] = value


def _updateTacticalBreakthrough(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['tacticalBreakthrough']:
        dossierDescr['singleAchievements']['tacticalBreakthrough'] = 1
        dossierDescr.addPopUp('singleAchievements', 'tacticalBreakthrough', 1)


def _updateFightingReconnaissanceMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['fightingReconnaissanceMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['fightingReconnaissanceMedal'] += medals
        dossierBlockDescr['fightingReconnaissance'] = amountLeft


def _updatePyromaniacMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['pyromaniacMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['pyromaniacMedal'] += medals
        dossierBlockDescr['pyromaniac'] = amountLeft


def _updateRangerMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['rangerMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['rangerMedal'] += medals
        dossierBlockDescr['ranger'] = amountLeft


def _updatePromisingFighterMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['promisingFighterMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['promisingFighterMedal'] += medals
        dossierBlockDescr['promisingFighter'] = amountLeft


def _updateHeavyFireMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['heavyFireMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['heavyFireMedal'] += medals
        dossierBlockDescr['heavyFire'] = amountLeft


def _updateFireAndSteelMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['fireAndSteelMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['fireAndSteelMedal'] += medals
        dossierBlockDescr['fireAndSteel'] = amountLeft


def _updateGuerrillaMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['guerrillaMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['guerrillaMedal'] += medals
        dossierBlockDescr['guerrilla'] = amountLeft


def _updateBruteForceMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['bruteForceMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['bruteForceMedal'] += medals
        dossierBlockDescr['bruteForce'] = amountLeft


def _updatePrematureDetonationMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['prematureDetonationMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['prematureDetonationMedal'] += medals
        dossierBlockDescr['prematureDetonation'] = amountLeft


def _updateSentinelMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['sentinelMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['sentinelMedal'] += medals
        dossierBlockDescr['sentinel'] = amountLeft


def _updateSteamBattleCredits(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamLittleSavingsMedal'] and not dossierBlockDescr['steamLittleSavingsMedal']:
        dossierBlockDescr['steamLittleSavingsMedal'] = True
    if value >= RECORD_CONFIGS['steamMintedCoinMedal'] and not dossierBlockDescr['steamMintedCoinMedal']:
        dossierBlockDescr['steamMintedCoinMedal'] = True
    if value >= RECORD_CONFIGS['steamKingMidasMedal']:
        dossierBlockDescr['steamKingMidasMedal'] = True


def _updateSteamBattleXP(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamGoodStudentMedal'] and not dossierBlockDescr['steamGoodStudentMedal']:
        dossierBlockDescr['steamGoodStudentMedal'] = True
    if value >= RECORD_CONFIGS['steamBattleHardenedMedal'] and not dossierBlockDescr['steamBattleHardenedMedal']:
        dossierBlockDescr['steamBattleHardenedMedal'] = True
    if value >= RECORD_CONFIGS['steamExperienceMedal']:
        dossierBlockDescr['steamExperienceMedal'] = True


def _updateSteamFreeXP(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamHandyMedal'] and not dossierBlockDescr['steamHandyMedal']:
        dossierBlockDescr['steamHandyMedal'] = True
    if value >= RECORD_CONFIGS['steamUniversalResourceMedal'] and not dossierBlockDescr['steamUniversalResourceMedal']:
        dossierBlockDescr['steamUniversalResourceMedal'] = True
    if value >= RECORD_CONFIGS['steamPowerKnowledgeMedal']:
        dossierBlockDescr['steamPowerKnowledgeMedal'] = True


def _updateSteamFragsMedals(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamSuchWorkMedal'] and not dossierBlockDescr['steamSuchWorkMedal']:
        dossierBlockDescr['steamSuchWorkMedal'] = True
    if value >= RECORD_CONFIGS['steamNothingPersonalMedal'] and not dossierBlockDescr['steamNothingPersonalMedal']:
        dossierBlockDescr['steamNothingPersonalMedal'] = True
    if value >= RECORD_CONFIGS['steamTheBeginningMedal']:
        dossierBlockDescr['steamTheBeginningMedal'] = True


def _updateSteamMasteryMarksMedals(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamGetMaxMedal'] and not dossierBlockDescr['steamGetMaxMedal']:
        dossierBlockDescr['steamGetMaxMedal'] = True
    if value >= RECORD_CONFIGS['steamThreeCheersMedal'] and not dossierBlockDescr['steamThreeCheersMedal']:
        dossierBlockDescr['steamThreeCheersMedal'] = True
    if value >= RECORD_CONFIGS['steamGoldenFiveMedal']:
        dossierBlockDescr['steamGoldenFiveMedal'] = True


def _updateSteamForWarriorMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if dossierDescr.isBlockInLayout('steamAchievements') and not dossierDescr['steamAchievements']['steamForWarriorMedal']:
        dossierDescr['steamAchievements']['steamForWarriorMedal'] = True


def _updateSteamForSteelWallMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if dossierDescr.isBlockInLayout('steamAchievements') and not dossierDescr['steamAchievements']['steamForSteelWallMedal']:
        dossierDescr['steamAchievements']['steamForSteelWallMedal'] = True


def _updateSteamForBonecrusherMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if dossierDescr.isBlockInLayout('steamAchievements') and not dossierDescr['steamAchievements']['steamForBonecrusherMedal']:
        dossierDescr['steamAchievements']['steamForBonecrusherMedal'] = True


def _updateSteamOrderMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamOrderMedal']:
        dossierDescr['steamAchievements']['steamOrderMedal'] = True


def _updateSteamSpottedMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamSpottedMedal']:
        dossierBlockDescr['steamSpottedMedal'] = True


def _updateSteamBasePoints(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamBasePointsMedal']:
        dossierBlockDescr['steamBasePointsMedal'] = True


def _updateSteamHardCharacterMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamHardCharacterMedal']:
        dossierBlockDescr['steamHardCharacterMedal'] = True


def _updatesteamMediumMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamMediumMedal']:
        dossierBlockDescr['steamMediumMedal'] = True


def _updateSteamATSPGMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamATSPGMedal']:
        dossierBlockDescr['steamATSPGMedal'] = True


def _updateSteamBreakThroughMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamBreakThroughMedal']:
        dossierBlockDescr['steamBreakThroughMedal'] = True


def _updateSteamStopMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamStopMedal']:
        dossierBlockDescr['steamStopMedal'] = True


def _updateSteamReconnoiterMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamReconnoiterMedal']:
        dossierBlockDescr['steamReconnoiterMedal'] = True


def _updateSteamPotentialStunMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamPotentialStunMedal']:
        dossierBlockDescr['steamPotentialStunMedal'] = True


def _updateSteamMileageMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamMileageMedal']:
        dossierBlockDescr['steamMileageMedal'] = True


def _updateSteamBootcamp(dossierDescr, dossierBlockDescr, value, added):
    if dossierDescr.isBlockInLayout('steamAchievements') and added:
        dossierDescr['steamAchievements']['steamBootcampMedal'] = True


def _updateSteamTopLeagueMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['steamTopLeagueMedal']:
        dossierBlockDescr['steamTopLeagueMedal'] = True


def _updateInfiltratorMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    amountRequired = RECORD_CONFIGS['infiltratorMedal']
    if value >= amountRequired:
        medals, amountLeft = divmod(value, amountRequired)
        dossierBlockDescr['infiltratorMedal'] += medals
        dossierBlockDescr['infiltrator'] = amountLeft


def _updateAwardCount(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if key == 'maxTacticalBreakthroughSeries':
        amountRequired = RECORD_CONFIGS['tacticalBreakthrough']
        if prevValue < amountRequired <= value:
            dossierBlockDescr['awardCount'] += 1
    elif key == 'forTacticalOperations' and value - prevValue != 0:
        dossierBlockDescr['awardCount'] += 1
    else:
        dossierBlockDescr['awardCount'] += value - prevValue


def _updateBattleTested(dossierDescr, dossierBlockDescr, key, value, prevValue):
    awardCountCnfg = RECORD_CONFIGS['battleTested']
    maxMedalClass = len(awardCountCnfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if value >= awardCountCnfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierBlockDescr['battleTested']
    if curClass == 0 or curClass > medalClass:
        dossierBlockDescr['battleTested'] = medalClass


def _updateMakerOfHistoryMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    minWinsCnfg = RECORD_CONFIGS['makerOfHistory']
    maxMedalClass = len(minWinsCnfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if value >= minWinsCnfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierBlockDescr['makerOfHistory']
    if curClass == 0 or curClass > medalClass:
        dossierBlockDescr['makerOfHistory'] = medalClass


def _updateGuardsManMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    minWinsCnfg = RECORD_CONFIGS['guardsman']
    maxMedalClass = len(minWinsCnfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if value >= minWinsCnfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierBlockDescr['guardsman']
    if curClass == 0 or curClass > medalClass:
        dossierBlockDescr['guardsman'] = medalClass


def _updateForTacticalOperations(dossierDescr, dossierBlockDescr, key, value, prevValue):
    wins7x7 = dossierBlockDescr['wins']
    medalCfg = RECORD_CONFIGS['forTacticalOperations']
    maxMedalClass = len(medalCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if wins7x7 >= medalCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    achievements7x7 = dossierDescr['achievements7x7']
    curClass = achievements7x7['forTacticalOperations']
    if curClass == 0 or curClass > medalClass:
        achievements7x7['forTacticalOperations'] = medalClass


def _updateConquerorMedal(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'conqueror'
    medalClass = dossierDescr['fortAchievements'][medalName]
    newMedalClass = __getNewMedalClass(medalName, value, medalClass)
    if newMedalClass is not None:
        dossierDescr['fortAchievements'][medalName] = newMedalClass
    return


def _updateSoldierOfFortune(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'soldierOfFortune'
    medalClass = dossierDescr['fortAchievements'][medalName]
    wins = dossierBlockDescr['wins']
    newMedalClass = __getNewMedalClass(medalName, wins, medalClass)
    if newMedalClass is not None:
        dossierDescr['fortAchievements'][medalName] = newMedalClass
    return


def _updateMedalRotmistrov(dossierDescr, dossierBlockDescr, key, value, prevValue):
    cfg = RECORD_CONFIGS['medalRotmistrov']
    battlesCount = 0
    for block in ('globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute'):
        if dossierDescr.isBlockInLayout(block):
            if block in dossierDescr:
                battlesCount += dossierDescr[block][key]

    i = 0
    for cfgBattlesCount in cfg:
        if battlesCount < cfgBattlesCount:
            break
        i += 1

    if i > 0:
        medalClass = len(cfg) - i + 1
        dossierDescr['clanAchievements']['medalRotmistrov'] = medalClass


def _updateKampfer(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'kampfer'
    medalClass = dossierDescr['fortAchievements'][medalName]
    newMedalClass = __getNewMedalClass(medalName, value, medalClass)
    if newMedalClass is not None:
        dossierDescr['fortAchievements'][medalName] = newMedalClass
    return


def _updateFireAndSword(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'fireAndSword'
    medalClass = dossierDescr['fortAchievements'][medalName]
    newMedalClass = __getNewMedalClass(medalName, value, medalClass)
    if newMedalClass is not None:
        dossierDescr['fortAchievements'][medalName] = newMedalClass
    return


def _updateCrusher(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'crusher'
    medalValue = dossierDescr['fortAchievements'][medalName]
    cfg = RECORD_CONFIGS[medalName]
    newValue = value // cfg
    if newValue > medalValue:
        dossierDescr['fortAchievements'][medalName] = newValue


def _updateCounterblow(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'counterblow'
    medalValue = dossierDescr['fortAchievements'][medalName]
    cfg = RECORD_CONFIGS[medalName]
    newValue = value // cfg
    if newValue > medalValue:
        dossierDescr['fortAchievements'][medalName] = newValue


def _updateStrategicOperations(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'strategicOperations'
    medalClass = dossierDescr['achievementsRated7x7'][medalName]
    newMedalClass = __getNewMedalClass(medalName, value, medalClass)
    if newMedalClass is not None:
        dossierDescr['achievementsRated7x7'][medalName] = newMedalClass
    return


def _updateMaxVictoryMarchSeries(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value > dossierBlockDescr['maxVictoryMarchSeries']:
        dossierBlockDescr['maxVictoryMarchSeries'] = value


def _updateVictoryMarch(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['victoryMarch']:
        dossierDescr['singleAchievements']['victoryMarch'] = 1
        dossierDescr.addPopUp('singleAchievements', 'victoryMarch', 1)


def _updateClubVictoryMarch(dossierDescr, dossierBlockDescr, key, value, prevValue):
    if value >= RECORD_CONFIGS['victoryMarch']:
        dossierDescr['singleAchievementsRated7x7']['victoryMarch'] = 1
        dossierDescr.addPopUp('singleAchievementsRated7x7', 'victoryMarch', 1)


def _updateStormLord(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'stormLord'
    medalClass = dossierDescr['falloutAchievements'][medalName]
    newMedalClass = __getNewMedalClass(medalName, value, medalClass)
    if newMedalClass is not None:
        dossierDescr['falloutAchievements'][medalName] = newMedalClass
    return


def _updateWinnerLaurels(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'winnerLaurels'
    medalClass = dossierDescr['falloutAchievements'][medalName]
    newMedalClass = __getNewMedalClass(medalName, value, medalClass)
    if newMedalClass is not None:
        dossierDescr['falloutAchievements'][medalName] = newMedalClass
    return


def _updateRP2018sergeant(dossierDescr, dossierBlockDescr, key, value, prevValue):
    medalName = 'RP2018sergeant'
    medalClass = dossierDescr['achievements'][medalName]
    newMedalClass = __getNewMedalClass(medalName, value, medalClass)
    if newMedalClass is not None:
        dossierDescr['achievements'][medalName] = newMedalClass
    return


def __getNewMedalClass(medalConfigName, valueToCheck, curMedalClass):
    medalCfg = RECORD_CONFIGS[medalConfigName]
    maxMedalClass = len(medalCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if valueToCheck >= medalCfg[maxMedalClass - medalClass]:
            if curMedalClass == 0 or curMedalClass > medalClass:
                return medalClass
            break

    return None


def _updateNYBadges(dossierDescr, dossierBlockDescr, key, value, prevValue):
    for badgeID in PREVIOUS_YEARS_BADGE_IDS:
        dossierBlockDescr.pop(badgeID, None)

    return


def init():
    _set_A15X15_STATS_DEPENDENCIES()
    _set_A7X7_STATS_DEPENDENCIES()
    _set_ACHIEVEMENT15X15_DEPENDENCIES()
    _set_ACHIEVEMENT7X7_DEPENDENCIES()
    _set_ACHIEVEMENTRATED7X7_DEPENDENCIES()
    _set_VEH_TYPE_FRAGS_DEPENDENCIES()
    _set_HISTORICAL_STATS_DEPENDENCIES()
    _set_HISTORICAL_ACHIEVEMENTS_DEPENDENCIES()
    _set_SINGLE_ACHIEVEMENTS_DEPENDENCIES()
    _set_FORT_BATTLES_STATS_DEPENDENCIES()
    _set_FORT_SORTIES_STATS_DEPENDENCIES()
    _set_FORT_ACHIEVEMENTS_DEPENDENCIES()
    _set_CLAN_STATS_DEPENDENCIES()
    _set_CLUB_BATTLES_STAT_DEPENDENCIES()
    _set_CLUB_ACHIEVEMENTS_DEPENDENCIES()
    _set_GLOBAL_MAP_STATS_DEPENDENCIES()
    _set_FALLOUT_STATS_DEPENDENCIES()
    _set_RANKED_STATS_DEPENDENCIES()
    _set_EPIC_BATTLE_STATS_DEPENDENCIES()
    _set_STEAM_ACHIEVEMENT_DEPENDENCIES()
    _set_PLAYER_BADGES_DEPENDENCIES()
