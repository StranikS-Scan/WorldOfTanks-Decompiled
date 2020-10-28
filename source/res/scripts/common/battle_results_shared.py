# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_results_shared.py
import struct
from itertools import izip
from constants import PREMIUM_TYPE, PREM_BONUS_TYPES
VEH_INTERACTION_DETAILS = (('spotted', 'B', 1, 0),
 ('deathReason', 'b', 10, -1),
 ('directHits', 'H', 65535, 0),
 ('directEnemyHits', 'H', 65535, 0),
 ('explosionHits', 'H', 65535, 0),
 ('piercings', 'H', 65535, 0),
 ('piercingEnemyHits', 'H', 65535, 0),
 ('damageDealt', 'I', 4294967295L, 0),
 ('damageAssistedTrack', 'H', 65535, 0),
 ('damageAssistedRadio', 'H', 65535, 0),
 ('damageAssistedStun', 'H', 65535, 0),
 ('damageAssistedSmoke', 'H', 65535, 0),
 ('damageAssistedInspire', 'H', 65535, 0),
 ('crits', 'I', 4294967295L, 0),
 ('fire', 'H', 65535, 0),
 ('stunNum', 'H', 65535, 0),
 ('stunDuration', 'f', 65535.0, 0.0),
 ('damageBlockedByArmor', 'I', 4294967295L, 0),
 ('damageReceived', 'H', 65535, 0),
 ('rickochetsReceived', 'H', 65535, 0),
 ('noDamageDirectHitsReceived', 'H', 65535, 0),
 ('targetKills', 'B', 255, 0))
VEH_INTERACTION_DETAILS_NAMES = [ x[0] for x in VEH_INTERACTION_DETAILS ]
VEH_INTERACTION_DETAILS_MAX_VALUES = dict(((x[0], x[2]) for x in VEH_INTERACTION_DETAILS))
VEH_INTERACTION_DETAILS_INIT_VALUES = [ x[3] for x in VEH_INTERACTION_DETAILS ]
VEH_INTERACTION_DETAILS_LAYOUT = ''.join([ x[1] for x in VEH_INTERACTION_DETAILS ])
VEH_INTERACTION_DETAILS_INDICES = dict(((x[1][0], x[0]) for x in enumerate(VEH_INTERACTION_DETAILS)))
VEH_INTERACTION_DETAILS_TYPES = dict(((x[0], x[1]) for x in VEH_INTERACTION_DETAILS))
VEH_INTERACTIVE_STATS = ('xp', 'damageDealt', 'capturePts', 'flagActions', 'winPoints', 'deathCount', 'resourceAbsorbed', 'stopRespawn', 'equipmentDamage', 'equipmentKills')
VEH_INTERACTIVE_STATS_INDICES = dict(((x[1], x[0]) for x in enumerate(VEH_INTERACTIVE_STATS)))
AVATAR_PRIVATE_STATS = ('ragePoints',)
AVATAR_PRIVATE_STATS_INDICES = dict(((x[1], x[0]) for x in enumerate(AVATAR_PRIVATE_STATS)))
_PREM_TYPE_TO_FACTOR100_NAMES = {PREM_BONUS_TYPES.CREDITS: {PREMIUM_TYPE.BASIC: 'premiumCreditsFactor100',
                            PREMIUM_TYPE.PLUS: 'premiumPlusCreditsFactor100',
                            PREMIUM_TYPE.VIP: 'premiumVipCreditsFactor100'},
 PREM_BONUS_TYPES.XP: {PREMIUM_TYPE.BASIC: 'premiumXPFactor100',
                       PREMIUM_TYPE.PLUS: 'premiumPlusXPFactor100',
                       PREMIUM_TYPE.VIP: 'premiumVipXPFactor100'},
 PREM_BONUS_TYPES.TMEN_XP: {PREMIUM_TYPE.BASIC: 'premiumTmenXPFactor100',
                            PREMIUM_TYPE.PLUS: 'premiumPlusTmenXPFactor100',
                            PREMIUM_TYPE.VIP: 'premiumVipXPTmenFactor100'}}

