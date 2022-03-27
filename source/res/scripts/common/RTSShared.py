# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/RTSShared.py
from collections import namedtuple
from functools import partial
import typing
from enum import Enum, IntEnum
import Math
from debug_utils import LOG_ERROR
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Optional
    from items.vehicles import VehicleType
MAX_ORDERS_QUEUE_SIZE = 10
RTS_GAMEPLAY_NAME = 'rts'
WARMUP_BATTLE_COST_FOR_COMMANDER = 0

class RTSEvent(Enum):
    ON_TARGET_REACHED = 1
    ON_PURSUIT_TARGET = 2
    ON_TARGET_DETECTED = 3
    ON_ORDER_MODIFIED_BY_SERVER = 4
    ON_ORDER_CANCELED_BY_SERVER = 5
    ON_MANNER_MODIFIED_BY_SERVER = 6
    ON_RELOAD = 7
    ON_RELOAD_NON_EMPTY_CLIP = 8
    ON_FIRE_LINE_BLOCKED = 9
    ON_OVERWATCH_MODE_ENABLED = 10
    ON_OVERWATCH_MODE_DISABLED = 11
    ON_TARGET_LOST = 12


class RTSOrder(IntEnum):
    GO_TO_POSITION = 1
    ATTACK_ENEMY = 2
    CAPTURE_THE_BASE = 3
    DEFEND_THE_BASE = 4
    FORCE_GO_TO_POSITION = 5
    FORCE_ATTACK_ENEMY = 6
    RETREAT = 7
    STOP = 8


FORCED_ORDERS = (RTSOrder.FORCE_ATTACK_ENEMY, RTSOrder.FORCE_GO_TO_POSITION, RTSOrder.STOP)
MOVEMENT_ORDERS = (RTSOrder.GO_TO_POSITION, RTSOrder.FORCE_GO_TO_POSITION, RTSOrder.RETREAT)
ORDERS_WITH_TARGET_POS = MOVEMENT_ORDERS + (RTSOrder.STOP,)
ORDERS_WITH_TARGET_VEHICLE = (RTSOrder.ATTACK_ENEMY, RTSOrder.FORCE_ATTACK_ENEMY)

class RTSQuery(Enum):
    POSITION_ON_NAV_MESH = 1


class RTSQueryResultCode(Enum):
    OK = 1
    FAILED = 2
    MODIFIED = 3
    CANCELED = 4
    TIMEOUT = 5


class RTSCommandResult(Enum):
    NONE = 0
    SUCCESS = 1
    FAILED = 2
    ABORTED = 3


class RTSQueryResult(object):

    def __init__(self, queryID, queryType, vehicleID, resultCode, position):
        self.queryID = queryID
        self.queryType = queryType
        self.vehicleID = vehicleID
        self.resultCode = resultCode
        self.position = position


class RTSManner(object):
    SCOUT = 1
    DEFENSIVE = 2
    HOLD = 3
    ALL = (DEFENSIVE, SCOUT, HOLD)
    DEFAULT = DEFENSIVE

    @classmethod
    def getMannerName(cls, mannerID):
        return [ name for name, value in cls.__dict__.iteritems() if value == mannerID ][0]


