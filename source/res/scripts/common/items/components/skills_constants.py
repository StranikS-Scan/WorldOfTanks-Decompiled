# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/skills_constants.py
SKILL_NAMES = ('reserved', 'commander', 'radioman', 'driver', 'gunner', 'loader', 'repair', 'fireFighting', 'camouflage', 'brotherhood', 'reserved', 'reserved', 'reserved', 'reserved', 'reserved', 'reserved', 'commander_tutor', 'commander_eagleEye', 'commander_sixthSense', 'commander_expert', 'commander_universalist', 'reserved', 'reserved', 'reserved', 'reserved', 'reserved', 'reserved', 'reserved', 'driver_virtuoso', 'driver_smoothDriving', 'driver_badRoadsKing', 'driver_rammingMaster', 'driver_tidyPerson', 'reserved', 'reserved', 'reserved', 'reserved', 'gunner_gunsmith', 'gunner_sniper', 'gunner_smoothTurret', 'gunner_rancorous', 'reserved', 'reserved', 'reserved', 'reserved', 'reserved', 'loader_pedant', 'loader_desperado', 'loader_intuition', 'reserved', 'reserved', 'reserved', 'reserved', 'radioman_inventor', 'radioman_finder', 'radioman_retransmitter', 'radioman_lastEffort', 'reserved', 'reserved', 'reserved', 'reserved')
SKILL_INDICES = dict(((x[1], x[0]) for x in enumerate(SKILL_NAMES) if not x[1].startswith('reserved')))
ROLES = frozenset(('commander', 'radioman', 'driver', 'gunner', 'loader'))
ROLE_LIMITS = {'commander': 1,
 'driver': 1}
COMMON_SKILLS = frozenset(('repair', 'fireFighting', 'camouflage', 'brotherhood'))
ROLES_AND_COMMON_SKILLS = ROLES | COMMON_SKILLS
COMMANDER_SKILLS = frozenset(('commander_tutor', 'commander_expert', 'commander_universalist', 'commander_sixthSense', 'commander_eagleEye'))
SKILLS_BY_ROLES = {'commander': COMMON_SKILLS.union(COMMANDER_SKILLS),
 'driver': COMMON_SKILLS.union(('driver_tidyPerson', 'driver_smoothDriving', 'driver_virtuoso', 'driver_badRoadsKing', 'driver_rammingMaster')),
 'gunner': COMMON_SKILLS.union(('gunner_smoothTurret', 'gunner_sniper', 'gunner_rancorous', 'gunner_gunsmith')),
 'loader': COMMON_SKILLS.union(('loader_pedant', 'loader_desperado', 'loader_intuition')),
 'radioman': COMMON_SKILLS.union(('radioman_finder', 'radioman_inventor', 'radioman_lastEffort', 'radioman_retransmitter'))}
ACTIVE_SKILLS = SKILLS_BY_ROLES['commander'] | SKILLS_BY_ROLES['radioman'] | SKILLS_BY_ROLES['driver'] | SKILLS_BY_ROLES['gunner'] | SKILLS_BY_ROLES['loader']
PERKS = frozenset(('brotherhood', 'commander_sixthSense', 'commander_expert', 'driver_tidyPerson', 'gunner_rancorous', 'gunner_sniper', 'loader_pedant', 'loader_desperado', 'loader_intuition', 'radioman_lastEffort'))
