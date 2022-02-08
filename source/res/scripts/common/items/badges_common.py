# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/badges_common.py
import struct
from typing import TYPE_CHECKING, List, Tuple, Any
import battle_pass_common
if TYPE_CHECKING:
    from BaseAccount import BaseAccount
ExtraInfo = List[Any]
BadgesInfo = Tuple[List[int], ExtraInfo]

class BadgesCommon(object):
    _BADGE_IDS_LEN_FORMAT = '<B'
    _BADGE_IDS = '<{}I'
    _BADGES_EXTRA_INFO = '<I'

    @staticmethod
    def getExtraInfo(account):
        battlePassLevel = 0
        extraInfo = [battlePassLevel]
        return extraInfo

    @staticmethod
    def selectedBadgesEmpty():
        return ([], [])

    @staticmethod
    def packPlayerBadges(badgesInfo):
        badgeIDs, extraInfo = badgesInfo
        badgesLen, extraInfoLen = len(badgeIDs), len(extraInfo)
        packed = BadgesCommon._packLen(badgesLen)
        if badgesLen:
            packed += struct.pack(BadgesCommon._getBadgeIDsFormat(badgesLen), *badgeIDs)
        packed += BadgesCommon._packLen(extraInfoLen)
        if extraInfoLen:
            packed += struct.pack(BadgesCommon._BADGES_EXTRA_INFO, *extraInfo)
        return packed

    @staticmethod
    def unpackPlayerBadges(packedData, initialOffset):
        offset = initialOffset
        badgeIDsLen, offset = BadgesCommon._unpackLen(packedData, offset)
        if badgeIDsLen:
            fmt = BadgesCommon._getBadgeIDsFormat(badgeIDsLen)
            badgeIDs = list(struct.unpack_from(fmt, packedData, offset))
            offset += struct.calcsize(fmt)
        else:
            badgeIDs = list()
        extraInfoLen, offset = BadgesCommon._unpackLen(packedData, offset)
        if extraInfoLen:
            extraInfo = list(struct.unpack_from(BadgesCommon._BADGES_EXTRA_INFO, packedData, offset))
            offset += struct.calcsize(BadgesCommon._BADGES_EXTRA_INFO)
        else:
            extraInfo = list()
        return ((badgeIDs, extraInfo), offset - initialOffset)

    @staticmethod
    def _getBadgeIDsFormat(badgesLen):
        return BadgesCommon._BADGE_IDS.format(badgesLen)

    @staticmethod
    def _packLen(lenValue):
        return struct.pack(BadgesCommon._BADGE_IDS_LEN_FORMAT, lenValue)

    @staticmethod
    def _unpackLen(packedData, offset):
        lenValue = struct.unpack_from(BadgesCommon._BADGE_IDS_LEN_FORMAT, packedData, offset)[0]
        newOffset = offset + struct.calcsize(BadgesCommon._BADGE_IDS_LEN_FORMAT)
        return (lenValue, newOffset)
