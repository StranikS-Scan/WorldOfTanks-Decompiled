# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/items/prb_seqs.py
import time
from constants import PREBATTLE_CACHE_KEY
from constants import PREBATTLE_TYPE
from gui.prb_control.prb_getters import getPrebattleAutoInvites
from gui.prb_control.items.prb_items import PlayerPrbInfo
from gui.prb_control.prb_helpers import BadgesHelper
from helpers.time_utils import makeLocalServerTime
from messenger.ext import passCensor

def PrbListIterator(prebattles):
    for t, prbID, info in prebattles:
        yield PrbListItem(t, prbID, info)


def RosterIterator(roster_data):
    for pID, name, dbID, roster, state, t, vehCompDescr, igrType, clanDBID, clanAbbrev in roster_data:
        yield PlayerPrbInfo(pID, name=name, dbID=dbID, state=state, time=t, vehCompDescr=vehCompDescr, igrType=igrType, clanDBID=clanDBID, clanAbbrev=clanAbbrev, roster=roster)


def AutoInvitesIterator():
    autoInvites = getPrebattleAutoInvites().items()

    def comparator(obj, other):
        return cmp(obj[1].get('startTime', time.time()), other[1].get('startTime', time.time()))

    autoInvites.sort(comparator)
    for prbID, info in autoInvites:
        yield AutoInviteItem(prbID, **info)


class PrbListItem(object):
    __slots__ = ('prbID', 'time', 'arenaTypeID', 'creator', 'clanAbbrev', 'playersCount', 'isOpened', 'comment', 'creatorIgrType', 'creatorDbId', 'badges')

    def __init__(self, t, prbID, info):
        super(PrbListItem, self).__init__()
        self.prbID = prbID
        self.time = t
        self.arenaTypeID = 0
        if PREBATTLE_CACHE_KEY.ARENA_TYPE_ID in info:
            self.arenaTypeID = info[PREBATTLE_CACHE_KEY.ARENA_TYPE_ID]
        self.creator = ''
        if PREBATTLE_CACHE_KEY.CREATOR in info:
            self.creator = info[PREBATTLE_CACHE_KEY.CREATOR]
        self.clanAbbrev = ''
        if PREBATTLE_CACHE_KEY.CREATOR_CLAN_ABBREV in info:
            self.clanAbbrev = info[PREBATTLE_CACHE_KEY.CREATOR_CLAN_ABBREV]
        self.playersCount = 0
        if PREBATTLE_CACHE_KEY.PLAYER_COUNT in info:
            self.playersCount = info[PREBATTLE_CACHE_KEY.PLAYER_COUNT]
        self.isOpened = True
        if PREBATTLE_CACHE_KEY.IS_OPENED in info:
            self.isOpened = info[PREBATTLE_CACHE_KEY.IS_OPENED]
        self.comment = ''
        if PREBATTLE_CACHE_KEY.COMMENT in info:
            self.comment = info[PREBATTLE_CACHE_KEY.COMMENT]
        self.creatorIgrType = 0
        if PREBATTLE_CACHE_KEY.CREATOR_IGR_TYPE in info:
            self.creatorIgrType = info[PREBATTLE_CACHE_KEY.CREATOR_IGR_TYPE]
        self.creatorDbId = 0
        if PREBATTLE_CACHE_KEY.CREATOR_DB_ID in info:
            self.creatorDbId = info[PREBATTLE_CACHE_KEY.CREATOR_DB_ID]
        creatorBadges = []
        if PREBATTLE_CACHE_KEY.CREATOR_BADGES in info:
            creatorBadges = info[PREBATTLE_CACHE_KEY.CREATOR_BADGES]
        self.badges = BadgesHelper(creatorBadges)

    def __repr__(self):
        return 'PrbListItem(prbID = {0:n}, arenaTypeID = {1:n}, creator = {2:>s}, playersCount = {3:n}, isOpened = {4!r:s}, time = {5:n}, creatorIgrType = {6:n}, creatorDbId = {7:n})'.format(self.prbID, self.arenaTypeID, self.getCreatorFullName(), self.playersCount, self.isOpened, self.time, self.creatorIgrType, self.creatorDbId)

    def getCreatorFullName(self):
        if self.clanAbbrev:
            fullName = '{0:>s}[{1:>s}]'.format(self.creator, self.clanAbbrev)
        else:
            fullName = self.creator
        return fullName

    def getCensoredComment(self):
        return passCensor(self.comment) if self.comment else ''

    def getBadgeID(self):
        return self.badges.getBadgeID()

    def getBadgeImgStr(self, size=24, vspace=-6):
        return self.badges.getBadgeImgStr(size, vspace)


class AutoInviteItem(object):
    __slots__ = ('prbID', 'peripheryID', 'description', 'startTime', 'isValid', 'prbType')

    def __init__(self, prbID, type=PREBATTLE_TYPE.CLAN, peripheryID=0, description=None, startTime=0, isValid=True):
        super(AutoInviteItem, self).__init__()
        self.prbID = prbID
        self.peripheryID = peripheryID
        self.prbType = type
        if description:
            self.description = description
        else:
            self.description = {}
        if startTime > 0:
            self.startTime = makeLocalServerTime(startTime)
        else:
            self.startTime = time.time()
        self.isValid = isValid

    def __repr__(self):
        return 'AutoInviteItem(prbID = {0:n}, peripheryID = {1:n}, type = {2:n} description = {3!r:s}, startTime = {4:n}, isValid = {5!r:s})'.format(self.prbID, self.prbType, self.peripheryID, self.description, self.startTime, self.isValid)
