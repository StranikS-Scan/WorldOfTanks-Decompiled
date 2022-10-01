# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/factories.py
import nations
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE, getType as getAchieveType, ACHIEVEMENT_BLOCK as _AB, RARE_STORAGE_RECORD, HONORED_RANK_RECORD
from gui.shared.gui_items.dossier import achievements as _as
from gui.shared.gui_items.dossier.achievements import abstract as _abstract_achievements
from gui.shared.gui_items.dossier.achievements.loyal_service import LoyalServiceAchievement

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

    def create(self, value=None):
        return self._achieveClass(self._name, self._block, self._dossier, value)

    @classmethod
    def get(cls, achieveClass):
        return lambda name, block, dossier: cls(achieveClass, name, block, dossier)


class _CustomAchieveFactory(_AchieveFactory):

    def create(self, value=None):
        return self._achieveClass(self._dossier, value)

    @classmethod
    def get(cls, achieveClass):
        return lambda name, block, dossier: cls(achieveClass, name, block, dossier)


class _BlockAchieveFactory(_AchieveFactory):

    def create(self, value=None):
        return self._achieveClass(self._name, self._dossier, value)

    @classmethod
    def get(cls, achieveClass):
        return lambda name, block, dossier: cls(achieveClass, name, block, dossier)


class _SequenceAchieveFactory(_AchieveFactory):

    def create(self, value=None):
        counts = {}
        achieves = self._dossier.getBlock(self._block) if self._dossier is not None else ()
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

    def create(self, value=None):
        return self._achieveClass(self._nationID, self._block, self._dossier, value)

    @classmethod
    def get(cls, achieveClass, nationID=-1):
        return lambda name, block, dossier: cls(achieveClass, name, nationID, block, dossier)


_ACHIEVEMENTS_BY_BLOCK = {_AB.RARE: _BlockAchieveFactory.get(_abstract_achievements.RareAchievement)}
_ACHIEVEMENTS_BY_TYPE = {ACHIEVEMENT_TYPE.CLASS: _AchieveFactory.get(_abstract_achievements.ClassProgressAchievement),
 ACHIEVEMENT_TYPE.SERIES: _AchieveFactory.get(_abstract_achievements.SeriesAchievement)}