class RTSSupply(object):
    BARRICADES = 1
    BUNKER = 2
    AT_GUN = 3
    PILLBOX = 4
    WATCH_TOWER = 5
    MORTAR = 6
    FLAMER = 7
    ALL = (BARRICADES,
     BUNKER,
     AT_GUN,
     WATCH_TOWER,
     PILLBOX,
     MORTAR,
     FLAMER)
    TAG_TO_SUPPLY = {'supply_Barricades': BARRICADES,
     'supply_Bunker': BUNKER,
     'supply_ATgun': AT_GUN,
     'supply_WatchTower': WATCH_TOWER,
     'supply_Pillbox': PILLBOX,
     'supply_Mortar': MORTAR,
     'supply_Flamer': FLAMER}
    SUPPLY_ID_TO_TAG = dict(((supplyID, classTag) for classTag, supplyID in TAG_TO_SUPPLY.iteritems()))
    SUPPLY_TAG_LIST = frozenset(TAG_TO_SUPPLY.keys())

    @classmethod
    def getID(cls, vehicleType):
        for tag in vehicleType.tags:
            supplyID = cls.TAG_TO_SUPPLY.get(tag)
            if supplyID is not None and supplyID in cls.ALL:
                return supplyID

        return

    @classmethod
    def getSupplyTag(cls, vehicleType):
        for tag in vehicleType.tags:
            supplyID = cls.TAG_TO_SUPPLY.get(tag)
            if supplyID is not None and supplyID in cls.ALL:
                return tag

        return

    @classmethod
    def isBarricades(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.BARRICADES] in tags

    @classmethod
    def isBunker(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.BUNKER] in tags

    @classmethod
    def isATGun(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.AT_GUN] in tags

    @classmethod
    def isWatchTower(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.WATCH_TOWER] in tags

    @classmethod
    def isPillbox(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.PILLBOX] in tags

    @classmethod
    def isMortar(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.MORTAR] in tags

    @classmethod
    def isFlamer(cls, tags):
        return cls.SUPPLY_ID_TO_TAG[cls.FLAMER] in tags

    @classmethod
    def isWithoutRamming(cls, tags):
        return 'supply_WithoutRamming' in tags

    @classmethod
    def isWithoutSelfRamming(cls, tags):
        return 'supply_WithoutSelfRamming' in tags

    @classmethod
    def isSupply(cls, vehicleType):
        return 'supply' in vehicleType.tags

    @classmethod
    def isStructure(cls, vehicleType):
        return 'supply_structure' in vehicleType.tags

    @classmethod
    def isNoCollisionWhenDestroyed(cls, vehicleType):
        return 'noCollisionWhenDestroyed' in vehicleType.tags

    @classmethod
    def isDestructibleSupply(cls, vehicleType):
        return 'isDestructibleSupply' in vehicleType.tags

    @classmethod
    def isStationary(cls, vehicleType):
        return 'stationary' in vehicleType.tags

    @classmethod
    def isVisibleToWatchTower(cls, vehicleType):
        return 'visibleToWatchTower' in vehicleType.tags


class RTSBootcampMatchmakerState(IntEnum):
    DISABLED = 0
    DISABLED_TEMPORARY = 1
    ENABLED = 2


_OrderDataTuple = namedtuple('OrderData', ['order',
 'manner',
 'position',
 'isPositionModified',
 'target',
 'heading',
 'baseID',
 'baseTeam',
 'companions'])
_PackerTuple = namedtuple('PackerTuple', ['pack', 'unpack'])

def _commonEquals(a, b):
    return a == b


def _packAbstract(value, stub, dbgFuncName, funcEquals=_commonEquals):
    if value is None:
        return stub
    else:
        if funcEquals(value, stub):
            LOG_ERROR('Logic error using OrderData.%s: given %s will be packed as None' % (dbgFuncName, stub))
        return value


def _unpackAbstract(value, stub, dbgFuncName, funcEquals=_commonEquals):
    if funcEquals(value, stub):
        return
    else:
        if value is None:
            LOG_ERROR('Logic error using OrderData.%s: None given' % dbgFuncName)
        return value


def _makeSimplePacker(stub, dbgAffix, funcEquals=_commonEquals):
    pack = partial(_packAbstract, stub=stub, dbgFuncName='__pack%s' % dbgAffix, funcEquals=funcEquals)
    unpack = partial(_unpackAbstract, stub=stub, dbgFuncName='__unpack%s' % dbgAffix, funcEquals=funcEquals)
    return _PackerTuple(pack=pack, unpack=unpack)


