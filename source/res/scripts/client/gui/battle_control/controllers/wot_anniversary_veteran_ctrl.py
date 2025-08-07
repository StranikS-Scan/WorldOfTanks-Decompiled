# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/wot_anniversary_veteran_ctrl.py
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from messenger import MessengerEntry, g_settings
from skeletons.gui.battle_session import IBattleSessionProvider

class WotAnniversaryVeteranController(IArenaVehiclesController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getControllerID(self):
        return BATTLE_CTRL_ID.WOT_ANNIVERSARY_VETERAN_CTRL

    def arenaLoadCompleted(self):
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is None or arena.arenaInfo is None:
            return
        else:
            veteranInfo = arena.arenaInfo.dynamicComponents.get('veteranInfo')
            if veteranInfo is None or veteranInfo.messageInfo is None:
                return
            messageInfo = veteranInfo.messageInfo
            arenaDP = self.__sessionProvider.getArenaDP()
            playerSessionID = int(arenaDP.getVehicleInfo().player.avatarSessionID)
            if playerSessionID in messageInfo.veterans + messageInfo.anonymVeterans:
                return
            names = []
            for sessionID in messageInfo.veterans:
                vehID = arenaDP.getVehIDBySessionID(str(sessionID))
                if vehID is not None:
                    names.append(arenaDP.getVehicleInfo(vehID).player.getPlayerLabel())

            bonusText = str(int(messageInfo.creditsBonus * 100))
            if len(names) > 1:
                separator = backport.text(R.strings.wot_anniversary.veteranBonus.notifications.playerNames.separator())
                message = backport.text(R.strings.wot_anniversary.veteranBonus.notifications.manyPlayers(), bonus=bonusText, playerNames=separator.join(names))
            elif names:
                message = backport.text(R.strings.wot_anniversary.veteranBonus.notifications.onePlayer(), bonus=bonusText, playerName=names[0])
            else:
                message = backport.text(R.strings.wot_anniversary.veteranBonus.notifications.noOne(), bonus=bonusText)
            MessengerEntry.g_instance.gui.addClientMessage(g_settings.htmlTemplates.format('battleWarningMessage', ctx={'fontColor': '#FFC364',
             'message': message}))
            return


def createWotAnniversaryVeteranController():
    return WotAnniversaryVeteranController()
