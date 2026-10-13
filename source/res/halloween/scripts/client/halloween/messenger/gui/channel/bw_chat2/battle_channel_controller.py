# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/messenger/gui/channel/bw_chat2/battle_channel_controller.py
from __future__ import absolute_import
import types
import BigWorld
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from halloween_common.halloween_constants import HalloweenMarkersType, HalloweenMarkerComponentNames
from messenger.gui.Scaleform.channels.bw_chat2.battle_controllers import TeamChannelController
from messenger.m_constants import MESSENGER_COMMAND_TYPE
from messenger_common_chat2 import MESSENGER_ACTION_IDS
from gui.impl import backport
from gui.impl.gen import R
from messenger import g_settings

class HalloweenTeamChannelController(TeamChannelController):
    _BASE_RELATED_COMMANDS_NAME = (BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT, BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT)

    def _formatCommand(self, command):
        isCurrent = False
        if command.getCommandType() == MESSENGER_COMMAND_TYPE.BATTLE:
            avatarSessionID = command.getSenderID()
            isCurrent = command.isSender()
            _getTargetOriginal = getattr(command, '_getTarget')

            def _getTargetReplaced(obj):
                vID = obj.getFirstTargetID()
                vInfo = obj.sessionProvider.getArenaDP().getVehicleInfo(vID)
                if not vInfo.isEnemy():
                    return _getTargetOriginal()
                target = vInfo.vehicleType.name
                if obj.isReceiver():
                    target = g_settings.battle.targetFormat % {'target': target}
                return target

            setattr(command, '_getTarget', types.MethodType(_getTargetReplaced, command))
            commandText = command.getCommandText()
            battleChatCommand = MESSENGER_ACTION_IDS.battleChatCommandFromActionID(command.getID())
            if battleChatCommand.name in self._BASE_RELATED_COMMANDS_NAME:
                targetID = command.getFirstTargetID()
                entity = BigWorld.entities.get(targetID)
                if entity and HalloweenMarkerComponentNames.SOULS_COLLECTOR in entity.dynamicComponents and entity.hwSoulsCollectorMarker.style == HalloweenMarkersType.SOULS_COLLECTOR:
                    if battleChatCommand.name == BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT:
                        commandText = backport.text(R.strings.halloween_battle.arena.marker.move_to_volot())
                    elif battleChatCommand.name == BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT:
                        commandText = backport.text(R.strings.halloween_battle.arena.marker.attention_to_volot())
                elif entity and HalloweenMarkerComponentNames.CAMP in entity.dynamicComponents and entity.hwCampMarker.style == HalloweenMarkersType.CAMP:
                    if battleChatCommand.name == BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT:
                        commandText = backport.text(R.strings.halloween_battle.arena.marker.move_to_camp())
                    elif battleChatCommand.name == BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT:
                        mapsCtrl = self.sessionProvider.dynamic.maps
                        if mapsCtrl and mapsCtrl.hasMinimapGrid():
                            cellId = mapsCtrl.getMinimapCellIdByPosition(entity.position)
                            commandText = backport.text(R.strings.halloween_battle.arena.marker.attention_to_camp(), gridId=mapsCtrl.getMinimapCellNameById(cellId))
                else:
                    return (isCurrent, u'')
            text = self._mBuilder.setColors(avatarSessionID).setName(avatarSessionID).setText(commandText).build()
        else:
            text = command.getCommandText()
        return (isCurrent, text)
