# Embedded file name: scripts/client/messenger/ext/channel_num_gen.py
import BigWorld
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from ids_generators import SequenceIDGenerator
from messenger.m_constants import LAZY_CHANNEL

class PRIMARY_CHANNEL_ORDER(object):
    LAZY = 1
    SYSTEM = 2
    OTHER = 3


_CHANNEL_LAZY_ORDER = {LAZY_CHANNEL.COMMON: 1,
 LAZY_CHANNEL.COMPANIES: 2,
 LAZY_CHANNEL.SPECIAL_BATTLES: 3}
_idGen = SequenceIDGenerator()
_PRB_CLIENT_IDS = dict(((prbType, -(idx + 1)) for idx, prbType in enumerate(PREBATTLE_TYPE.RANGE)))
_LAZY_CLIENT_IDS = dict(((name, -(idx + 1 + 32)) for idx, name in enumerate(LAZY_CHANNEL.ALL)))
_QUEUE_CLIENT_IDS = dict(((name, -(idx + 1 + 64)) for idx, name in enumerate(QUEUE_TYPE.ALL)))

def genOrder4Channel(channel):
    primary = PRIMARY_CHANNEL_ORDER.OTHER
    secondary = BigWorld.time()
    if channel.getName() in LAZY_CHANNEL.ALL:
        primary = PRIMARY_CHANNEL_ORDER.LAZY
    elif channel.isSystem():
        primary = PRIMARY_CHANNEL_ORDER.SYSTEM
    return (primary, secondary)


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


def isClientIDValid(clientID):
    result = False
    if clientID > 0:
        result = True
    elif clientID < 0:
        if clientID in _PRB_CLIENT_IDS.values() or clientID in _LAZY_CLIENT_IDS.values() or clientID in _QUEUE_CLIENT_IDS.values():
            result = True
    return result
