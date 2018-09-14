# Embedded file name: scripts/client/gui/Scaleform/ingame_help.py
from account_helpers.AccountSettings import AccountSettings
import BigWorld, ResMgr
import CommandMapping
import constants
from debug_utils import LOG_DEBUG, LOG_ERROR
from helpers import VERSION_FILE_PATH
from gui.Scaleform.windows import UIInterface

class IngameHelp(object):
    __viewCmds = ('CMD_MOVE_FORWARD', 'CMD_MOVE_BACKWARD', 'CMD_ROTATE_LEFT', 'CMD_ROTATE_RIGHT', 'CMD_INCREMENT_CRUISE_MODE', 'CMD_DECREMENT_CRUISE_MODE', 'CMD_CM_VEHICLE_SWITCH_AUTOROTATION', 'CMD_RELOAD_PARTIAL_CLIP', 'CMD_CM_SHOOT', 'CMD_CM_LOCK_TARGET', 'CMD_CM_LOCK_TARGET_OFF', 'CMD_CM_ALTERNATE_MODE', 'CMD_VEHICLE_MARKERS_SHOW_INFO', 'CMD_RADIAL_MENU_SHOW', 'CMD_CHAT_SHORTCUT_ATTACK', 'CMD_VOICECHAT_MUTE', 'CMD_MINIMAP_VISIBLE', 'CMD_TOGGLE_GUI')
    __viewCmdMapping = []
    __version = -1

    def __init__(self, parentUI):
        self.buildCmdMapping()
        self.__ui = parentUI

    def __del__(self):
        LOG_DEBUG('IngameHelp deleted')

    def start(self):
        if self.__ui:
            self.__ui.addExternalCallbacks({'battle.ingameHelp.getCommandMapping': self.onGetCommandMapping})

    def destroy(self):
        if self.__ui:
            self.__ui.removeExternalCallbacks('battle.ingameHelp.getCommandMapping')
        self.__ui = None
        return

    def isRequiredToShow(self):
        playerHelpVersion = int(AccountSettings.getSettings('ingameHelpVersion'))
        return constants.IS_SHOW_INGAME_HELP_FIRST_TIME and self.__version is not -1 and playerHelpVersion is not self.__version

    def buildCmdMapping(self):
        cmdMap = CommandMapping.g_instance
        self.__viewCmdMapping = []
        for command in self.__viewCmds:
            key = cmdMap.get(command)
            self.__viewCmdMapping.append(command)
            self.__viewCmdMapping.append(BigWorld.keyToString(key) if key is not None else 'NONE')

        return

    def onGetCommandMapping(self, responceId, *args):
        args = [responceId]
        args.extend(self.__viewCmdMapping)
        self.__ui.respond(args)

    @classmethod
    def _readVersion(cls):
        dSection = ResMgr.openSection(VERSION_FILE_PATH)
        if dSection is None:
            LOG_ERROR('Can not open file:', VERSION_FILE_PATH)
            IngameHelp.__version = -1
            return
        else:
            IngameHelp.__version = dSection.readInt('ingameHelpVersion', -1)
            return

    @classmethod
    def _writeVersionForCurrentPlayer(cls):
        AccountSettings.setSettings('ingameHelpVersion', IngameHelp.__version)


class IngameHelpLobbyDelegator(UIInterface):

    def __init__(self):
        super(IngameHelpLobbyDelegator, self).__init__()

    def populateUI(self, proxy):
        super(IngameHelpLobbyDelegator, self).populateUI(proxy)
        self.__callback = None
        self.__ingameHelp = IngameHelp(proxy)
        self.__ingameHelp.start()
        self.__ingameHelp._readVersion()
        return

    def dispossessUI(self):
        self.__ingameHelp.destroy()
        self.__ingameHelp = None
        self.__callback = None
        super(IngameHelpLobbyDelegator, self).dispossessUI()
        return

    def isRequiredToShow(self):
        return self.__ingameHelp.isRequiredToShow()

    def showIngameHelp(self, callback = None):
        self.__ingameHelp.buildCmdMapping()
        self.__ingameHelp._writeVersionForCurrentPlayer()
        self.__callback = callback
        self.uiHolder.call('common.ingameHelp.show')

    def closeIngameHelp(self):
        if self.__callback is not None:
            self.__callback()
            self.__callback = None
        return

    def onClose(self, _):
        self.closeIngameHelp()
