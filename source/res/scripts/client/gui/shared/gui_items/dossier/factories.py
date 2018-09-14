# Embedded file name: scripts/client/gui/shared/gui_items/dossier/factories.py
import nations
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE, getType as getAchieveType, ACHIEVEMENT_BLOCK as _AB, WHITE_TIGER_RECORD, RARE_STORAGE_RECORD
from gui.shared.gui_items.dossier import achievements as _as
from gui.shared.gui_items.dossier.achievements import abstract as _abstract_achievements

class _AchieveFactory(object):

    def __init__(self, achieveClass, name, block, dossier):
        self._achieveClass = achieveClass
        self._name = name
        self._block = block
        self._dossier = dossier

    def getName(self):
        return self._name

    def getBlock(self):
        return self._block

    def getDossier(self):
        return self._dossier

    def getAchieveClass(self):
        return self._achieveClass

    def isInDossier(self):
        return self._achieveClass.checkIsInDossier(self._block, self._name, self._dossier)

    def isValid(self):
        return self._achieveClass.checkIsValid(self._block, self._name, self._dossier)

    def create(self, value = None):
        return self._achieveClass(self._name, self._block, self._dossier, value)

    @classmethod
    def get(cls, achieveClass):
        return lambda name, block, dossier: cls(achieveClass, name, block, dossier)


class _CustomAchieveFactory(_AchieveFactory):

    def create(self, value = None):
        return self._achieveClass(self._dossier, value)

    @classmethod
    def get(cls, achieveClass):
        return lambda name, block, dossier: cls(achieveClass, name, block, dossier)


class _BlockAchieveFactory(_AchieveFactory):

    def __init__(self, achieveClass, name, block, dossier):
        super(_BlockAchieveFactory, self).__init__(achieveClass, name, block, dossier)

    def create(self, value = None):
        return self._achieveClass(self._name, self._dossier, value)

    @classmethod
    def get(cls, achieveClass):
        return lambda name, block, dossier: cls(achieveClass, name, block, dossier)


class _SequenceAchieveFactory(_AchieveFactory):

    def create(self, value = None):
        counts = {}
        achieves = self._dossier.getBlock(self._block)
        for achieveID in set(achieves):
            counts[achieveID] = achieves.count(achieveID)

        result = {}
        for achieveID, count in counts.iteritems():
            factory = getAchievementFactory((self._block, achieveID), self._dossier)
            if factory is not None:
                achieve = factory.create(value=count)
                if achieve is not None:
                    result[achieveID] = achieve

        return result

    @classmethod
    def get(cls, defaultClass):
        return lambda name, block, dossier: cls(defaultClass, name, block, dossier)

    def isInDossier(self):
        return True


class _RareAchievesFactory(_SequenceAchieveFactory):

    def isValid(self):
        return not self._dossier.isInRoaming()

    @classmethod
    def get(cls):
        return lambda rareID, block, dossier: cls(_abstract_achievements.RareAchievement, rareID, block, dossier)


class _NationAchieveFactory(_AchieveFactory):

    def __init__(self, achieveClass, name, nationID, block, dossier):
        super(_NationAchieveFactory, self).__init__(achieveClass, name, block, dossier)
        self._nationID = nationID

    def getNationID(self):
        return self._nationID

    def create(self, value = None):
        return self._achieveClass(self._nationID, self._block, self._dossier, value)

    @classmethod
    def get(cls, achieveClass, nationID = -1):
        return lambda name, block, dossier: cls(achieveClass, name, nationID, block, dossier)


_ACHIEVEMENTS_BY_BLOCK = {_AB.RARE: _BlockAchieveFactory.get(_abstract_achievements.RareAchievement)}
_ACHIEVEMENTS_BY_TYPE = {ACHIEVEMENT_TYPE.CLASS: _AchieveFactory.get(_abstract_achievements.ClassProgressAchievement),
 ACHIEVEMENT_TYPE.SERIES: _AchieveFactory.get(_abstract_achievements.SeriesAchievement)}
