# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/tankman_flags.py


class TankmanFlags(object):
    __slots__ = ('_len', 'extendedVehicleTypeID', 'isPremium', 'isFemale', 'hasFreeSkills')
    EXTENDED_VEHICLE_TYPE_ID_FLAG = 128
    IS_PREMIUM_FLAG = 64
    IS_FEMALE_FLAG = 32
    HAS_FREE_SKILLS_FLAG = 16
    MORE_FLAGS_FLAG = 1

    def __init__(self):
        self._len = 0
        self.extendedVehicleTypeID = False
        self.isPremium = False
        self.isFemale = False
        self.hasFreeSkills = False

    @classmethod
    def fromCD(cls, compactDescriptor):
        cd = compactDescriptor
        f = TankmanFlags()
        f._len = 1
        byte = ord(cd[0])
        f.extendedVehicleTypeID = bool(byte & f.EXTENDED_VEHICLE_TYPE_ID_FLAG)
        f.isPremium = bool(byte & f.IS_PREMIUM_FLAG)
        f.isFemale = bool(byte & f.IS_FEMALE_FLAG)
        f.hasFreeSkills = bool(byte & f.HAS_FREE_SKILLS_FLAG)
        while byte & f.MORE_FLAGS_FLAG:
            f._len += 1
            cd = cd[1:]
            byte = ord(cd[0])

        return f

    def pack(self):
        v = self.EXTENDED_VEHICLE_TYPE_ID_FLAG if self.extendedVehicleTypeID else 0
        v += self.IS_PREMIUM_FLAG if self.isPremium else 0
        v += self.IS_FEMALE_FLAG if self.isFemale else 0
        v += self.HAS_FREE_SKILLS_FLAG if self.hasFreeSkills else 0
        return chr(v)

    @property
    def len(self):
        return self._len
