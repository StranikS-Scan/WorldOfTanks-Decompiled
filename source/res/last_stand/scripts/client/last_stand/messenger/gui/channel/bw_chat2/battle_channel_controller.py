# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/messenger/gui/channel/bw_chat2/battle_channel_controller.py
import types
import BigWorld
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from last_stand_common.last_stand_constants import LSMarkersType, LSMarkerComponentNames
from messenger.gui.Scaleform.channels.bw_chat2.battle_controllers import TeamChannelController
from messenger.m_constants import MESSENGER_COMMAND_TYPE
from messenger_common_chat2 import MESSENGER_ACTION_IDS
from gui.impl import backport
from gui.impl.gen import R
from messenger import g_settings

class LSTeamChannelController(TeamChannelController):
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
                if not entity:
                    return

                def getTextWithGridId(rString):
                    mapsCtrl = self.sessionProvider.dynamic.maps
                    if mapsCtrl and mapsCtrl.hasMinimapGrid():
                        cellId = mapsCtrl.getMinimapCellIdByPosition(entity.position)
                        return backport.text(rString, gridId=mapsCtrl.getMinimapCellNameById(cellId))
                    else:
                        return None

                rPath = R.strings.last_stand_battle.arena.marker
                markerCommand2Text = {(LSMarkerComponentNames.MAGNUS, LSMarkersType.MAGNUS): {BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT: (rPath.move_to_magnus(), backport.text),
                                                                         BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT: (rPath.attention_to_magnus(), backport.text)},
                 (LSMarkerComponentNames.CAMP, LSMarkersType.CAMP): {BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT: (rPath.move_to_camp(), backport.text),
                                                                     BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT: (rPath.attention_to_camp(), getTextWithGridId)}}
                for componentName, markerStyle in markerCommand2Text:
                    component = entity.dynamicComponents.get(componentName)
                    if component and component.style == markerStyle:
                        params = markerCommand2Text[componentName, markerStyle].get(battleChatCommand.name, None)
                        if params:
                            rString, wrapper = params
                            commandText = wrapper(rString)
                            if commandText:
                                break
                else:
                    return (isCurrent, u'')

            text = self._mBuilder.setColors(avatarSessionID).setName(avatarSessionID).setText(commandText).build()
        else:
            text = command.getCommandText()
        return (isCurrent, text)
