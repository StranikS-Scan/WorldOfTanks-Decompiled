# Embedded file name: scripts/common/dossiers1/achievements.py


class ACHIEVEMENT_TYPE:
    REPEATABLE = 'repeatable'
    CLASS = 'class'
    CUSTOM = 'custom'
    SERIES = 'series'


class ACHIEVEMENT_SECTION:
    EPIC = 'epic'
    BATTLE = 'battle'
    SPECIAL = 'special'
    CLASS = 'class'
    ACTION = 'action'
    MEMORIAL = 'memorial'
    GROUP = 'group'


_AT = ACHIEVEMENT_TYPE
_AS = ACHIEVEMENT_SECTION
DEFAULT_WEIGHT = -1

def _makeAchieve(aType, section, weight = DEFAULT_WEIGHT, recordFieldName = None, curRecordFiledName = None):
    return {'type': aType,
     'section': section,
     'record': recordFieldName,
     'curRecord': curRecordFiledName,
     'weight': weight}


ACHIEVEMENTS = {'warrior': _makeAchieve(_AT.REPEATABLE, _AS.BATTLE, 1),
 'invader': _makeAchieve(_AT.REPEATABLE, _AS.BATTLE, 11),
 'sniper': _makeAchieve(_AT.REPEATABLE, _AS.BATTLE, 2),
 'defender': _makeAchieve(_AT.REPEATABLE, _AS.BATTLE, 10),
 'steelwall': _makeAchieve(_AT.REPEATABLE, _AS.BATTLE, 9),
 'supporter': _makeAchieve(_AT.REPEATABLE, _AS.BATTLE, 3),
 'scout': _makeAchieve(_AT.REPEATABLE, _AS.BATTLE, 12),
 'evileye': _makeAchieve(_AT.REPEATABLE, _AS.BATTLE, 8),
 'medalKay': _makeAchieve(_AT.CLASS, _AS.CLASS, 62, 'battleHeroes'),
 'medalCarius': _makeAchieve(_AT.CLASS, _AS.CLASS, 63, 'frags'),
 'medalKnispel': _makeAchieve(_AT.CLASS, _AS.CLASS, 65),
 'medalPoppel': _makeAchieve(_AT.CLASS, _AS.CLASS, 66, 'spotted'),
 'medalAbrams': _makeAchieve(_AT.CLASS, _AS.CLASS, 67, 'winAndSurvived'),
 'medalLeClerc': _makeAchieve(_AT.CLASS, _AS.CLASS, 68, 'capturePoints'),
 'medalLavrinenko': _makeAchieve(_AT.CLASS, _AS.CLASS, 69, 'droppedCapturePoints'),
 'medalEkins': _makeAchieve(_AT.CLASS, _AS.CLASS, 64, 'frags8p'),
 'markOfMastery': _makeAchieve(_AT.CLASS, _AS.CLASS),
 'heroesOfRassenay': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 4),
 'medalLafayettePool': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 5),
 'medalRadleyWalters': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 6),
 'huntsman': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 13),
 'medalKolobanov': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 17),
 'medalNikolas': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 18),
 'medalOskin': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 19),
 'medalLehvaslaiho': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 20),
 'medalOrlik': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 21),
 'medalHalonen': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 22),
 'medalTamadaYoshio': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 23),
 'medalBurda': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 24),
 'medalDumitru': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 25),
 'medalPascucci': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 26),
 'medalDeLanglade': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 27),
 'medalTarczay': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 30),
 'medalBrunoPietro': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 31),
 'medalBillotte': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 32),
 'medalFadin': _makeAchieve(_AT.REPEATABLE, _AS.EPIC, 33),
 'kamikaze': _makeAchieve(_AT.REPEATABLE, _AS.SPECIAL, 29),
 'raider': _makeAchieve(_AT.REPEATABLE, _AS.SPECIAL, 34),
 'mousebane': _makeAchieve(_AT.REPEATABLE, _AS.SPECIAL, 40),
 'beasthunter': _makeAchieve(_AT.REPEATABLE, _AS.SPECIAL, 42),
 'sinai': _makeAchieve(_AT.REPEATABLE, _AS.SPECIAL, 43),
 'pattonValley': _makeAchieve(_AT.REPEATABLE, _AS.SPECIAL, 41),
 'bombardier': _makeAchieve(_AT.REPEATABLE, _AS.SPECIAL, 35),
 'sturdy': _makeAchieve(_AT.REPEATABLE, _AS.MEMORIAL, 38),
 'ironMan': _makeAchieve(_AT.REPEATABLE, _AS.MEMORIAL, 37),
 'luckyDevil': _makeAchieve(_AT.REPEATABLE, _AS.MEMORIAL, 39),
 'tankExpert': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 47),
 'tankExpert0': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 54),
 'tankExpert1': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 55),
 'tankExpert2': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 56),
 'tankExpert3': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 57),
 'tankExpert4': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 58),
 'tankExpert5': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 59),
 'tankExpert6': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'tankExpert7': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'tankExpert8': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'tankExpert9': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'tankExpert10': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'tankExpert11': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'tankExpert12': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'tankExpert13': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'tankExpert14': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 46),
 'mechanicEngineer0': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 48),
 'mechanicEngineer1': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 49),
 'mechanicEngineer2': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 50),
 'mechanicEngineer3': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 51),
 'mechanicEngineer4': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 52),
 'mechanicEngineer5': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL, 53),
 'mechanicEngineer6': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer7': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer8': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer9': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer10': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer11': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer12': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer13': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'mechanicEngineer14': _makeAchieve(_AT.CUSTOM, _AS.SPECIAL),
 'medalCrucialContribution': _makeAchieve(_AT.REPEATABLE, _AS.GROUP, 14),
 'medalBrothersInArms': _makeAchieve(_AT.REPEATABLE, _AS.GROUP, 15),
 'titleSniper': _makeAchieve(_AT.SERIES, _AS.SPECIAL, 45, 'maxSniperSeries', 'sniperSeries'),
 'invincible': _makeAchieve(_AT.SERIES, _AS.SPECIAL, 28, 'maxInvincibleSeries', 'invincibleSeries'),
 'diehard': _makeAchieve(_AT.SERIES, _AS.SPECIAL, 7, 'maxDiehardSeries', 'diehardSeries'),
 'handOfDeath': _makeAchieve(_AT.SERIES, _AS.SPECIAL, 36, 'maxKillingSeries', 'killingSeries'),
 'armorPiercer': _makeAchieve(_AT.SERIES, _AS.SPECIAL, 44, 'maxPiercingSeries', 'piercingSeries'),
 'rareAchievements': _makeAchieve(_AT.CUSTOM, _AS.ACTION),
 'whiteTiger': _makeAchieve(_AT.REPEATABLE, _AS.ACTION),
 'medalWittmann': _makeAchieve(_AT.REPEATABLE, _AS.ACTION, 16)}
ACHIEVEMENT_SECTIONS_ORDER = (_AS.BATTLE,
 _AS.SPECIAL,
 _AS.EPIC,
 _AS.GROUP,
 _AS.MEMORIAL,
 _AS.CLASS,
 _AS.ACTION)
ACHIEVEMENT_SECTIONS_INDICES = dict(((n, i) for i, n in enumerate(ACHIEVEMENT_SECTIONS_ORDER)))
