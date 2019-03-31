# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scalefrom/MessengerBattlePageInterface.py
# Compiled at: 2011-06-17 18:55:59
from gui.BattleContext import g_battleContext
from messenger import BATTLE_MESSAGE_FORMAT, g_settings
from messenger.UsersManager import UsersManager
from messenger.gui.interfaces import MessengerPageInterface

class MessengerBattlePageInterface(MessengerPageInterface):
    __mformat = BATTLE_MESSAGE_FORMAT
    _pColorSchemes = g_settings.getBattlePlayerHexCS()
    _msgColorSchemes = g_settings.getBattleMsgHexCS()

    def __init__(self):
        super(MessengerBattlePageInterface, self).__init__()
        self.teamCid = 0
        self.commonCid = 0

    def format(self, message, system=False):
        playerColor, msgColor = self.getColors(message, message.originator)
        return self.__mformat % (playerColor,
         unicode(g_battleContext.getFullPlayerName(accID=message.originator), 'utf-8', errors='ignore'),
         msgColor,
         message.data)

    def addMessage(self, message, format=True, system=False):
        if format:
            return self.format(message, system)
        return message.data

    def getColors(self, message, playerDbId):
        cid = message.channel
        uid = message.originator
        msgColor = self._msgColorSchemes['unknown']
        playerColor = self._msgColorSchemes['unknown']
        if cid == self.teamCid:
            msgColor = self._msgColorSchemes['team']
            if UsersManager.isCurrentPlayer(playerDbId):
                playerColor = self._pColorSchemes['himself']
            elif g_battleContext.isTeamKiller(accID=uid):
                playerColor = self._pColorSchemes['teamkiller']
            elif g_battleContext.isSquadMan(accID=uid):
                playerColor = self._pColorSchemes['squadman']
            else:
                playerColor = self._pColorSchemes['teammate']
        elif cid == self.commonCid:
            msgColor = self._msgColorSchemes['common']
            if UsersManager.isCurrentPlayer(playerDbId):
                playerColor = self._pColorSchemes['himself']
            elif self.channels.hasExistMemeber(self.teamCid, uid):
                if g_battleContext.isTeamKiller(accID=uid):
                    playerColor = self._pColorSchemes['teamkiller']
                elif g_battleContext.isSquadMan(accID=uid):
                    playerColor = self._pColorSchemes['squadman']
                else:
                    playerColor = self._pColorSchemes['teammate']
            elif self.channels.hasExistMemeber(self.commonCid, uid):
                playerColor = self._pColorSchemes['enemy']
        return (playerColor, msgColor)

    def updateColors(self, **kwargs):
        self._pColorSchemes = g_settings.getBattlePlayerHexCS(**kwargs)
