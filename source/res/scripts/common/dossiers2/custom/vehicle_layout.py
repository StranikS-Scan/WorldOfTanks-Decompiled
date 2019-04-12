# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/vehicle_layout.py
from dossiers2.common.DossierBlockBuilders import *
from battle_statistics_layouts import *
from dossiers2.custom.dependencies import ACHIEVEMENT15X15_DEPENDENCIES
from dossiers2.custom.dependencies import ACHIEVEMENT7X7_DEPENDENCIES
from dossiers2.custom.dependencies import FALLOUT_STATS_DEPENDENCIES
from dossiers2.custom.dependencies import FORT_ACHIEVEMENTS_DEPENDENCIES
from dossiers2.custom.dependencies import GLOBAL_MAP_STATS_DEPENDENCIES
from dossiers2.custom.dependencies import RANKED_STATS_DEPENDENCIES
from dossiers2.custom.dependencies import A30X30_STATS_DEPENDENCIES
from dossiers2.custom.dependencies import EPIC_BATTLE_STATS_DEPENDENCIES
TOTAL_BLOCK_LAYOUT = ['creationTime',
 'lastBattleTime',
 'battleLifeTime',
 'treesCut',
 'mileage']
_totalBlockBuilder = StaticSizeBlockBuilder('total', TOTAL_BLOCK_LAYOUT, {}, [])
_a15x15BlockBuilder = StaticSizeBlockBuilder('a15x15', A15X15_BLOCK_LAYOUT, A15X15_STATS_DEPENDENCIES, [])
_a15x15_2BlockBuilder = StaticSizeBlockBuilder('a15x15_2', A15X15_2_BLOCK_LAYOUT, {}, [])
_clanBlockBuilder = StaticSizeBlockBuilder('clan', CLAN_BLOCK_LAYOUT, CLAN_STATS_DEPENDENCIES, [])
_clan2BlockBuilder = StaticSizeBlockBuilder('clan2', CLAN2_BLOCK_LAYOUT, {}, [])
_companyBlockBuilder = StaticSizeBlockBuilder('company', COMPANY_BLOCK_LAYOUT, {}, [])
_company2BlockBuilder = StaticSizeBlockBuilder('company2', COMPANY2_BLOCK_LAYOUT, {}, [])
_a7x7BlockBuilder = StaticSizeBlockBuilder('a7x7', A7X7_BLOCK_LAYOUT, A7X7_STATS_DEPENDENCIES, [])
_rated7x7BlockBuilder = StaticSizeBlockBuilder('rated7x7', RATED_7X7_BLOCK_LAYOUT, {}, [])
_historicalBlockBuilder = StaticSizeBlockBuilder('historical', HISTORICAL_BLOCK_LAYOUT, HISTORICAL_STATS_DEPENDENCIES, [])
_fortBattlesBlockBuilder = StaticSizeBlockBuilder('fortBattles', FORT_BLOCK_LAYOUT, FORT_BATTLES_STATS_DEPENDENCIES, [])
_fortSortiesBlockBuilder = StaticSizeBlockBuilder('fortSorties', FORT_BLOCK_LAYOUT, FORT_SORTIES_STATS_DEPENDENCIES, [])
_globalMapCommonBlockBuilder = StaticSizeBlockBuilder('globalMapCommon', GLOBAL_MAP_BLOCK_LAYOUT, GLOBAL_MAP_STATS_DEPENDENCIES, [])
_falloutBlockBuilder = StaticSizeBlockBuilder('fallout', FALLOUT_VEHICLE_BLOCK_LAYOUT, FALLOUT_STATS_DEPENDENCIES, [])
_rankedBlockBuilder = StaticSizeBlockBuilder('ranked', RANKED_BLOCK_LAYOUT, RANKED_STATS_DEPENDENCIES, [])
_a30x30BlockBuilder = StaticSizeBlockBuilder('a30x30', A30X30_BLOCK_LAYOUT, A30X30_STATS_DEPENDENCIES, [])
_epicBattleBlockBuilder = StaticSizeBlockBuilder('epicBattle', EPIC_BATTLE_VEHICLE_BLOCK_LAYOUT, {}, [])
_maxPopUps = ['maxXP', 'maxFrags', 'maxDamage']
_maxFalloutPopUps = _maxPopUps + ['maxWinPoints', 'maxCoins']
_max15x15BlockBuilder = StaticSizeBlockBuilder('max15x15', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_max7x7BlockBuilder = StaticSizeBlockBuilder('max7x7', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxHistoricalBlockBuilder = StaticSizeBlockBuilder('maxHistorical', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxFortBattlesBlockBuilder = StaticSizeBlockBuilder('maxFortBattles', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxFortSortiesBlockBuilder = StaticSizeBlockBuilder('maxFortSorties', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxRated7x7BlockBuilder = StaticSizeBlockBuilder('maxRated7x7', MAX_BLOCK_LAYOUT, {}, [])
_maxGlobalMapCommonBlockBuilder = StaticSizeBlockBuilder('maxGlobalMapCommon', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxFalloutBlockBuilder = StaticSizeBlockBuilder('maxFallout', MAX_FALLOUT_BLOCK_LAYOUT, {}, _maxFalloutPopUps)
_maxRankedBlockBuilder = StaticSizeBlockBuilder('maxRanked', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_max30x30BlockBuilder = StaticSizeBlockBuilder('max30x30', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxEpicBattleBlockBuilder = StaticSizeBlockBuilder('maxEpicBattle', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_vehTypeFragsBlockBuilder = DictBlockBuilder('vehTypeFrags', 'I', 'H', VEH_TYPE_FRAGS_DEPENDENCIES)
_rankedSeasonsBlockBuilder = DictBlockBuilder('rankedSeasons', 'II', 'BB', {})
_maxRankedSeason1BlockBuilder = StaticSizeBlockBuilder('maxRankedSeason1', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxRankedSeason2BlockBuilder = StaticSizeBlockBuilder('maxRankedSeason2', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_maxRankedSeason3BlockBuilder = StaticSizeBlockBuilder('maxRankedSeason3', MAX_BLOCK_LAYOUT, {}, _maxPopUps)
_ACHIEVEMENTS15X15_BLOCK_LAYOUT = ['fragsBeast',
 'sniperSeries',
 'maxSniperSeries',
 'invincibleSeries',
 'maxInvincibleSeries',
 'diehardSeries',
 'maxDiehardSeries',
 'killingSeries',
 'fragsSinai',
 'maxKillingSeries',
 'piercingSeries',
 'maxPiercingSeries',
 'battleHeroes',
 'warrior',
 'invader',
 'sniper',
 'defender',
 'steelwall',
 'supporter',
 'scout',
 'evileye',
 'medalKay',
 'medalCarius',
 'medalKnispel',
 'medalPoppel',
 'medalAbrams',
 'medalLeClerc',
 'medalLavrinenko',
 'medalEkins',
 'medalWittmann',
 'medalOrlik',
 'medalOskin',
 'medalHalonen',
 'medalBurda',
 'medalBillotte',
 'medalKolobanov',
 'medalFadin',
 'medalRadleyWalters',
 'medalBrunoPietro',
 'medalTarczay',
 'medalPascucci',
 'medalDumitru',
 'medalLehvaslaiho',
 'medalNikolas',
 'medalLafayettePool',
 'sinai',
 'heroesOfRassenay',
 'beasthunter',
 'mousebane',
 'tankExpertStrg',
 'raider',
 'kamikaze',
 'lumberjack',
 'medalBrothersInArms',
 'medalCrucialContribution',
 'medalDeLanglade',
 'medalTamadaYoshio',
 'bombardier',
 'huntsman',
 'alaric',
 'sturdy',
 'ironMan',
 'luckyDevil',
 'pattonValley',
 'fragsPatton',
 'markOfMastery',
 'sniper2',
 'mainGun',
 'marksOnGun',
 'movingAvgDamage',
 'medalMonolith',
 'medalAntiSpgFire',
 'medalGore',
 'medalCoolBlood',
 'medalStark',
 'damageRating',
 'impenetrable',
 'maxAimerSeries',
 'shootToKill',
 'fighter',
 'duelist',
 'demolition',
 'arsonist',
 'bonecrusher',
 'charmed',
 'even']
_achievements15x15PopUps = ['tankExpert',
 'tankExpert0',
 'tankExpert1',
 'tankExpert2',
 'tankExpert3',
 'tankExpert4',
 'tankExpert5',
 'tankExpert6',
 'tankExpert7',
 'tankExpert8',
 'tankExpert9',
 'tankExpert10',
 'tankExpert11',
 'tankExpert12',
 'tankExpert13',
 'tankExpert14',
 'markOfMastery',
 'marksOnGun',
 'impenetrableshootToKill',
 'fighter',
 'duelist',
 'demolition',
 'arsonist',
 'bonecrusher',
 'charmed',
 'even']
_achievements15x15BlockBuilder = StaticSizeBlockBuilder('achievements', _ACHIEVEMENTS15X15_BLOCK_LAYOUT, ACHIEVEMENT15X15_DEPENDENCIES, _achievements15x15PopUps)
ACHIEVEMENTS7X7_BLOCK_LAYOUT = ['wolfAmongSheep',
 'wolfAmongSheepMedal',
 'geniusForWar',
 'geniusForWarMedal',
 'kingOfTheHill',
 'tacticalBreakthroughSeries',
 'maxTacticalBreakthroughSeries',
 'armoredFist',
 'godOfWar',
 'fightingReconnaissance',
 'fightingReconnaissanceMedal',
 'willToWinSpirit',
 'crucialShot',
 'crucialShotMedal',
 'forTacticalOperations',
 'promisingFighter',
 'promisingFighterMedal',
 'heavyFire',
 'heavyFireMedal',
 'ranger',
 'rangerMedal',
 'fireAndSteel',
 'fireAndSteelMedal',
 'pyromaniac',
 'pyromaniacMedal',
 'noMansLand',
 'guerrilla',
 'guerrillaMedal',
 'infiltrator',
 'infiltratorMedal',
 'sentinel',
 'sentinelMedal',
 'prematureDetonation',
 'prematureDetonationMedal',
 'bruteForce',
 'bruteForceMedal',
 'awardCount',
 'battleTested']
_achievements7x7BlockBuilder = StaticSizeBlockBuilder('achievements7x7', ACHIEVEMENTS7X7_BLOCK_LAYOUT, ACHIEVEMENT7X7_DEPENDENCIES, [])
UNIQUE_VEH_ACHIEVEMENT_VALUES = []
_uniqueVehAchievementPopUps = []
_uniqueVehAchievementBlockBuilder = BinarySetDossierBlockBuilder('uniqueAchievements', UNIQUE_VEH_ACHIEVEMENT_VALUES, {}, _uniqueVehAchievementPopUps)
_SINGLE_ACHIEVEMENTS_VALUES = ['titleSniper',
 'invincible',
 'diehard',
 'handOfDeath',
 'armorPiercer',
 'tacticalBreakthrough',
 'aimer']
_singleAchievementsPopUps = ['titleSniper',
 'invincible',
 'diehard',
 'handOfDeath',
 'armorPiercer',
 'tacticalBreakthrough',
 'aimer']
_singleAchievementsBlockBuilder = BinarySetDossierBlockBuilder('singleAchievements', _SINGLE_ACHIEVEMENTS_VALUES, {}, _singleAchievementsPopUps)
FORT_ACHIEVEMENTS_BLOCK_LAYOUT = ['conqueror',
 'fireAndSword',
 'crusher',
 'counterblow',
 'kampfer',
 'soldierOfFortune']
_fortPersonalAchievementsPopUps = ['soldierOfFortune']
_fortPersonalAchievementsBlockBuilder = StaticSizeBlockBuilder('fortAchievements', FORT_ACHIEVEMENTS_BLOCK_LAYOUT, FORT_ACHIEVEMENTS_DEPENDENCIES, _fortPersonalAchievementsPopUps)
CLAN_ACHIEVEMENTS_BLOCK_LAYOUT = ['medalRotmistrov']
_clanAchievementsBlockBuilder = StaticSizeBlockBuilder('clanAchievements', CLAN_ACHIEVEMENTS_BLOCK_LAYOUT, {}, [])
FALLOUT_ACHIEVEMENTS_BLOCK_LAYOUT = ['shoulderToShoulder',
 'aloneInTheField',
 'fallenFlags',
 'effectiveSupport',
 'stormLord',
 'winnerLaurels',
 'predator',
 'unreachable',
 'champion',
 'bannerman',
 'falloutDieHard',
 'deleted']
_falloutAchievementsPopUps = ['falloutDieHard']
_falloutAchievementsBlockBuilder = StaticSizeBlockBuilder('falloutAchievements', FALLOUT_ACHIEVEMENTS_BLOCK_LAYOUT, {}, _falloutAchievementsPopUps)
EPIC_BATTLE_ACHIEVEMENTS_BLOCK_LAYOUT = ['occupyingForce',
 'ironShield',
 'generalOfTheArmy',
 'supremeGun',
 'smallArmy']
_epicBattleAchievementsPopUps = ['occupyingForce',
 'ironShield',
 'generalOfTheArmy',
 'supremeGun',
 'smallArmy']
_epicBattleAchievementsBlockBuilder = StaticSizeBlockBuilder('epicBattleAchievements', EPIC_BATTLE_ACHIEVEMENTS_BLOCK_LAYOUT, {}, _epicBattleAchievementsPopUps)
_playerInscriptionsBlockBuilder = ListBlockBuilder('inscriptions', 'H', {})
_playerEmblemsBlockBuilder = ListBlockBuilder('emblems', 'H', {})
_camouflagesBlockBuilder = ListBlockBuilder('camouflages', 'H', {})
COMPENSATION_BLOCK_LAYOUT = ['gold']
_compensationBlockBuilder = StaticSizeBlockBuilder('compensation', COMPENSATION_BLOCK_LAYOUT, {}, [])
vehicleDossierLayout = (_a15x15BlockBuilder,
 _a15x15_2BlockBuilder,
 _clanBlockBuilder,
 _clan2BlockBuilder,
 _companyBlockBuilder,
 _company2BlockBuilder,
 _a7x7BlockBuilder,
 _achievements15x15BlockBuilder,
 _vehTypeFragsBlockBuilder,
 _totalBlockBuilder,
 _max15x15BlockBuilder,
 _max7x7BlockBuilder,
 _playerInscriptionsBlockBuilder,
 _playerEmblemsBlockBuilder,
 _camouflagesBlockBuilder,
 _compensationBlockBuilder,
 _achievements7x7BlockBuilder,
 _historicalBlockBuilder,
 _maxHistoricalBlockBuilder,
 _uniqueVehAchievementBlockBuilder,
 _fortBattlesBlockBuilder,
 _maxFortBattlesBlockBuilder,
 _fortSortiesBlockBuilder,
 _maxFortSortiesBlockBuilder,
 _fortPersonalAchievementsBlockBuilder,
 _singleAchievementsBlockBuilder,
 _clanAchievementsBlockBuilder,
 _rated7x7BlockBuilder,
 _maxRated7x7BlockBuilder,
 _globalMapCommonBlockBuilder,
 _maxGlobalMapCommonBlockBuilder,
 _falloutBlockBuilder,
 _maxFalloutBlockBuilder,
 _falloutAchievementsBlockBuilder,
 _rankedBlockBuilder,
 _maxRankedBlockBuilder,
 _rankedSeasonsBlockBuilder,
 _a30x30BlockBuilder,
 _max30x30BlockBuilder,
 _epicBattleBlockBuilder,
 _maxEpicBattleBlockBuilder,
 _epicBattleAchievementsBlockBuilder,
 _maxRankedSeason1BlockBuilder,
 _maxRankedSeason2BlockBuilder,
 _maxRankedSeason3BlockBuilder)
