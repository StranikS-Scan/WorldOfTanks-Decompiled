# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/callout_panel.py
import CommandMapping
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from gui.Scaleform.daapi.view.meta.CalloutPanelMeta import CalloutPanelMeta
from gui.Scaleform.genConsts.BATTLEDAMAGELOG_IMAGES import BATTLEDAMAGELOG_IMAGES as _IMAGES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.key_mapping import getReadableKey
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_VEHICLE_CLASS_TAGS_ICONS = {'lightTank': _IMAGES.WHITE_ICON_LIGHTTANK_16X16,
 'mediumTank': _IMAGES.WHITE_ICON_MEDIUM_TANK_16X16,
 'heavyTank': _IMAGES.WHITE_ICON_HEAVYTANK_16X16,
 'SPG': _IMAGES.WHITE_ICON_SPG_16X16,
 'AT-SPG': _IMAGES.WHITE_ICON_AT_SPG_16X16}
_CALLOUT_COMMMAND_TO_UI_VISUAL_STATE = {BATTLE_CHAT_COMMAND_NAMES.HELPME: BATTLE_CHAT_COMMAND_NAMES.HELPME,
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK: BATTLE_CHAT_COMMAND_NAMES.REPLY,
 BATTLE_CHAT_COMMAND_NAMES.THANKS: BATTLE_CHAT_COMMAND_NAMES.REPLY,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY: BATTLE_CHAT_COMMAND_NAMES.THANKS}

class CalloutPanel(CalloutPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(CalloutPanel, self).__init__()
        self.__hidingInProgress = False

    def onHideStart(self):
        self.__hidingInProgress = True

    def onHideCompleted(self):
        self.__reset()

    def __reset(self):
        self.__hidingInProgress = False

    def setShowData(self, senderVehicleID, cmdName):
        vInfoVO = self.sessionProvider.getArenaDP().getVehicleInfo(senderVehicleID)
        if not vInfoVO:
            return
        vehicleTypeImg = _VEHICLE_CLASS_TAGS_ICONS[vInfoVO.vehicleType.classTag]
        vehName = vInfoVO.vehicleType.shortNameWithPrefix
        pressText = backport.text(R.strings.ingame_gui.quickReply.hint.press())
        if cmdName == BATTLE_CHAT_COMMAND_NAMES.HELPME:
            hintText = backport.text(R.strings.ingame_gui.quickReply.hint.toHelp())
        else:
            hintText = backport.text(R.strings.ingame_gui.quickReply.hint.toAcknowledge())
        keyName = getReadableKey(CommandMapping.CMD_RADIAL_MENU_SHOW)
        self.as_setDataS(cmdName, vehicleTypeImg, vehName, pressText, hintText, keyName)

    def setHideData(self, wasAnswered=False, commandReceived=None):
        if self.__hidingInProgress is True:
            return
        else:
            cmdName = _CALLOUT_COMMMAND_TO_UI_VISUAL_STATE.get(commandReceived, None)
            answered = wasAnswered and cmdName is not None
            self.as_setHideDataS(answered, cmdName)
            return
