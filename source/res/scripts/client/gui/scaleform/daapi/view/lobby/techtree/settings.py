# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/settings.py
from collections import namedtuple, defaultdict
import nations
from debug_utils import LOG_DEBUG
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from items import getTypeInfoByName
from items.vehicles import VEHICLE_CLASS_TAGS
__all__ = ('NODE_STATE', 'RequestState', 'SelectedNation', 'UnlockProps', 'DEFAULT_UNLOCK_PROPS', 'BpfProps', '_DEFAULT_BPF_PROPS', 'VehicleClassInfo', 'MAX_PATH_LIMIT', 'RESEARCH_ITEMS', 'TREE_SHARED_REL_FILE_PATH', 'NATION_TREE_REL_FILE_PATH')
TREE_SHARED_REL_FILE_PATH = 'gui/flash/techtree/tree-shared.xml'
NATION_TREE_REL_FILE_PATH = 'gui/flash/techtree/{}-tree.xml'
NATION_TREE_REL_PREMIUM_FILE_PATH = 'gui/flash/techtree/{}-premium.xml'
NODE_ORDER_PREFIX_COMMON = 0
NODE_ORDER_PREFIX_PREMIUM = 1
_VEHICLE_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEHICLE]
RESEARCH_ITEMS = (GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.RADIO,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.CHASSIS)
MAX_PATH_LIMIT = 5
UNKNOWN_VEHICLE_LEVEL = -1

class NODE_STATE(object):

    @classmethod
    def add(cls, state, flag):
        if not state & flag:
            state |= flag
            return state

    @classmethod
    def addIfNot(cls, state, flag):
        if not state & flag:
            state |= flag
        return state

    @classmethod
    def remove(cls, state, flag):
        if state & flag > 0:
            state ^= flag
            return state

    @classmethod
    def removeIfHas(cls, state, flag):
        if state & flag > 0:
            state ^= flag
        return state

    @classmethod
    def isNext2Unlock(cls, state):
        return state & NODE_STATE_FLAGS.NEXT_2_UNLOCK > 0

    @classmethod
    def isAvailable2Unlock(cls, state):
        return not state & NODE_STATE_FLAGS.UNLOCKED and state & NODE_STATE_FLAGS.NEXT_2_UNLOCK and state & NODE_STATE_FLAGS.ENOUGH_XP

    @classmethod
    def isUnlocked(cls, state):
        return state & NODE_STATE_FLAGS.UNLOCKED > 0

    @classmethod
    def inInventory(cls, state):
        return state & NODE_STATE_FLAGS.IN_INVENTORY > 0

    @classmethod
    def isVehicleCanBeChanged(cls, state):
        return state & NODE_STATE_FLAGS.VEHICLE_CAN_BE_CHANGED > 0

    @classmethod
    def isInstalled(cls, state):
        return state & NODE_STATE_FLAGS.INSTALLED > 0

    @classmethod
    def isAvailable2Buy(cls, state):
        return (not state & NODE_STATE_FLAGS.IN_INVENTORY or state & NODE_STATE_FLAGS.VEHICLE_IN_RENT) and state & NODE_STATE_FLAGS.UNLOCKED and state & NODE_STATE_FLAGS.ENOUGH_MONEY

    @classmethod
    def isAvailable2Sell(cls, state):
        return state & NODE_STATE_FLAGS.CAN_SELL > 0

    @classmethod
    def isWasInBattle(cls, state):
        return state & NODE_STATE_FLAGS.WAS_IN_BATTLE > 0

    @classmethod
    def isPremium(cls, state):
        return state & NODE_STATE_FLAGS.PREMIUM > 0

    @classmethod
    def isCollectible(cls, state):
        return state & NODE_STATE_FLAGS.COLLECTIBLE > 0

    @classmethod
    def isActionVehicle(cls, state):
        return state & NODE_STATE_FLAGS.ACTION > 0

    @classmethod
    def isCollectibleActionVehicle(cls, state):
        return state & NODE_STATE_FLAGS.COLLECTIBLE_ACTION > 0

    @classmethod
    def isBuyForCredits(cls, state):
        return state & NODE_STATE_FLAGS.UNLOCKED and not state & NODE_STATE_FLAGS.IN_INVENTORY and not state & NODE_STATE_FLAGS.PREMIUM or state & NODE_STATE_FLAGS.RESTORE_AVAILABLE

    @classmethod
    def isBuyForGold(cls, state):
        return state & NODE_STATE_FLAGS.UNLOCKED and (not state & NODE_STATE_FLAGS.IN_INVENTORY or state & NODE_STATE_FLAGS.VEHICLE_IN_RENT) and state & NODE_STATE_FLAGS.PREMIUM

    @classmethod
    def setNext2Unlock(cls, state):
        state &= ~NODE_STATE_FLAGS.LOCKED
        if state & NODE_STATE_FLAGS.UNLOCKED == 0:
            state |= NODE_STATE_FLAGS.NEXT_2_UNLOCK
        return state

    @classmethod
    def change2Unlocked(cls, state):
        if state & NODE_STATE_FLAGS.UNLOCKED > 0:
            return -1
        if state & NODE_STATE_FLAGS.LOCKED > 0:
            state ^= NODE_STATE_FLAGS.LOCKED
        if state & NODE_STATE_FLAGS.NEXT_2_UNLOCK > 0:
            state ^= NODE_STATE_FLAGS.NEXT_2_UNLOCK
            if state & NODE_STATE_FLAGS.ENOUGH_XP > 0:
                state ^= NODE_STATE_FLAGS.ENOUGH_XP
        state |= NODE_STATE_FLAGS.UNLOCKED
        return state

    @classmethod
    def changeLast2Buy(cls, state, isLast2Buy):
        if isLast2Buy:
            state = cls.addIfNot(state, NODE_STATE_FLAGS.LAST_2_BUY)
        else:
            state = cls.removeIfHas(state, NODE_STATE_FLAGS.LAST_2_BUY)
        return state

    @classmethod
    def isRentalOver(cls, state):
        return state & NODE_STATE_FLAGS.VEHICLE_RENTAL_IS_OVER

    @classmethod
    def isRestoreAvailable(cls, state):
        return state & NODE_STATE_FLAGS.RESTORE_AVAILABLE

    @classmethod
    def isRentAvailable(cls, state):
        return state & NODE_STATE_FLAGS.RENT_AVAILABLE

    @classmethod
    def canTradeIn(cls, state):
        return state & NODE_STATE_FLAGS.CAN_TRADE_IN

    @classmethod
    def canTradeOff(cls, state):
        return state & NODE_STATE_FLAGS.CAN_TRADE_OFF

    @classmethod
    def isAnnouncement(cls, state):
        return state & NODE_STATE_FLAGS.ANNOUNCEMENT

    @classmethod
    def hasBlueprints(cls, state):
        return state & NODE_STATE_FLAGS.BLUEPRINT

    @classmethod
    def printStates(cls, state):
        states = []
        for k, v in NODE_STATE_FLAGS.__dict__.iteritems():
            if not k.startswith('_') and state & v:
                states.append(k)

        LOG_DEBUG('Next states are in node state: ', states)


