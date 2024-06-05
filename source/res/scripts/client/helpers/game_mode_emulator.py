# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/game_mode_emulator.py
import sys
import BigWorld
from SpaceVisibilityFlags import SpaceVisibilityFlagsFactory
from constants import ARENA_GAMEPLAY_IDS
GAME_MODE_ARG = 'gameMode'
DEFAULT_VISIBILITY_MASK = -1
ENVIRONMENT_ARG = 'environment'
DEFAULT_ENVIRONMENT = ''

def gameModeVisibilityMask(spaceName):
    if GAME_MODE_ARG not in sys.argv:
        return DEFAULT_VISIBILITY_MASK
    gameModeArgIndex = sys.argv.index(GAME_MODE_ARG) + 1
    if gameModeArgIndex >= len(sys.argv):
        return DEFAULT_VISIBILITY_MASK
    gameMode = sys.argv[gameModeArgIndex].lower()
    if gameMode not in ARENA_GAMEPLAY_IDS:
        return DEFAULT_VISIBILITY_MASK
    spaceVisibilityFlags = SpaceVisibilityFlagsFactory.create(spaceName)
    return spaceVisibilityFlags.getMaskForGameplayID(gameMode)


def environment():
    if ENVIRONMENT_ARG not in sys.argv:
        return DEFAULT_ENVIRONMENT
    environmentArgIndex = sys.argv.index(ENVIRONMENT_ARG) + 1
    return DEFAULT_ENVIRONMENT if environmentArgIndex >= len(sys.argv) else sys.argv[environmentArgIndex]


def createFakeAvatar():
    entityID = BigWorld.createEntity('OfflineEntity', BigWorld.camera().spaceID, 0, (0, 0, 0), (0, 0, 0), {})
    entity = BigWorld.entity(entityID)
    BigWorld.player = lambda : entity
