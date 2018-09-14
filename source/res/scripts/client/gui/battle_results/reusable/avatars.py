# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/avatars.py
from gui.battle_results.reusable import shared

class AvatarInfo(shared.ItemInfo):
    """Information about each avatar which took part in a battle."""
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
        """Total number of damaged vehicles by avatar and all vehicles."""
        return self.__totalDamaged

    @property
    def avatarKills(self):
        """Number of enemies kills by avatar."""
        return self.__avatarKills

    @property
    def avatarDamaged(self):
        """Number of damaged vehicle by avatar."""
        return self.__avatarDamaged

    @property
    def avatarDamageDealt(self):
        """Damage dealt to enemies."""
        return self.__avatarDamageDealt

    def hasPenalties(self):
        """Has specified avatar penalties"""
        return self.__fairplayViolations.hasPenalties()

    @property
    def accRank(self):
        """Return just a rank value without a step. If new rank has been just received"""
        return self.__accRank[0] if self.__accRank else 0

    @property
    def prevAccRank(self):
        """Account rank before battle. Return just a rank value without a step."""
        return self.__prevAccRank[0] if self.__prevAccRank else 0

    @property
    def badge(self):
        """Currently selected user badge."""
        return self.__badge


class AvatarsInfo(shared.UnpackedInfo):
    """Class contains reusable information about avatars.
    This information is fetched from battle_results['avatars']"""
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
        """Gets avatar information by specified accounts's database ID.
        :param dbID: long containing accounts's database ID.
        :return: instance of AvatarInfo.
        """
        if dbID in self.__avatars:
            info = self.__avatars[dbID]
        else:
            self.__avatars[dbID] = info = AvatarInfo(wasInBattle=False)
        return info
