# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/required_libraries_config.py
from soft_exception import SoftException
LOBBY_REQUIRED_LIBRARIES = ['windows.swf',
 'animations.swf',
 'common_i18n.swf',
 'guiControlsLogin.swf',
 'guiControlsLoginBattleDynamic.swf',
 'ub_components.swf',
 'serviceMessageComponents.swf']
BATTLE_REQUIRED_LIBRARIES = ['windows.swf',
 'common_i18n.swf',
 'popovers.swf',
 'guiControlsLobbyBattleDynamic.swf',
 'guiControlsLoginBattleDynamic.swf',
 'guiControlsBattleDynamic.swf',
 'battleMessages.swf']

def addLobbyRequiredLibraries(swfList, personality):
    for swf in swfList:
        if swf in LOBBY_REQUIRED_LIBRARIES:
            raise SoftException('LOBBY_REQUIRED_LIBRARIES already has swf:{swf}. Personality: {personality}'.format(swf=swf, personality=personality))
        LOBBY_REQUIRED_LIBRARIES.append(swf)


def addBattleRequiredLibraries(swfList, personality):
    for swf in swfList:
        if swf in BATTLE_REQUIRED_LIBRARIES:
            raise SoftException('BATTLE_REQUIRED_LIBRARIES already has swf:{swf}. Personality: {personality}'.format(swf=swf, personality=personality))
        BATTLE_REQUIRED_LIBRARIES.append(swf)
