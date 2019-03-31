# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/arena_achievements.py
# Compiled at: 2011-01-18 20:36:18
ACHIEVEMENT_NAMES = ('medalWittmann', 'medalOrlik', 'medalOskin', 'medalHalonen', 'medalBurda', 'medalBillotte', 'medalKolobanov', 'medalFadin', 'invincible', 'diehard', 'raider', 'kamikaze', 'sniper', 'killing', 'piercing')
ACHIEVEMENTS_INDICES = dict(((x[1], x[0]) for x in enumerate(ACHIEVEMENT_NAMES)))
ACHIEVEMENT_CONDITIONS = {'medalWittmann': {'minVictimLevel': 4,
                   'minTankOrAtspgKills': 7,
                   'minSpgKills': 10},
 'medalOrlik': {'minVictimLevelDelta': 2,
                'minKills': 3},
 'medalOskin': {'minVictimLevelDelta': 2,
                'minKills': 3},
 'medalHalonen': {'minVictimLevelDelta': 2,
                  'minKills': 3},
 'medalBurda': {'minKills': 5},
 'medalBillotte': {'hpPercentage': 20,
                   'minCrits': 5,
                   'minKills': 1},
 'medalKolobanov': {'teamDiff': 5},
 'kamikaze': {'levelDelta': 1}}
