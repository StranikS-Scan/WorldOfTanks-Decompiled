# Embedded file name: scripts/client/account_helpers/gameplay_ctx.py
import ArenaType
import constants
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
ENABLED_ARENA_GAMEPLAY_NAMES = constants.ARENA_GAMEPLAY_NAMES[0:4]

def getDefaultMask():

    def getValue(name):
        return ArenaType.getVisibilityMask(ArenaType.getGameplayIDForName(name))

    return sum(map(getValue, ENABLED_ARENA_GAMEPLAY_NAMES))


def getMask():
    from account_helpers.settings_core.SettingsCore import g_settingsCore
    mask = g_settingsCore.serverSettings.getGameplaySetting('gameplayMask', getDefaultMask())
    ctfMask = 1 << constants.ARENA_GAMEPLAY_IDS['ctf']
    nationsMask = 1 << constants.ARENA_GAMEPLAY_IDS['nations']
    if not mask:
        LOG_WARNING('Gameplay is not defined', mask)
    else:
        if mask & ctfMask == 0:
            LOG_WARNING('Gameplay "ctf" is not defined', mask)
        if mask & nationsMask:
            mask ^= nationsMask
            LOG_DEBUG('Nations battle mode currently unavailable')
    mask |= ctfMask
    return mask


def setMaskByNames(names):
    gameplayNames = {'ctf'}
    for name in names:
        if name in ArenaType.g_gameplayNames:
            gameplayNames.add(name)
        else:
            LOG_ERROR('Gameplay is not available', name)

    gameplayMask = ArenaType.getGameplaysMask(gameplayNames)
    LOG_DEBUG('Set gameplay (names, mask)', gameplayNames, gameplayMask)
    from account_helpers.settings_core.SettingsCore import g_settingsCore
    g_settingsCore.serverSettings.setGameplaySettings({'gameplayMask': gameplayMask})


def isCreationEnabled(gameplayName):
    return gameplayName in ENABLED_ARENA_GAMEPLAY_NAMES and gameplayName != 'nations'