class UNIT_CLAN_MEMBERSHIP:
    NONE = 0
    ANY = 1
    SAME = 2


def dictToList(indices, d):
    l = [None] * len(indices)
    for name, index in indices.iteritems():
        l[index] = d[name]

    return l


def listToDict(names, l):
    d = {}
    for x in enumerate(names):
        d[x[1]] = l[x[0]]

    return d


class _VehicleInteractionDetailsItem(object):

    @staticmethod
    def __fmt2py(format):
        return float if format in ('f',) else int

    def __init__(self, values, offset):
        self.__values = values
        self.__offset = offset

    def __getitem__(self, key):
        return self.__values[self.__offset + VEH_INTERACTION_DETAILS_INDICES[key]]

    def __setitem__(self, key, value):
        self.__values[self.__offset + VEH_INTERACTION_DETAILS_INDICES[key]] = min(self.__fmt2py(VEH_INTERACTION_DETAILS_TYPES[key])(value), VEH_INTERACTION_DETAILS_MAX_VALUES[key])

    def __str__(self):
        return str(dict(self))

    def __iter__(self):
        return izip(VEH_INTERACTION_DETAILS_NAMES, self.__values[self.__offset:])


class VehicleInteractionDetails(object):

    def __init__(self, uniqueVehIDs, values):
        self.__uniqueVehIDs = uniqueVehIDs
        self.__values = values
        size = len(VEH_INTERACTION_DETAILS)
        self.__offsets = dict(((x[1], x[0] * size) for x in enumerate(uniqueVehIDs)))

    @staticmethod
    def fromPacked(packed):
        count = len(packed) / struct.calcsize(''.join(['<2I', VEH_INTERACTION_DETAILS_LAYOUT]))
        packedVehIDsLayout = '<%dI' % (2 * count,)
        packedVehIDsLen = struct.calcsize(packedVehIDsLayout)
        flatIDs = struct.unpack(packedVehIDsLayout, packed[:packedVehIDsLen])
        uniqueVehIDs = []
        for i in xrange(0, len(flatIDs), 2):
            uniqueVehIDs.append((flatIDs[i], flatIDs[i + 1]))

        values = struct.unpack('<' + VEH_INTERACTION_DETAILS_LAYOUT * count, packed[packedVehIDsLen:])
        return VehicleInteractionDetails(uniqueVehIDs, values)

    def __getitem__(self, uniqueVehID):
        if not isinstance(uniqueVehID, tuple):
            raise UserWarning('Argument uniqueVehID should be tuple: {}'.format(uniqueVehID))
        offset = self.__offsets.get(uniqueVehID, None)
        if offset is None:
            self.__uniqueVehIDs.append(uniqueVehID)
            offset = len(self.__values)
            self.__values += VEH_INTERACTION_DETAILS_INIT_VALUES
            self.__offsets[uniqueVehID] = offset
        return _VehicleInteractionDetailsItem(self.__values, offset)

    def __contains__(self, uniqueVehID):
        if not isinstance(uniqueVehID, tuple):
            raise UserWarning('Argument uniqueVehID should be tuple: {}'.format(uniqueVehID))
        return uniqueVehID in self.__offsets

    def __str__(self):
        return str(self.toDict())

    def pack(self):
        count = len(self.__uniqueVehIDs)
        flatIDs = []
        for uniqueID in self.__uniqueVehIDs:
            flatIDs.append(uniqueID[0])
            flatIDs.append(uniqueID[1])

        try:
            packed = struct.pack(('<%dI' % (2 * count)), *flatIDs) + struct.pack(('<' + VEH_INTERACTION_DETAILS_LAYOUT * count), *self.__values)
        except Exception as e:
            from debug_utils import LOG_ERROR
            LOG_ERROR('PACKING EXCEPTION', e, str(self))
            packed = ''

        return packed

    def toDict(self):
        return dict([ ((vehID, vehIdx), dict(_VehicleInteractionDetailsItem(self.__values, offset))) for (vehID, vehIdx), offset in self.__offsets.iteritems() ])
