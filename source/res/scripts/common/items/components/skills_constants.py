# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/skills_constants.py
from collections import OrderedDict
SKILL_NAMES = ('reserved', 'commander', 'radioman', 'driver', 'gunner', 'loader', 'repair', 'fireFighting', 'camouflage', 'brotherhood', 'any', 'reserved', 'reserved', 'reserved', 'reserved', 'reserved', 'commander_tutor', 'commander_eagleEye', 'commander_sixthSense', 'commander_expert', 'commander_universalist', 'commander_enemyShotPredictor', 'commander_practical', 'commander_emergency', 'commander_coordination', 'reserved', 'reserved', 'reserved', 'driver_virtuoso', 'driver_smoothDriving', 'driver_badRoadsKing', 'driver_rammingMaster', 'driver_tidyPerson', 'driver_motorExpert', 'driver_reliablePlacement', 'reserved', 'reserved', 'gunner_gunsmith', 'gunner_sniper', 'gunner_smoothTurret', 'gunner_rancorous', 'gunner_focus', 'gunner_quickAiming', 'gunner_armorer', 'reserved', 'reserved', 'loader_pedant', 'loader_desperado', 'loader_intuition', 'loader_perfectCharge', 'loader_ammunitionImprove', 'loader_melee', 'reserved', 'radioman_inventor', 'radioman_finder', 'radioman_retransmitter', 'reserved', 'radioman_interference', 'radioman_signalInterception', 'radioman_sideBySide', 'radioman_expert')

class ROLE_NAMES(object):
    COMMANDER = 'commander'
    RADIOMAN = 'radioman'
    DRIVER = 'driver'
    GUNNER = 'gunner'
    LOADER = 'loader'


SKILL_INDICES = dict(((x[1], x[0]) for x in enumerate(SKILL_NAMES) if not x[1].startswith('reserved')))
ORDERED_ROLES = (ROLE_NAMES.COMMANDER,
 ROLE_NAMES.GUNNER,
 ROLE_NAMES.DRIVER,
 ROLE_NAMES.RADIOMAN,
 ROLE_NAMES.LOADER)
ROLES = frozenset(ORDERED_ROLES)
COMMON_SKILL_ROLE_TYPE = 'common'
ROLE_LIMITS = {ROLE_NAMES.COMMANDER: 1,
 ROLE_NAMES.DRIVER: 1}
COMMON_SKILLS_ORDERED = ('brotherhood', 'repair', 'camouflage')
COMMON_SKILLS = frozenset(COMMON_SKILLS_ORDERED)
ROLES_AND_COMMON_SKILLS = ROLES | COMMON_SKILLS
COMMANDER_SKILLS = ('commander_eagleEye', 'commander_emergency', 'commander_tutor', 'commander_coordination', 'commander_enemyShotPredictor', 'commander_practical', 'commander_sixthSense')
GUNNER_SKILLS = ('gunner_smoothTurret', 'gunner_sniper', 'gunner_rancorous', 'gunner_focus', 'gunner_quickAiming', 'gunner_armorer')
DRIVER_SKILLS = ('driver_virtuoso', 'driver_smoothDriving', 'driver_badRoadsKing', 'driver_reliablePlacement', 'driver_rammingMaster', 'driver_motorExpert')
RADIOMAN_SKILLS = ('radioman_finder', 'radioman_sideBySide', 'radioman_interference', 'radioman_signalInterception', 'radioman_expert', 'fireFighting')
LOADER_SKILLS = ('loader_desperado', 'loader_pedant', 'loader_intuition', 'loader_perfectCharge', 'loader_melee', 'loader_ammunitionImprove')
COMMON_ROLE = 'common'
SKILLS_BY_ROLES_ORDERED = {ROLE_NAMES.COMMANDER: COMMON_SKILLS_ORDERED + COMMANDER_SKILLS,
 ROLE_NAMES.GUNNER: COMMON_SKILLS_ORDERED + GUNNER_SKILLS,
 ROLE_NAMES.DRIVER: COMMON_SKILLS_ORDERED + DRIVER_SKILLS,
 ROLE_NAMES.RADIOMAN: COMMON_SKILLS_ORDERED + RADIOMAN_SKILLS,
 ROLE_NAMES.LOADER: COMMON_SKILLS_ORDERED + LOADER_SKILLS}
SKILL_NAMES_ORDERED = COMMON_SKILLS_ORDERED + COMMANDER_SKILLS + GUNNER_SKILLS + DRIVER_SKILLS + RADIOMAN_SKILLS + LOADER_SKILLS
SKILL_INDICES_ORDERED = dict(((x[1], x[0]) for x in enumerate(SKILL_NAMES_ORDERED)))
SKILLS_BY_ROLES = {}
for role, skills in SKILLS_BY_ROLES_ORDERED.iteritems():
    SKILLS_BY_ROLES.setdefault(role, frozenset(skills))

ROLES_BY_SKILLS = {}
for role, skills in SKILLS_BY_ROLES.iteritems():
    for skill in skills:
        ROLES_BY_SKILLS.setdefault(skill, set()).add(role)

ACTIVE_SKILLS = SKILLS_BY_ROLES[ROLE_NAMES.COMMANDER] | SKILLS_BY_ROLES[ROLE_NAMES.RADIOMAN] | SKILLS_BY_ROLES[ROLE_NAMES.DRIVER] | SKILLS_BY_ROLES[ROLE_NAMES.GUNNER] | SKILLS_BY_ROLES[ROLE_NAMES.LOADER]
ACTIVE_NOT_GROUP_SKILLS = frozenset(set(ACTIVE_SKILLS) - set(COMMON_SKILLS_ORDERED))
ACTIVE_FREE_SKILLS = ACTIVE_SKILLS | {'any'}
UNLEARNABLE_SKILLS = ('commander_sixthSense',)
LEARNABLE_ACTIVE_SKILLS = ACTIVE_SKILLS.difference(UNLEARNABLE_SKILLS)
LEARNABLE_COMMANDER_SKILLS = SKILLS_BY_ROLES[ROLE_NAMES.COMMANDER].difference(UNLEARNABLE_SKILLS)
ALL_SKILLS_BY_ROLE_TYPE = OrderedDict(((COMMON_ROLE, COMMON_SKILLS_ORDERED),
 (ROLE_NAMES.COMMANDER, tuple((skill for skill in COMMANDER_SKILLS if skill not in UNLEARNABLE_SKILLS))),
 (ROLE_NAMES.GUNNER, GUNNER_SKILLS),
 (ROLE_NAMES.DRIVER, DRIVER_SKILLS),
 (ROLE_NAMES.RADIOMAN, RADIOMAN_SKILLS),
 (ROLE_NAMES.LOADER, LOADER_SKILLS)))

class ParamMeasureType(object):
    PERCENTS = 'percents'
    SECONDS = 'seconds'
    PERCENT_GAP = 'percentGap'
    MPH = 'mph'
    METERS = 'meters'


class ParamSignType(object):
    PLUS = 'plus'
    MINUS = 'minus'
    SIGN_LESS = 'signLess'


class SkillTypeName(object):
    MAIN = 'main'
    SITUATIONAL = 'situational'
    COMMON = 'common'
    COMMANDER_SPECIAL = 'commanderSpecial'


class SkillUtilization(object):
    FREE_SKILL = 0
    MAJOR_SKILL = 1
    BONUS_SKILL = 2