class UnlockStats(namedtuple('UnlockStats', 'unlocked xps freeXP')):

    def isUnlocked(self, nodeCD):
        return nodeCD in self.unlocked

    def isSeqUnlocked(self, seq):
        return seq.issubset(self.unlocked)

    def getVehXP(self, nodeCD):
        result = 0
        if nodeCD in self.xps:
            result = self.xps[nodeCD]
        return result

    def getVehTotalXP(self, nodeCD):
        return self.freeXP + self.getVehXP(nodeCD)


class UnlockProps(namedtuple('UnlockProps', ('parentID', 'unlockIdx', 'xpCost', 'required', 'discount', 'xpFullCost'))):
    __slots__ = ()

    def makeTuple(self):
        return (self.parentID,
         self.unlockIdx,
         self.xpCost,
         list(self.required),
         self.discount,
         self.xpFullCost)


DEFAULT_UNLOCK_PROPS = UnlockProps(0, -1, 0, set(), 0, 0)
BpfProps = namedtuple('BpfProps', ('filledCount', 'totalCount', 'canConvert'))
_DEFAULT_BPF_PROPS = BpfProps(0, 0, False)

class SelectedNation(object):
    __slots__ = ()
    __index = None

    @classmethod
    def byDefault(cls):
        if cls.__index is None:
            from CurrentVehicle import g_currentVehicle
            from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
            index = 0
            if g_currentVehicle.isPresent() and g_currentVehicle.item.nationID in g_techTreeDP.getAvailableNationsIndices():
                index = g_currentVehicle.item.nationID
            cls.__index = index
        return

    @classmethod
    def select(cls, index):
        from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
        if index in g_techTreeDP.getAvailableNationsIndices():
            cls.__index = index

    @classmethod
    def getIndex(cls):
        return cls.__index

    @classmethod
    def getName(cls):
        return nations.NAMES[cls.__index]


class RequestState(object):
    __slots__ = ()
    __states = set()

    @classmethod
    def sent(cls, name):
        cls.__states.add(name)

    @classmethod
    def received(cls, name):
        if name in cls.__states:
            cls.__states.remove(name)

    @classmethod
    def inProcess(cls, name):
        return name in cls.__states


class VehicleClassInfo(object):
    __slots__ = ('__info',)

    def __init__(self):
        super(VehicleClassInfo, self).__init__()
        self.__info = defaultdict(lambda : {'name': ''})
        for tag in VEHICLE_CLASS_TAGS:
            info = getTypeInfoByName(_VEHICLE_TYPE_NAME)['tags'][tag]
            self.__info[frozenset((tag,))] = {'name': info['name']}

    def getInfoByTags(self, tags):
        return self.__info[VEHICLE_CLASS_TAGS & tags]

    def clear(self):
        self.__info.clear()
