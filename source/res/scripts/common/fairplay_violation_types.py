# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/fairplay_violation_types.py
from soft_exception import SoftException
from extension_utils import ResMgr
from constants import FairplayViolationType, ARENA_BONUS_TYPE, PENALTY_TYPES, IS_CLIENT
if IS_CLIENT:
    from gui.impl.gen import R
_CONFIG_FILE = 'scripts/item_defs/fairplay_violation_types.xml'
_XML_NAMESPACE = 'xmlns:xmlref'

class FairplayViolations(object):
    __violation2type = {}
    __type2violations = {}

    @classmethod
    def getViolationType(cls, violationName):
        return cls.__violation2type.get(violationName)

    @classmethod
    def setViolationType(cls, violationName, violationType):
        cls.__violation2type[violationName] = violationType
        cls.__type2violations.setdefault(violationType, []).append(violationName)

    @classmethod
    def getViolationsByType(cls, violationType):
        return cls.__type2violations[violationType]


def getViolationsByMask(violationsMask):
    violationNames = []
    for name in FAIRPLAY_VIOLATIONS_NAMES:
        if violationsMask & FAIRPLAY_VIOLATIONS_MASKS[name] != 0:
            violationNames.append(name)

    return violationNames


def getViolationTypesMask(violationsMask):
    violationNames = getViolationsByMask(violationsMask)
    vTypesMask = 0
    for violation in violationNames:
        vTypesMask |= FairplayViolations.getViolationType(violation)

    return vTypesMask


FAIRPLAY_EXCLUDED_ARENA_BONUS_TYPES = [ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD]
FAIRPLAY_VIOLATIONS_NAMES = []
FAIRPLAY_VIOLATIONS_MASKS = {}
BASE_VIOLATIONS = ['deserter', 'suicide', 'afk']

def init():
    if not FAIRPLAY_VIOLATIONS_NAMES:
        section = ResMgr.openSection(_CONFIG_FILE)['']
        violationTypes = _readViolations(section)
        initViolationTypes(violationTypes)


def _readViolations(section):
    if section is None:
        raise SoftException('Cannot find root section')
    violations = []
    for violation, item in section.items():
        if violation == _XML_NAMESPACE:
            continue
        vType = item.readString('violationType')
        if vType and not hasattr(FairplayViolationType, vType.upper()):
            raise SoftException('Wrong Attibute {} in class {}'.format(vType, FairplayViolations))
        elif not vType:
            raise SoftException('Empty Attibute violationType in class {}'.format(vType, FairplayViolations))
        violations.append((violation, vType))

    return violations


def initViolationTypes(violationTypes):
    for idx, (violationType, vType) in enumerate(violationTypes):
        if hasattr(FairplayViolations, violationType):
            raise SoftException('Attibute {} already in class {}'.format(violationType, FairplayViolations))
        violationName = violationType.lower()
        setattr(FairplayViolations, violationType, violationName)
        FairplayViolations.setViolationType(violationName, getattr(FairplayViolationType, vType))
        FAIRPLAY_VIOLATIONS_NAMES.append(violationName)
        FAIRPLAY_VIOLATIONS_MASKS.update({violationName: 1 << idx})


def getPenaltyTypeAndViolationName(fairplayViolations, banDuration):
    from account_shared import getFairPlayViolationName
    warning, penalty, _ = fairplayViolations
    getViolationType = FairplayViolations.getViolationType
    if banDuration:
        violationName = getFairPlayViolationName(penalty)
        return (PENALTY_TYPES.BAN, violationName, getViolationType(violationName) == FairplayViolationType.AFK)
    if penalty != 0:
        violationName = getFairPlayViolationName(penalty)
        return (PENALTY_TYPES.PENALTY, violationName, getViolationType(violationName) == FairplayViolationType.AFK)
    if warning != 0:
        violationName = getFairPlayViolationName(warning)
        return (PENALTY_TYPES.WARNING, violationName, getViolationType(violationName) == FairplayViolationType.AFK)


def getFairplayViolationLocale(violationName):
    path = R.strings.dialogs.punishmentWindow.reason
    accessor = path.dyn(violationName)
    if accessor.isValid():
        return accessor()
    for violation in BASE_VIOLATIONS:
        if violation in violationName:
            return path.dyn(violation)()

    return path.mixed()