_ACHIEVEMENTS_BY_NAME = {(_AB.TOTAL, 'tankExpert'): _NationAchieveFactory.get(_as.TankExpertAchievement),
 (_AB.TOTAL, 'mechanicEngineer'): _NationAchieveFactory.get(_as.MechEngineerAchievement),
 (_AB.TOTAL, 'mousebane'): _CustomAchieveFactory.get(_as.MousebaneAchievement),
 (_AB.TOTAL, 'beasthunter'): _CustomAchieveFactory.get(_as.BeasthunterAchievement),
 (_AB.TOTAL, 'pattonValley'): _CustomAchieveFactory.get(_as.PattonValleyAchievement),
 (_AB.TOTAL, 'sinai'): _CustomAchieveFactory.get(_as.SinaiAchievement),
 (_AB.TOTAL, 'markOfMastery'): _CustomAchieveFactory.get(_as.MarkOfMasteryAchievement),
 (_AB.TOTAL, 'medalKnispel'): _CustomAchieveFactory.get(_as.MedalKnispelAchievement),
 (_AB.TOTAL, 'medalCarius'): _CustomAchieveFactory.get(_as.MedalCariusAchievement),
 (_AB.TOTAL, 'medalAbrams'): _CustomAchieveFactory.get(_as.MedalAbramsAchievement),
 (_AB.TOTAL, 'medalPoppel'): _CustomAchieveFactory.get(_as.MedalPoppelAchievement),
 (_AB.TOTAL, 'medalKay'): _CustomAchieveFactory.get(_as.MedalKayAchievement),
 (_AB.TOTAL, 'medalEkins'): _CustomAchieveFactory.get(_as.MedalEkinsAchievement),
 (_AB.TOTAL, 'medalLeClerc'): _CustomAchieveFactory.get(_as.MedalLeClercAchievement),
 (_AB.TOTAL, 'medalLavrinenko'): _CustomAchieveFactory.get(_as.MedalLavrinenkoAchievement),
 (_AB.TOTAL, 'marksOnGun'): _CustomAchieveFactory.get(_as.MarkOnGunAchievement),
 (_AB.TOTAL, 'sniper'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'medalWittmann'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'reliableComrade'): _CustomAchieveFactory.get(_as.ReliableComradeAchievement),
 (_AB.TOTAL, 'readyForBattleLT'): _CustomAchieveFactory.get(_as.ReadyForBattleLTAchievement),
 (_AB.TOTAL, 'readyForBattleMT'): _CustomAchieveFactory.get(_as.ReadyForBattleMTAchievement),
 (_AB.TOTAL, 'readyForBattleHT'): _CustomAchieveFactory.get(_as.ReadyForBattleHTAchievement),
 (_AB.TOTAL, 'readyForBattleSPG'): _CustomAchieveFactory.get(_as.ReadyForBattleSPGAchievement),
 (_AB.TOTAL, 'readyForBattleATSPG'): _CustomAchieveFactory.get(_as.ReadyForBattleATSPGAchievement),
 (_AB.TOTAL, 'testartilleryman'): _AchieveFactory.get(_as.Achieved),
 (_AB.CLAN, 'medalRotmistrov'): _CustomAchieveFactory.get(_as.MedalRotmistrovAchievement),
 (_AB.RATED_7X7, 'strategicOperations'): _CustomAchieveFactory.get(_as.StrategicOperationsAchievement),
 (_AB.FORT, 'fireAndSword'): _CustomAchieveFactory.get(_as.FireAndSwordAchievement),
 (_AB.FORT, 'soldierOfFortune'): _CustomAchieveFactory.get(_as.SoldierOfFortuneAchievement),
 (_AB.FORT, 'kampfer'): _CustomAchieveFactory.get(_as.KampferAchievement),
 (_AB.FORT, 'conqueror'): _CustomAchieveFactory.get(_as.ConquerorAchievement),
 (_AB.HISTORICAL, 'makerOfHistory'): _CustomAchieveFactory.get(_as.MakerOfHistoryAchievement),
 (_AB.HISTORICAL, 'guardsman'): _CustomAchieveFactory.get(_as.GuardsmanAchievement),
 (_AB.SINGLE, 'diehard'): _CustomAchieveFactory.get(_as.DiehardAchievement),
 (_AB.SINGLE, 'invincible'): _CustomAchieveFactory.get(_as.InvincibleAchievement),
 (_AB.SINGLE, 'tacticalBreakthrough'): _CustomAchieveFactory.get(_as.TacticalBreakthroughAchievement),
 (_AB.SINGLE, 'handOfDeath'): _CustomAchieveFactory.get(_as.HandOfDeathAchievement),
 (_AB.SINGLE, 'armorPiercer'): _CustomAchieveFactory.get(_as.ArmorPiercerAchievement),
 (_AB.SINGLE, 'titleSniper'): _CustomAchieveFactory.get(_as.TitleSniperAchievement),
 (_AB.SINGLE, 'victoryMarch'): _CustomAchieveFactory.get(_as.VictoryMarchAchievement),
 (_AB.SINGLE_7X7, 'victoryMarch'): _CustomAchieveFactory.get(_as.VictoryMarchClubAchievement),
 (_AB.SINGLE, 'battleCitizen'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'WFC2014'): _CustomAchieveFactory.get(_as.WFC2014Achievement),
 (_AB.SINGLE, 'deathTrack'): _CustomAchieveFactory.get(_as.DeathTrackAchievement),
 (_AB.SINGLE, 'aimer'): _CustomAchieveFactory.get(_as.AimerAchievement),
 (_AB.SINGLE, 'tankwomen'): _CustomAchieveFactory.get(_as.TankwomenAchievement),
 (_AB.SINGLE, 'operationWinter'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'fallout'): _AchieveFactory.get(_as.Achieved),
 (_AB.SINGLE, 'fallout2'): _AchieveFactory.get(_as.Achieved),
 (_AB.SINGLE, 'falloutSingleWolf'): _AchieveFactory.get(_as.Achieved),
 (_AB.SINGLE, 'falloutPackOfWolfs'): _AchieveFactory.get(_as.Achieved),
 (_AB.SINGLE, 'falloutSteelHunter'): _AchieveFactory.get(_as.Achieved),
 (_AB.SINGLE, 'falloutAlwaysInLine'): _AchieveFactory.get(_as.Achieved),
 (_AB.TEAM_7X7, 'geniusForWarMedal'): _CustomAchieveFactory.get(_as.GeniusForWarAchievement),
 (_AB.TEAM_7X7, 'wolfAmongSheepMedal'): _CustomAchieveFactory.get(_as.WolfAmongSheepAchievement),
 (_AB.TEAM_7X7, 'fightingReconnaissanceMedal'): _CustomAchieveFactory.get(_as.FightingReconnaissanceAchievement),
 (_AB.TEAM_7X7, 'crucialShotMedal'): _CustomAchieveFactory.get(_as.CrucialShotAchievement),
 (_AB.TEAM_7X7, 'forTacticalOperations'): _CustomAchieveFactory.get(_as.ForTacticalOperationsAchievement),
 (_AB.TEAM_7X7, 'battleTested'): _CustomAchieveFactory.get(_as.BattleTestedAchievement),
 (_AB.TEAM_7X7, 'guerrillaMedal'): _CustomAchieveFactory.get(_as.GuerrillaAchievement),
 (_AB.TEAM_7X7, 'infiltratorMedal'): _CustomAchieveFactory.get(_as.InfiltratorAchievement),
 (_AB.TEAM_7X7, 'sentinelMedal'): _CustomAchieveFactory.get(_as.SentinelAchievement),
 (_AB.TEAM_7X7, 'prematureDetonationMedal'): _CustomAchieveFactory.get(_as.PrematureDetonationAchievement),
 (_AB.TEAM_7X7, 'bruteForceMedal'): _CustomAchieveFactory.get(_as.BruteForceAchievement),
 (_AB.TEAM_7X7, 'promisingFighterMedal'): _CustomAchieveFactory.get(_as.PromisingFighterAchievement),
 (_AB.TEAM_7X7, 'heavyFireMedal'): _CustomAchieveFactory.get(_as.HeavyFireAchievement),
 (_AB.TEAM_7X7, 'rangerMedal'): _CustomAchieveFactory.get(_as.RangerAchievement),
 (_AB.TEAM_7X7, 'fireAndSteelMedal'): _CustomAchieveFactory.get(_as.FireAndSteelAchievement),
 (_AB.TEAM_7X7, 'pyromaniacMedal'): _CustomAchieveFactory.get(_as.PyromaniacAchievement),
 (_AB.UNIQUE, 'histBattle1_battlefield'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle2_battlefield'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle3_battlefield'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle4_battlefield'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle5_battlefield'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle6_battlefield'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle1_historyLessons'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle2_historyLessons'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle3_historyLessons'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle4_historyLessons'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle5_historyLessons'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.UNIQUE, 'histBattle6_historyLessons'): _AchieveFactory.get(_abstract_achievements.HistoricalAchievement),
 (_AB.FALLOUT, 'stormLord'): _CustomAchieveFactory.get(_as.StormLordAchievement),
 (_AB.FALLOUT, 'winnerLaurels'): _CustomAchieveFactory.get(_as.WinnerLaurelsAchievement),
 WHITE_TIGER_RECORD: _CustomAchieveFactory.get(_as.WhiteTigerAchievement),
 RARE_STORAGE_RECORD: _RareAchievesFactory.get()}
for _nID, _ in enumerate(nations.NAMES):
    _ACHIEVEMENTS_BY_NAME[_AB.TOTAL, 'tankExpert%d' % _nID] = _NationAchieveFactory.get(_as.TankExpertAchievement, _nID)
    _ACHIEVEMENTS_BY_NAME[_AB.TOTAL, 'mechanicEngineer%d' % _nID] = _NationAchieveFactory.get(_as.MechEngineerAchievement, _nID)

def getAchievementFactory(record, dossier = None):
    achieveType = getAchieveType(record)
    if record in _ACHIEVEMENTS_BY_NAME:
        factoryMaker = _ACHIEVEMENTS_BY_NAME[record]
    elif achieveType is not None and achieveType in _ACHIEVEMENTS_BY_TYPE:
        factoryMaker = _ACHIEVEMENTS_BY_TYPE[achieveType]
    elif record[0] in _ACHIEVEMENTS_BY_BLOCK:
        factoryMaker = _ACHIEVEMENTS_BY_BLOCK[record[0]]
    else:
        factoryMaker = _AchieveFactory.get(_abstract_achievements.RegularAchievement)
    return factoryMaker(record[1], record[0], dossier)
