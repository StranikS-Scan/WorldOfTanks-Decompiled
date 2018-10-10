# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/gameplay_ctx.py
import ArenaType
import constants
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_ASSAULT2_GP_NAME = constants.ARENA_GAMEPLAY_NAMES[6]
_EPIC_RANDOM_NAMES = (constants.ARENA_GAMEPLAY_NAMES[11], constants.ARENA_GAMEPLAY_NAMES[12])
ENABLED_ARENA_GAMEPLAY_NAMES = constants.ARENA_GAMEPLAY_NAMES[:3] + (_ASSAULT2_GP_NAME,) + _EPIC_RANDOM_NAMES
if constants.IS_DEVELOPMENT:
    ENABLED_ARENA_GAMEPLAY_NAMES += (constants.ARENA_GAMEPLAY_NAMES[13],)

def getDefaultMask():

    def getValue(name):
        return ArenaType.getVisibilityMask(ArenaType.getGameplayIDForName(name))

    return sum(map(getValue, ENABLED_ARENA_GAMEPLAY_NAMES))


def getMask():
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    settingsCore = dependency.instance(ISettingsCore)
    settingsMask = userMask = settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.GAMEPLAY, 'gameplayMask', getDefaultMask())
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
        LOG_ERROR('Gameplay is not available', name)

    gameplayMask = ArenaType.getGameplaysMask(gameplayNames)
    LOG_DEBUG('Set gameplay (names, mask)', gameplayNames, gameplayMask)
    _setMask(gameplayMask)


def isCreationEnabled(gameplayName):
    return gameplayName in ENABLED_ARENA_GAMEPLAY_NAMES


def _setMask(gameplayMask):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    settingsCore = dependency.instance(ISettingsCore)
    settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GAMEPLAY, {'gameplayMask': gameplayMask})
