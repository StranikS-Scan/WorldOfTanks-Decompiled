# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/settings.py
from collections import namedtuple, defaultdict
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from items import getTypeInfoByName
from items.vehicles import VEHICLE_CLASS_TAGS
import nations
__all__ = ('USE_XML_DUMPING', 'NODE_STATE', 'RequestState', 'SelectedNation', 'UnlockProps', 'makeDefUnlockProps', 'listeners', 'VehicleClassInfo', 'tech_tree_dp', 'dumpers', 'data', 'MAX_PATH_LIMIT', 'RESEARCH_ITEMS', 'TREE_SHARED_REL_FILE_PATH', 'NATION_TREE_REL_FILE_PATH')
TREE_SHARED_REL_FILE_PATH = 'gui/flash/techtree/tree-shared.xml'
NATION_TREE_REL_FILE_PATH = 'gui/flash/techtree/%s-tree.xml'
USE_XML_DUMPING = False
_VEHICLE_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEHICLE]
RESEARCH_ITEMS = (GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.RADIO,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.CHASSIS)
MAX_PATH_LIMIT = 5

class NODE_STATE:
    LOCKED = 1
    NEXT_2_UNLOCK = 2
    UNLOCKED = 4
    ENOUGH_XP = 8
    ENOUGH_MONEY = 16
    IN_INVENTORY = 32
    WAS_IN_BATTLE = 64
    ELITE = 128
    PREMIUM = 256
    SELECTED = 512
    AUTO_UNLOCKED = 1024
    INSTALLED = 2048
    SHOP_ACTION = 4096
    CAN_SELL = 8192
    VEHICLE_CAN_BE_CHANGED = 16384
    VEHICLE_IN_RENT = 32768
    VEHICLE_RENTAL_IS_OVER = 65536

    @classmethod
    def add(cls, state, flag):
        if not state & flag:
            state |= flag
            return state
        return -1

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
        return -1

    @classmethod
    def removeIfHas(cls, state, flag):
        if state & flag > 0:
            state ^= flag
        return state

    @classmethod
    def isAvailable2Unlock(cls, state):
        return not state & cls.UNLOCKED and state & cls.NEXT_2_UNLOCK and state & cls.ENOUGH_XP

    @classmethod
    def isUnlocked(cls, state):
        return state & cls.UNLOCKED > 0

    @classmethod
    def inInventory(cls, state):
        return state & cls.IN_INVENTORY > 0

    @classmethod
    def isVehicleCanBeChanged(cls, state):
        return state & cls.VEHICLE_CAN_BE_CHANGED > 0

    @classmethod
    def isInstalled(cls, state):
        return state & cls.INSTALLED > 0

    @classmethod
    def isAvailable2Buy(cls, state):
        return (not state & cls.IN_INVENTORY or state & cls.VEHICLE_IN_RENT) and state & cls.UNLOCKED and state & cls.ENOUGH_MONEY

    @classmethod
    def isAvailable2Sell(cls, state):
        return state & cls.CAN_SELL > 0

    @classmethod
    def isWasInBattle(cls, state):
        return state & cls.WAS_IN_BATTLE > 0

    @classmethod
    def isPremium(cls, state):
        return state & cls.PREMIUM > 0

    @classmethod
    def isBuyForCredits(cls, state):
        return state & cls.UNLOCKED and not state & cls.IN_INVENTORY and not state & cls.PREMIUM

    @classmethod
    def isBuyForGold(cls, state):
        return state & cls.UNLOCKED and (not state & cls.IN_INVENTORY or state & cls.VEHICLE_IN_RENT) and state & cls.PREMIUM

    @classmethod
    def change2Unlocked(cls, state):
        if state & NODE_STATE.UNLOCKED > 0:
            return -1
        if state & cls.LOCKED > 0:
            state ^= cls.LOCKED
        if state & cls.NEXT_2_UNLOCK > 0:
            state ^= cls.NEXT_2_UNLOCK
            if state & cls.ENOUGH_XP > 0:
                state ^= cls.ENOUGH_XP
        state |= cls.UNLOCKED
        return state

    @classmethod
    def isRentalOver(cls, state):
        return state & cls.VEHICLE_RENTAL_IS_OVER


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


class UnlockProps(namedtuple('UnlockProps', 'parentID unlockIdx xpCost required')):

    def _makeTuple(self):
        return (self.parentID,
         self.unlockIdx,
         self.xpCost,
         list(self.required))


def makeDefUnlockProps():
    return UnlockProps(0, -1, 0, set())


class SelectedNation(object):
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
        self.__info = defaultdict(lambda : {'userString': '',
         'name': ''})
        for tag in VEHICLE_CLASS_TAGS:
            info = getTypeInfoByName(_VEHICLE_TYPE_NAME)['tags'][tag]
            self.__info[frozenset((tag,))] = {'userString': info['userString'],
             'name': info['name']}

    def getInfoByTags(self, tags):
        return self.__info[VEHICLE_CLASS_TAGS & tags]

    def clear(self):
        self.__info.clear()
