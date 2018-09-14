# Embedded file name: scripts/client/account_helpers/gameplay_ctx.py
import ArenaType
import constants
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
_ASSAULT2_GP_NAME = constants.ARENA_GAMEPLAY_NAMES[6]
ENABLED_ARENA_GAMEPLAY_NAMES = constants.ARENA_GAMEPLAY_NAMES[:3] + (_ASSAULT2_GP_NAME,)
if constants.IS_DEVELOPMENT:
    ENABLED_ARENA_GAMEPLAY_NAMES += (constants.ARENA_GAMEPLAY_NAMES[13],)

def getDefaultMask():

    def getValue(name):
        return ArenaType.getVisibilityMask(ArenaType.getGameplayIDForName(name))

    return sum(map(getValue, ENABLED_ARENA_GAMEPLAY_NAMES))


def getMask():
    from account_helpers.settings_core.SettingsCore import g_settingsCore
    settingsMask = userMask = g_settingsCore.serverSettings.getGameplaySetting('gameplayMask', getDefaultMask())
    ctfMask = 1 << constants.ARENA_GAMEPLAY_IDS['ctf']
    nationsMask = 1 << constants.ARENA_GAMEPLAY_IDS['nations']
    if not userMask:
        LOG_WARNING('Gameplay is not defined', userMask)
    else:
        if userMask & ctfMask == 0:
            LOG_WARNING('Gameplay "ctf" is not defined', userMask)
        if userMask & nationsMask:
            userMask ^= nationsMask
            LOG_DEBUG('Nations battle mode currently unavailable')
    userMask |= ctfMask
    if settingsMask != userMask:
        _setMask(userMask)
    return userMask


def setMaskByNames(names):
    gameplayNames = {'ctf'}
    for name in names:
        if name in ArenaType.g_gameplayNames:
            gameplayNames.add(name)
        else:
            LOG_ERROR('Gameplay is not available', name)

    gameplayMask = ArenaType.getGameplaysMask(gameplayNames)
    LOG_DEBUG('Set gameplay (names, mask)', gameplayNames, gameplayMask)
    _setMask(gameplayMask)


def isCreationEnabled(gameplayName):
    return gameplayName in ENABLED_ARENA_GAMEPLAY_NAMES


def _setMask(gameplayMask):
    from account_helpers.settings_core.SettingsCore import g_settingsCore
    g_settingsCore.serverSettings.setGameplaySettings({'gameplayMask': gameplayMask})
