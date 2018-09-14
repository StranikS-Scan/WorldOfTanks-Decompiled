# Embedded file name: scripts/client/messenger/ext/channel_num_gen.py
import BigWorld
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from shared_utils import CONST_CONTAINER
from ids_generators import SequenceIDGenerator
from messenger.m_constants import LAZY_CHANNEL, BATTLE_CHANNEL, PRIMARY_CHANNEL_ORDER
_CHANNEL_LAZY_ORDER = {LAZY_CHANNEL.COMMON: 1,
 LAZY_CHANNEL.COMPANIES: 2,
 LAZY_CHANNEL.SPECIAL_BATTLES: 3}

class SPECIAL_CLIENT_WINDOWS(CONST_CONTAINER):
    TRAINING_LIST = 1
    TRAINING_ROOM = 2
    CLUB_CHAT = 3


_idGen = SequenceIDGenerator()
_PRB_CLIENT_IDS = {}
_PRB_CLIENT_COMBINED_IDS = {PREBATTLE_TYPE.SORTIE: PREBATTLE_TYPE.UNIT,
 PREBATTLE_TYPE.FORT_BATTLE: PREBATTLE_TYPE.UNIT,
 PREBATTLE_TYPE.CLUBS: PREBATTLE_TYPE.UNIT,
 PREBATTLE_TYPE.SQUAD: PREBATTLE_TYPE.UNIT}
for idx, prbType in enumerate(PREBATTLE_TYPE.RANGE):
    index = idx
    if prbType in _PRB_CLIENT_COMBINED_IDS:
        index = PREBATTLE_TYPE.RANGE.index(_PRB_CLIENT_COMBINED_IDS[prbType])
    _PRB_CLIENT_IDS[prbType] = -(index + 1)

_LAZY_CLIENT_IDS = dict(((name, -(idx + 1 + 32)) for idx, name in enumerate(LAZY_CHANNEL.ALL)))
_QUEUE_CLIENT_IDS = dict(((name, -(idx + 1 + 64)) for idx, name in enumerate(QUEUE_TYPE.ALL)))
_BATTLE_CLIENT_IDS = dict(((item.name, -(idx + 1 + 128)) for idx, item in enumerate(BATTLE_CHANNEL.REQUIRED)))
_SPECIAL_CLIENT_IDS = dict(((name, -(idx + 1 + 256)) for idx, name in enumerate(SPECIAL_CLIENT_WINDOWS.ALL())))

def genOrder4Channel(channel):
    return (channel.getPrimaryOrder(), BigWorld.time())


def getOrder4Prebattle():
    return (PRIMARY_CHANNEL_ORDER.SYSTEM, BigWorld.time())


def getOrder4LazyChannel(name):
    if name in _CHANNEL_LAZY_ORDER:
        result = (PRIMARY_CHANNEL_ORDER.LAZY, _CHANNEL_LAZY_ORDER[name])
    else:
        result = (PRIMARY_CHANNEL_ORDER.LAZY, BigWorld.time())
    return result


def genClientID4Channel(channel):
    prbType = channel.getPrebattleType()
    name = channel.getName()
    if prbType in _PRB_CLIENT_IDS:
        clientID = _PRB_CLIENT_IDS[prbType]
    elif name in _LAZY_CLIENT_IDS:
        clientID = _LAZY_CLIENT_IDS[name]
    elif name in _BATTLE_CLIENT_IDS:
        clientID = _BATTLE_CLIENT_IDS[name]
    else:
        clientID = _idGen.next()
    return clientID


def getClientID4Prebattle(prbType):
    result = 0
    if prbType in _PRB_CLIENT_IDS:
        result = _PRB_CLIENT_IDS[prbType]
    return result


def getClientID4PreQueue(queueType):
    result = 0
    if queueType in _QUEUE_CLIENT_IDS:
        result = _QUEUE_CLIENT_IDS[queueType]
    return result


def getClientID4LazyChannel(name):
    result = 0
    if name in _LAZY_CLIENT_IDS:
        result = _LAZY_CLIENT_IDS[name]
    return result


def getClientID4SpecialWindow(name):
    result = 0
    if name in _SPECIAL_CLIENT_IDS:
        result = _SPECIAL_CLIENT_IDS[name]
    return result


def getClientID4BattleChannel(name):
    result = 0
    if name in _BATTLE_CLIENT_IDS:
        result = _BATTLE_CLIENT_IDS[name]
    return result


def isClientIDValid(clientID):
    result = False
    if clientID > 0:
        result = True
    elif clientID < 0:
        if clientID in _PRB_CLIENT_IDS.values() or clientID in _LAZY_CLIENT_IDS.values() or clientID in _QUEUE_CLIENT_IDS.values() or clientID in _SPECIAL_CLIENT_IDS.values() or clientID in _BATTLE_CLIENT_IDS.values():
            result = True
    return result
