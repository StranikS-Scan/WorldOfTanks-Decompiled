# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_heroes.py
# Compiled at: 2010-11-10 17:31:37
ACHIEVEMENT_NAMES = ('reserved', 'warrior', 'invader', 'sniper', 'defender', 'steelwall', 'supporter', 'scout')
ACHIEVEMENTS_INDICES = dict(((x[1], x[0]) for x in enumerate(ACHIEVEMENT_NAMES)))
ACHIEVEMENT_TEXTS = {'warrior': '#achievements:warrior',
 'invader': '#achievements:invader',
 'sniper': '#achievements:sniper',
 'defender': '#achievements:defender',
 'steelwall': '#achievements:steelwall',
 'supporter': '#achievements:supporter',
 'scout': '#achievements:scout'}
ACHIEVEMENT_CONDITIONS = {'warrior': {'minFrags': 6},
 'invader': {'minCapturePts': 80},
 'sniper': {'minAccuracy': 0.85,
            'minShots': 10,
            'minDamage': 1000},
 'defender': {'minPoints': 70},
 'steelwall': {'minDamage': 1000,
               'minHits': 11},
 'supporter': {'minAssists': 6},
 'scout': {'minDetections': 9}}