_STUB_INT = -1
_packerInt = _makeSimplePacker(_STUB_INT, 'Int')
_STUB_LIST = []
_packerList = _makeSimplePacker(_STUB_LIST, 'List')

def _vectorEquals(a, b):
    return a.distSqrTo(b) < 0.01


_STUB_VECTOR = Math.Vector3(1001.0, 1002.0, 1003.0)
packerVector = _makeSimplePacker(_STUB_VECTOR, 'Vector')

def _packBool(value):
    return _packerInt.pack(None if value is None else int(value), dbgFuncName='_packBool')


def _unpackBool(value):
    intValue = _packerInt.unpack(value, dbgFuncName='_unpackBool')
    return None if intValue is None else bool(intValue)


_packerBool = _PackerTuple(pack=_packBool, unpack=_unpackBool)

def _packOrder(value):
    return _packerInt.pack(None if value is None else value.value, dbgFuncName='_packBool')


def _unpackOrder(value):
    intValue = _packerInt.unpack(value, dbgFuncName='_unpackOrder')
    try:
        return RTSOrder(intValue)
    except ValueError:
        return None

    return None


_packerOrder = _PackerTuple(pack=_packOrder, unpack=_unpackOrder)
_PACKERS = _OrderDataTuple(order=_packerOrder, manner=_packerInt, position=packerVector, isPositionModified=_packerBool, target=_packerInt, heading=packerVector, baseID=_packerInt, baseTeam=_packerInt, companions=_packerList)

class OrderDataPacked(_OrderDataTuple):
    pass


class OrderData(_OrderDataTuple):

    class InvalidOrderData(SoftException):

        def __init__(self, fieldName, valueGiven, valueExpected):
            log = 'OrderData type check failure: %s = %s (expected %s)' % (fieldName, valueGiven, valueExpected)
            super(OrderData.InvalidOrderData, self).__init__(log)

    def pack(self):
        packedFields = {}
        for fieldName in _OrderDataTuple._fields:
            fieldValue = getattr(self, fieldName)
            packer = getattr(_PACKERS, fieldName)
            packedFields[fieldName] = packer.pack(fieldValue)

        return OrderDataPacked(**packedFields)

    @staticmethod
    def unpack(packed):
        unpackedFields = {}
        for fieldName in _OrderDataTuple._fields:
            fieldValue = getattr(packed, fieldName)
            packer = getattr(_PACKERS, fieldName)
            unpackedFields[fieldName] = packer.unpack(fieldValue)

        return OrderData(**unpackedFields)

    def checkFields(self):
        order = self.order
        manner = self.manner
        if order is not None and order not in RTSOrder:
            raise OrderData.InvalidOrderData('order', order, RTSOrder)
        if manner is not None and manner not in RTSManner.ALL:
            raise OrderData.InvalidOrderData('manner', manner, RTSManner.ALL)
        return

    @property
    def headingNorm(self):
        heading = self.heading
        return heading and heading / heading.length


OrderData.__new__.func_defaults = (None,) * len(OrderData._fields)

class COMMAND_NAME(object):
    ATTACK = 'attack'
    MOVE = 'move'
    PURSUIT = 'chasingTarget'
    ORIENTATE = 'orientate'
    SQUAD = 'squad'
    RETREAT = 'retreat'


class RTSCommandQueuePosition(Enum):
    PREVIEW = -1
    SINGLE = 1
    CURRENT = 2
    NEXT = 3
    LAST = 4


DEFAULT_GROUP_ID = -1

class AnyVehicleCommanderData(object):
    __slots__ = ('vehicleID', 'commanderVehicleID')

    def __init__(self, vehicleID=0, commanderVehicleID=0):
        super(AnyVehicleCommanderData, self).__init__()
        self.vehicleID = vehicleID
        self.commanderVehicleID = commanderVehicleID

    def __iter__(self):
        return self._getSlots()

    def __repr__(self):
        return '{className}({slotsData})'.format(className=self.__class__.__name__, slotsData=', '.join(('{slotName}={slotValue}'.format(slotName=slotName, slotValue=getattr(self, slotName, None)) for slotName in self)))

    @property
    def isOwn(self):
        return False

    def _getSlots(self):
        for slotName in self.__slots__:
            yield slotName

    @property
    def asTuple(self):
        return tuple([ getattr(self, slot, None) for slot in self._getSlots() ])