_ACHIEVEMENTS_BY_NAME = {(_AB.TOTAL, 'warrior'): _CustomAchieveFactory.get(_as.regular_ext.WarriorAchievement),
 (_AB.TOTAL, 'heroesOfRassenay'): _CustomAchieveFactory.get(_as.regular_ext.HeroesOfRassenayAchievement),
 (_AB.TOTAL, 'medalLafayettePool'): _CustomAchieveFactory.get(_as.regular_ext.MedalLafayettePoolAchievement),
 (_AB.TOTAL, 'medalRadleyWalters'): _CustomAchieveFactory.get(_as.regular_ext.MedalRadleyWaltersAchievement),
 (_AB.TOTAL, 'tankExpert'): _NationAchieveFactory.get(_as.nation_specific.TankExpertAchievement),
 (_AB.TOTAL, 'mechanicEngineer'): _NationAchieveFactory.get(_as.nation_specific.MechEngineerAchievement),
 (_AB.TOTAL, 'mousebane'): _CustomAchieveFactory.get(_as.simple_progress.MousebaneAchievement),
 (_AB.TOTAL, 'beasthunter'): _CustomAchieveFactory.get(_as.simple_progress.BeasthunterAchievement),
 (_AB.TOTAL, 'pattonValley'): _CustomAchieveFactory.get(_as.simple_progress.PattonValleyAchievement),
 (_AB.TOTAL, 'sinai'): _CustomAchieveFactory.get(_as.simple_progress.SinaiAchievement),
 (_AB.TOTAL, 'markOfMastery'): _CustomAchieveFactory.get(_as.MarkOfMasteryAchievement),
 (_AB.TOTAL, 'medalKnispel'): _CustomAchieveFactory.get(_as.class_progress.MedalKnispelAchievement),
 (_AB.TOTAL, 'medalCarius'): _CustomAchieveFactory.get(_as.class_progress.MedalCariusAchievement),
 (_AB.TOTAL, 'medalAbrams'): _CustomAchieveFactory.get(_as.class_progress.MedalAbramsAchievement),
 (_AB.TOTAL, 'medalPoppel'): _CustomAchieveFactory.get(_as.class_progress.MedalPoppelAchievement),
 (_AB.TOTAL, 'medalKay'): _CustomAchieveFactory.get(_as.class_progress.MedalKayAchievement),
 (_AB.TOTAL, 'medalEkins'): _CustomAchieveFactory.get(_as.class_progress.MedalEkinsAchievement),
 (_AB.TOTAL, 'medalLeClerc'): _CustomAchieveFactory.get(_as.class_progress.MedalLeClercAchievement),
 (_AB.TOTAL, 'medalLavrinenko'): _CustomAchieveFactory.get(_as.class_progress.MedalLavrinenkoAchievement),
 (_AB.TOTAL, 'marksOnGun'): _CustomAchieveFactory.get(_as.mark_on_gun.MarkOnGunAchievement),
 (_AB.TOTAL, 'sniper'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'medalWittmann'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'reliableComrade'): _CustomAchieveFactory.get(_as.simple_progress.ReliableComradeAchievement),
 (_AB.TOTAL, 'readyForBattleLT'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleLTAchievement),
 (_AB.TOTAL, 'readyForBattleMT'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleMTAchievement),
 (_AB.TOTAL, 'readyForBattleHT'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleHTAchievement),
 (_AB.TOTAL, 'readyForBattleSPG'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleSPGAchievement),
 (_AB.TOTAL, 'readyForBattleATSPG'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleATSPGAchievement),
 (_AB.TOTAL, 'readyForBattleAllianceUSSR'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleAllianceUSSRAchievement),
 (_AB.TOTAL, 'readyForBattleAllianceGermany'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleAllianceGermanyAchievement),
 (_AB.TOTAL, 'readyForBattleAllianceUSA'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleAllianceUSAAchievement),
 (_AB.TOTAL, 'readyForBattleAllianceFrance'): _CustomAchieveFactory.get(_as.ready_for_battle.ReadyForBattleAllianceFranceAchievement),
 (_AB.TOTAL, 'testartilleryman'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.TOTAL, 'EFC2016Goleador'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.TOTAL, 'markIBomberman'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.TOTAL, 'markIRepairer'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.TOTAL, 'markI100Years'): _CustomAchieveFactory.get(_as.class_progress.MarkI100Years),
 (_AB.TOTAL, 'FE18ClosedStage'): _AchieveFactory.get(_abstract_achievements.StageAchievement),
 (_AB.TOTAL, 'FE18SoloStriker'): _AchieveFactory.get(_abstract_achievements.StageAchievement),
 (_AB.TOTAL, 'FE18SoloMidfielder'): _AchieveFactory.get(_abstract_achievements.StageAchievement),
 (_AB.TOTAL, 'FE18SoloDefender'): _AchieveFactory.get(_abstract_achievements.StageAchievement),
 (_AB.TOTAL, 'superTesterVeteran'): _AchieveFactory.get(_abstract_achievements.StageAchievement),
 (_AB.TOTAL, 'superTesterVeteranCross'): _AchieveFactory.get(_abstract_achievements.StageAchievement),
 (_AB.CLAN, 'medalRotmistrov'): _CustomAchieveFactory.get(_as.class_progress.MedalRotmistrovAchievement),
 (_AB.RATED_7X7, 'strategicOperations'): _CustomAchieveFactory.get(_as.class_progress.StrategicOperationsAchievement),
 (_AB.RATED_7X7, 'tacticalAdvantage'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.RATED_7X7, 'tacticalSkill'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.RATED_7X7, 'secretOperations'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FORT, 'fireAndSword'): _AchieveFactory.get(_abstract_achievements.DeprecatedClassAchievement),
 (_AB.FORT, 'soldierOfFortune'): _CustomAchieveFactory.get(_as.class_progress.SoldierOfFortuneAchievement),
 (_AB.FORT, 'kampfer'): _AchieveFactory.get(_abstract_achievements.DeprecatedClassAchievement),
 (_AB.FORT, 'conqueror'): _AchieveFactory.get(_abstract_achievements.DeprecatedClassAchievement),
 (_AB.FORT, 'counterblow'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FORT, 'crusher'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.HISTORICAL, 'makerOfHistory'): _CustomAchieveFactory.get(_as.class_progress.MakerOfHistoryAchievement),
 (_AB.HISTORICAL, 'guardsman'): _CustomAchieveFactory.get(_as.class_progress.GuardsmanAchievement),
 (_AB.SINGLE, 'diehard'): _CustomAchieveFactory.get(_as.series.DiehardAchievement),
 (_AB.SINGLE, 'invincible'): _CustomAchieveFactory.get(_as.series.InvincibleAchievement),
 (_AB.SINGLE, 'tacticalBreakthrough'): _CustomAchieveFactory.get(_as.series.TacticalBreakthroughAchievement),
 (_AB.SINGLE, 'handOfDeath'): _CustomAchieveFactory.get(_as.series.HandOfDeathAchievement),
 (_AB.SINGLE, 'armorPiercer'): _CustomAchieveFactory.get(_as.series.ArmorPiercerAchievement),
 (_AB.SINGLE, 'titleSniper'): _CustomAchieveFactory.get(_as.series.TitleSniperAchievement),
 (_AB.SINGLE, 'victoryMarch'): _CustomAchieveFactory.get(_as.series.VictoryMarchAchievement),
 (_AB.SINGLE_7X7, 'victoryMarch'): _CustomAchieveFactory.get(_as.series.VictoryMarchClubAchievement),
 (_AB.SINGLE, 'battleCitizen'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'WFC2014'): _CustomAchieveFactory.get(_as.series.WFC2014Achievement),
 (_AB.SINGLE, 'deathTrack'): _CustomAchieveFactory.get(_as.series.DeathTrackAchievement),
 (_AB.SINGLE, 'moonSphere'): _CustomAchieveFactory.get(_as.regular.MoonSphereAchievement),
 (_AB.SINGLE, 'aimer'): _CustomAchieveFactory.get(_as.series.AimerAchievement),
 (_AB.SINGLE, 'tankwomen'): _CustomAchieveFactory.get(_as.simple_progress.TankwomenAchievement),
 (_AB.SINGLE, 'operationWinter'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'fallout'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'fallout2'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'falloutSingleWolf'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'falloutPackOfWolfs'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'falloutSteelHunter'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'falloutAlwaysInLine'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'EFC2016'): _CustomAchieveFactory.get(_as.series.EFC2016Achievement),
 (_AB.SINGLE, 'markIProtector'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'markIBaseProtector'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'xmasTreeBronze'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'xmasTreeSilver'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'xmasTreeGold'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'rankedBattlesPioneer'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'rankedBattlesHero'): _CustomAchieveFactory.get(_as.series.RankedBattlesHeroAchievement),
 (_AB.SINGLE, 'rankedBattlesSeasonOne'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'HE17A1'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'HE17A2'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'HE17A3'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'NY18A1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY18A2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY18A3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'FE18Universal'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'FE18Collection1'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'FE18Collection2'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'FE18Collection3'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'FE18OpenRegistration'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'FE18OpenPlayOff'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'FE18OpenFinalStage'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'FE18OpenFirstPlace'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'medalKursk'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'streamersEventUsha'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'streamersEventJove'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'streamersEventAmway921'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'streamersEventLeBwA'): _AchieveFactory.get(_as.regular.Achieved),
 (_AB.SINGLE, 'DdaymarathonMedal'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'twitchPrime'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'twitchPrime2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'twitchPrime3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'twitchPrime4'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'alphaTester'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, 'betaTester'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '11YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '10YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '09YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '08YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '07YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '06YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '05YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '04YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '03YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '02YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, '01YearsOfService'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, 'betaTester_cn'): _AchieveFactory.get(LoyalServiceAchievement),
 (_AB.SINGLE, 'NY19A1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY19A2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY19A3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'se12019Medal'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'Fest19Collection1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'Fest19Collection2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'Fest19Collection3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'Fest19Racer'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'Fest19Offspring'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'RP2018firstmed'): _AchieveFactory.get(_as.regular.ReferralProgramSingleAchievement),
 (_AB.TOTAL, 'RP2018secondmed'): _AchieveFactory.get(_as.regular.ReferralProgramSingleAchievement),
 (_AB.TOTAL, 'RP2018thirdmed'): _AchieveFactory.get(_as.regular.ReferralProgramSingleAchievement),
 (_AB.TOTAL, 'RP2018sergeant'): _CustomAchieveFactory.get(_as.class_progress.ReferralProgramClassAchievement),
 (_AB.TOTAL, 'rankedDivisionFighter'): _CustomAchieveFactory.get(_as.class_progress.RankedDivisionFighterAchievement),
 (_AB.TOTAL, 'rankedStayingPower'): _CustomAchieveFactory.get(_as.class_progress.RankedStayingPowerAchievement),
 (_AB.TEAM_7X7, 'geniusForWarMedal'): _CustomAchieveFactory.get(_as.simple_progress.GeniusForWarAchievement),
 (_AB.TEAM_7X7, 'wolfAmongSheepMedal'): _CustomAchieveFactory.get(_as.simple_progress.WolfAmongSheepAchievement),
 (_AB.TEAM_7X7, 'fightingReconnaissanceMedal'): _CustomAchieveFactory.get(_as.simple_progress.FightingReconnaissanceAchievement),
 (_AB.TEAM_7X7, 'crucialShotMedal'): _CustomAchieveFactory.get(_as.simple_progress.CrucialShotAchievement),
 (_AB.TEAM_7X7, 'forTacticalOperations'): _CustomAchieveFactory.get(_as.class_progress.ForTacticalOperationsAchievement),
 (_AB.TEAM_7X7, 'battleTested'): _CustomAchieveFactory.get(_as.class_progress.BattleTestedAchievement),
 (_AB.TEAM_7X7, 'guerrillaMedal'): _CustomAchieveFactory.get(_as.simple_progress.GuerrillaAchievement),
 (_AB.TEAM_7X7, 'infiltratorMedal'): _CustomAchieveFactory.get(_as.simple_progress.InfiltratorAchievement),
 (_AB.TEAM_7X7, 'sentinelMedal'): _CustomAchieveFactory.get(_as.simple_progress.SentinelAchievement),
 (_AB.TEAM_7X7, 'prematureDetonationMedal'): _CustomAchieveFactory.get(_as.simple_progress.PrematureDetonationAchievement),
 (_AB.TEAM_7X7, 'bruteForceMedal'): _CustomAchieveFactory.get(_as.simple_progress.BruteForceAchievement),
 (_AB.TEAM_7X7, 'promisingFighterMedal'): _CustomAchieveFactory.get(_as.simple_progress.PromisingFighterAchievement),
 (_AB.TEAM_7X7, 'heavyFireMedal'): _CustomAchieveFactory.get(_as.simple_progress.HeavyFireAchievement),
 (_AB.TEAM_7X7, 'rangerMedal'): _CustomAchieveFactory.get(_as.simple_progress.RangerAchievement),
 (_AB.TEAM_7X7, 'fireAndSteelMedal'): _CustomAchieveFactory.get(_as.simple_progress.FireAndSteelAchievement),
 (_AB.TEAM_7X7, 'pyromaniacMedal'): _CustomAchieveFactory.get(_as.simple_progress.PyromaniacAchievement),
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
 (_AB.FALLOUT, 'stormLord'): _CustomAchieveFactory.get(_as.class_progress.StormLordAchievement),
 (_AB.FALLOUT, 'winnerLaurels'): _CustomAchieveFactory.get(_as.class_progress.WinnerLaurelsAchievement),
 (_AB.FALLOUT, 'shoulderToShoulder'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FALLOUT, 'aloneInTheField'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FALLOUT, 'fallenFlags'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FALLOUT, 'effectiveSupport'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FALLOUT, 'falloutDieHard'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FALLOUT, 'predator'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FALLOUT, 'unreachable'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FALLOUT, 'champion'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.FALLOUT, 'bannerman'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.EPIC_BATTLE, 'epicBattle1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.EPIC_BATTLE, 'epicBattle2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.EPIC_BATTLE, 'epicBattle3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.EPIC_BATTLE, 'epicBattle4'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.UNIQUE, 'BR2019Top1Solo'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.UNIQUE, 'BR2019Top1Squad'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'BR2019Title25'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'BR2019Title15'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'BR2019Title5'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'october19'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'november19'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'december19'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'january20'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'february20'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'march20'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'june20'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'september20'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'october20'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'january21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'february21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'march21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'april21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'may21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'june21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'july21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'august21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'september21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'october21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'november21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'december21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'june22'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'july22'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'august22'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'september22'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY20A1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY20A2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY20A3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobLebwa'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobYusha'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobAmway921'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobKorbenDallas'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobMailand'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobSkill4ltu'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobDezgamez'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobAwesomeEpicGuys'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobTigers'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'medalBobDragons'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bootcampMedal'): _AchieveFactory.get(_abstract_achievements.RegularAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_4'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_5'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_6'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_7'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_8'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_8ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_8quest'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BattlePassCommonPr_9'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'collectorVehicle'): _NationAchieveFactory.get(_as.nation_specific.VehicleCollectorAchievement),
 (_AB.SINGLE, 'dedicationMedal1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'dedicationMedal2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'dedicationMedal3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'dedicationMedal4'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'TenYearsCountdownParticipation'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'TenYearsCountdownStageMedal'): _AchieveFactory.get(_abstract_achievements.StageAchievement),
 (_AB.SINGLE, 'TenYearsCountdownSPGEventMedal'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'TenYearsCountdownBrawlMedal'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'BigAnniversaryMedal_CN'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 HONORED_RANK_RECORD: _CustomAchieveFactory.get(_as.regular.HonoredRankAchievement),
 (_AB.SINGLE, 'se2020Medal'): _AchieveFactory.get(_abstract_achievements.QuestAchievement),
 (_AB.SINGLE, 'hw2019Medal'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'hw2019Medal1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'hw2019Medal2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'hw2019Medal3'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 RARE_STORAGE_RECORD: _RareAchievesFactory.get(),
 (_AB.TOTAL, 'wtHunterWins'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wtBossWins'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wtSpecBossDefeat'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY21_AtmsphrLevel'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY21_CelebChallenge'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Lebwa_ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Yusha_ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Amway921_ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021KorbenDallas_ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021NearYou_ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021EvilGranny_ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Vspishka_ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Inspirer_ru'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Circon_eu'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Dakillzor_eu'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021NewMulti2k_eu'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Orzanel_eu'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Cabbagemechanic_na'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021TragicLoss_na'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021CmdrAF_na'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021MasterTortoise_apac'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021SummerTiger_apac'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'bob2021Maharlika_apac'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'gagarin21'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wtxHunterWins'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wtxBossWins'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wtxSpecBossDefeat'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'whiteTiger2012'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'hw2021Medal1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'hw2021Medal2'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY22_AtmsphrLevel'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'NY22_CelebChallenge'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'lunarNY2022Progression'): _AchieveFactory.get(_abstract_achievements.StageAchievement),
 (_AB.UNIQUE, 'oowTankmanWins'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.UNIQUE, 'oowStrategistWins'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'oowCompetetiveWin'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'oowCBTParticipant'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wclTournamentParticipant'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wclParticipant'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wt2022HunterWins'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wt2022BossWins'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.TOTAL, 'wt2022SpecBossDefeat'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement),
 (_AB.SINGLE, 'comp7Season1'): _AchieveFactory.get(_abstract_achievements.DeprecatedAchievement)}
for _nID, _ in enumerate(nations.NAMES):
    _ACHIEVEMENTS_BY_NAME[_AB.TOTAL, 'tankExpert%d' % _nID] = _NationAchieveFactory.get(_as.nation_specific.TankExpertAchievement, _nID)
    _ACHIEVEMENTS_BY_NAME[_AB.TOTAL, 'mechanicEngineer%d' % _nID] = _NationAchieveFactory.get(_as.nation_specific.MechEngineerAchievement, _nID)
    _ACHIEVEMENTS_BY_NAME[_AB.TOTAL, 'collectorVehicle%d' % _nID] = _NationAchieveFactory.get(_as.nation_specific.VehicleCollectorAchievement, _nID)

def getAchievementFactory(record, dossier=None):
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
