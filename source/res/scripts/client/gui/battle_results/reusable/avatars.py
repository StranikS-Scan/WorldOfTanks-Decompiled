# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/avatars.py
from gui.battle_results.reusable import shared

class AvatarInfo(shared.ItemInfo):
    __slots__ = ('__totalDamaged', '__avatarKills', '__avatarDamaged', '__avatarDamageDealt', '__badge', '__fairplayViolations', '__accRank', '__prevAccRank', '__weakref__')

    def __init__(self, totalDamaged=0, avatarKills=0, avatarDamaged=0, avatarDamageDealt=0, fairplayViolations=None, wasInBattle=True, accRank=None, prevAccRank=None, rankedBadge=0, **kwargs):
        super(AvatarInfo, self).__init__(wasInBattle=wasInBattle)
        self.__totalDamaged = totalDamaged
        self.__avatarKills = avatarKills
        self.__avatarDamaged = avatarDamaged
        self.__avatarDamageDealt = avatarDamageDealt
        self.__fairplayViolations = shared.FairplayViolationsInfo(*(fairplayViolations or ()))
        self.__accRank = accRank
        self.__prevAccRank = prevAccRank
        self.__badge = rankedBadge

    @property
    def totalDamaged(self):
        return self.__totalDamaged

    @property
    def avatarKills(self):
        return self.__avatarKills

    @property
    def avatarDamaged(self):
        return self.__avatarDamaged

    @property
    def avatarDamageDealt(self):
        return self.__avatarDamageDealt

    def hasPenalties(self):
        return self.__fairplayViolations.hasPenalties()

    @property
    def accRank(self):
        return self.__accRank[0] if self.__accRank else 0

    @property
    def prevAccRank(self):
        return self.__prevAccRank[0] if self.__prevAccRank else 0

    @property
    def badge(self):
        return self.__badge


class AvatarsInfo(shared.UnpackedInfo):
    __slots__ = ('__avatars',)

    def __init__(self, avatars):
        super(AvatarsInfo, self).__init__()

        def _convert(item):
            dbID, data = item
            if data is None:
                self._addUnpackedItemID(dbID)
                data = {}
            return (dbID, AvatarInfo(**data))

        self.__avatars = dict(map(_convert, avatars.iteritems()))

    def getAvatarInfo(self, dbID):
        if dbID in self.__avatars:
            info = self.__avatars[dbID]
        else:
            self.__avatars[dbID] = info = AvatarInfo(wasInBattle=False)
        return info
