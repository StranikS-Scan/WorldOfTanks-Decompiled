# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/formatters.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import getArenaSubTypeName

def getRoundLenString(roundLength):
    return backport.text(R.strings.menu.training.info.timeout.value(), roundLength=roundLength / 60)


def getTrainingRoomTitle(arenaType):
    return backport.text(R.strings.menu.training.info.title(), arenaName=arenaType.name)


def getArenaSubTypeString(arenaTypeID):
    arenaSubTypeName = getArenaSubTypeName(arenaTypeID)
    return backport.text(R.strings.arenas.type.dyn(arenaSubTypeName).name())


def getPlayerStateString(state):
    stateStr = 'state{}'.format(state)
    return backport.text(R.strings.menu.training.info.states.dyn(stateStr)())
