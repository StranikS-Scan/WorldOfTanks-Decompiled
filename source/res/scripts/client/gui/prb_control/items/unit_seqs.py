# Embedded file name: scripts/client/gui/prb_control/items/unit_seqs.py
from messenger.ext import passCensor
from gui.prb_control.items.unit_items import PlayerUnitInfo, UnitFlags
from gui.prb_control.settings import CREATOR_ROSTER_SLOT_INDEXES

def UnitsListIterator(requester, data):
    units = sorted(data.iteritems(), key=lambda item: item[1]['cmdrRating'], reverse=True)
    for cfdUnitID, unitInfo in units:
        item = UnitsListItem(cfdUnitID, **unitInfo)
        requester.addCacheItem(item)
        yield item


def UnitsUpdateIterator(requester, data):
    for cfdUnitID, unitInfo in data.iteritems():
        if unitInfo is None:
            item = None
            requester.removeCacheItem(cfdUnitID)
        else:
            item = requester.getCacheItem(cfdUnitID)
            item.update(**unitInfo)
        yield (cfdUnitID, item)

    return


class UnitsListItem(object):
    __slots__ = ('cfdUnitID', 'unitMgrID', 'creator', 'rating', 'playersCount', 'commandSize', 'vehicles', 'flags', 'isRosterSet', 'peripheryID', 'description', 'isClub', 'extra')

    def __init__(self, cfdUnitID, unitMgrID = 0, cmdrRating = 0, peripheryID = 0, unit = None, **kwargs):
        super(UnitsListItem, self).__init__()
        playersCount = 0
        commandSize = 0
        flags = 0
        isRosterSet = False
        creator = None
        description = None
        isClub = False
        extra = None
        if unit:
            creator = unit.getCreator()
            if creator is not None:
                creator = PlayerUnitInfo(unit.getCreatorDBID(), cfdUnitID, unit, **creator)
            freeSlots = unit.getFreeSlots()
            playersSlots = unit.getPlayerSlots()
            flags = unit.getFlags()
            playersCount = len(playersSlots)
            commandSize = len(playersSlots) + len(freeSlots)
            isRosterSet = unit.isRosterSet(ignored=CREATOR_ROSTER_SLOT_INDEXES)
            description = passCensor(unit.getComment())
            isClub = unit.isClub()
            extra = unit.getExtra()
        self.cfdUnitID = cfdUnitID
        self.unitMgrID = unitMgrID
        self.creator = creator
        self.rating = cmdrRating
        self.peripheryID = peripheryID
        self.playersCount = playersCount
        self.commandSize = commandSize
        self.flags = UnitFlags(flags)
        self.isRosterSet = isRosterSet
        self.description = description
        self.isClub = isClub
        self.extra = extra
        return

    def __repr__(self):
        return 'UnitsListItem(cfdUnitID={0:n}, unitMgrID = {1:n}, creator = {2!r:s}, rating = {3:n}, peripheryID = {4:n}, size = {5:n}/{6:n}, flags = {7!r:s}), description = {8:s}'.format(self.cfdUnitID, self.unitMgrID, self.creator, self.rating, self.peripheryID, self.playersCount, self.commandSize, self.flags, self.description)

    def update(self, cmdrRating = 0, unit = None, **kwargs):
        self.rating = cmdrRating
        if unit:
            creatorDBID = unit.getCreatorDBID()
            if self.creator.dbID != creatorDBID:
                isChanged = True
                data = unit.getCreator()
                if data:
                    self.creator = PlayerUnitInfo(creatorDBID, self.cfdUnitID, unit, **data)
                else:
                    self.creator = None
            self.flags = UnitFlags(unit.getFlags())
            freeSlots = unit.getFreeSlots()
            playersSlots = unit.getPlayerSlots()
            self.playersCount = len(playersSlots)
            self.commandSize = len(playersSlots) + len(freeSlots)
            self.isRosterSet = unit.isRosterSet(ignored=CREATOR_ROSTER_SLOT_INDEXES)
            self.description = passCensor(unit.getComment())
        else:
            self.creator = None
            self.playersCount = 0
            self.commandSize = 0
            self.flags = UnitFlags(0)
            self.isRosterSet = False
            self.description = None
        return
