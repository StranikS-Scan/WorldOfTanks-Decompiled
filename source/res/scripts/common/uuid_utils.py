# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/uuid_utils.py
import os
import random
from uuid import uuid1, UUID
_node = None

def _getNode():
    global _node
    if _node is not None:
        return _node
    else:
        _node = random.randrange(0, 4294967296L) << 16
        _node = _node | os.getpid() & 65535
        _node = _node | 1099511627776L
        return _node


def genUUID():
    return uuid1(_getNode())


def utcTimeFromUUID1(u):
    u = UUID(u)
    return (u.time - 122192928000000000L) * 100 / 1000000000.0
