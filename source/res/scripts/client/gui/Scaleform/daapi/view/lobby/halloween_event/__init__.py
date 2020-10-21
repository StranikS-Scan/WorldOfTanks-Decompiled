# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/halloween_event/__init__.py
from gui.prb_control.dispatcher import g_prbLoader
from constants import QUEUE_TYPE

def isInEvent():
    prbDispatcher = g_prbLoader.getDispatcher()
    if not prbDispatcher:
        return False
    else:
        entity = prbDispatcher.getEntity()
        return entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES
