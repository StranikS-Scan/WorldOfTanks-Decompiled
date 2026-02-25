# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/post_mortem_common.py
from constants import ARENA_BONUS_TYPE_NAMES
from debug_utils import LOG_ERROR

class POSTMORTEM_FEATURES:
    DEATH_FREE_CAM = 'deathfreecam'
    KILL_CAM = 'killcam'
    LOOK_AT_KILLER = 'lookAtKiller'
    ALL = (DEATH_FREE_CAM, KILL_CAM, LOOK_AT_KILLER)


class POSTMORTEM_MODIFIERS:
    POST_MORTEM = 'postmortemModifiers'
    DEATH_FREE_CAM = 'deathfreecamModifiers'
    KILL_CAM = 'killcamModifiers'
    ALL = (POST_MORTEM, DEATH_FREE_CAM, KILL_CAM)


def readPostMortemSection(dataSection, supportedFeatures=POSTMORTEM_FEATURES.ALL, supportedModifiers=POSTMORTEM_MODIFIERS.ALL):
    postMortemData = {}
    if dataSection is None:
        return postMortemData
    else:
        modes = dataSection.readString('bonusType')
        if not modes:
            LOG_ERROR('ARENA_BONUS_TYPE is missing from postmortem config. The entry is skipped.')
            return postMortemData
        modeSettings = {}
        for feature in supportedFeatures:
            modeSettings[feature] = dataSection.readBool(feature)

        modifiers = {}
        for modifierName in supportedModifiers:
            if dataSection[modifierName]:
                modifierList = list(dataSection[modifierName].readStrings('modifier'))
                if modifierList:
                    modifiers[modifierName] = modifierList

        for name in modes.split(' '):
            if name not in ARENA_BONUS_TYPE_NAMES:
                LOG_ERROR('Incorrect arena type name: {}'.format(name))
                continue
            postMortemData[name] = modeSettings
            postMortemData[name].update(modifiers)

        return postMortemData