class OwnVehicleCommanderData(AnyVehicleCommanderData):
    __slots__ = ('health', 'maxHealth', 'orderData', 'currentPath', 'isSpeedLinked', 'wasSpotted', 'groupID')

    def __init__(self, vehicleID=0, commanderVehicleID=0, health=0, maxHealth=0, orderData=None, currentPath=None, isSpeedLinked=False, wasSpotted=False, groupID=DEFAULT_GROUP_ID):
        super(OwnVehicleCommanderData, self).__init__(vehicleID, commanderVehicleID)
        self.health = health
        self.maxHealth = maxHealth
        self.orderData = orderData
        self.currentPath = currentPath
        self.isSpeedLinked = isSpeedLinked
        self.wasSpotted = wasSpotted
        self.groupID = groupID

    @property
    def isOwn(self):
        return True

    def _getSlots(self):
        for slotName in super(OwnVehicleCommanderData, self).__slots__ + self.__slots__:
            yield slotName


def createVehicleCommanderDataFromTuple(vehicleCommanderData):
    if not isinstance(vehicleCommanderData, tuple):
        raise SoftException("Unexpected type '{}' of vehicleCommanderData! 'tuple' expected.".format(type(vehicleCommanderData).__name__))
    size = len(vehicleCommanderData)
    if size == 2:
        return AnyVehicleCommanderData(vehicleCommanderData[0], vehicleCommanderData[1])
    elif size == 9:
        orderData = vehicleCommanderData[4]
        if orderData is not None:
            orderData = OrderData.unpack(OrderDataPacked(order=orderData['order'], manner=orderData['manner'], position=orderData['position'], isPositionModified=orderData['isPositionModified'], target=orderData['target'], heading=orderData['heading'], baseID=orderData['baseID'], baseTeam=orderData['baseTeam'], companions=orderData['companions']))
            orderData.checkFields()
        return OwnVehicleCommanderData(vehicleCommanderData[0], vehicleCommanderData[1], vehicleCommanderData[2], vehicleCommanderData[3], orderData, vehicleCommanderData[5], vehicleCommanderData[6], vehicleCommanderData[7], vehicleCommanderData[8])
    else:
        raise SoftException('Unexpected size {} of vehicleCommanderData tuple {}! 2 or 9 expected.'.format(size, vehicleCommanderData))
        return


def getMannerOrDefault(commanderData):
    if commanderData is not None:
        orderData = commanderData.orderData
        if orderData is not None:
            return orderData.manner
    return RTSManner.DEFAULT


class RtsStats(object):
    PDATA_KEY = 'rtsStatistics'
    RTS_STRATEGIST_1x7 = 'rts_1x7'
    RTS_STRATEGIST_1x1 = 'rts_1x1'
    RTS_TANKIST = 'tankist'
    ACTIVE_ARENAS = 'activeArenas'
    NUM_BATTLES = 'numBattles'
    NUM_WINS = 'wins'
    NUM_DESTROYED_SUPPLIES = 'killedSupplies'
    NUM_DESTROYED_TANKS = 'killedTanks'
    NUM_DESTROYED_TANKS_BY_SUPPLY = 'killedBySupply'
    AVERAGE_DAMAGE = 'avgDamage'
    AVERAGE_ACTIONS_PER_MINUTE = 'avgAPM'
    PEAK_ACTIONS_PER_MINUTE = 'peakAPM'
    LEADER_POINTS = 'rtsLeaderPoints'
    XP = 'xp'
