# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/TanksBirthdayAccountComponent.py
import typing
import BigWorld
from mt_birthday_common.constants import CMD_GET_PLAYERS_FROM_BATTLES
if typing.TYPE_CHECKING:
    from Account import Account

class TanksBirthdayAccountComponent(BigWorld.StaticScriptComponent):

    @property
    def _account(self):
        return self.entity

    def getPlayersFromBattles(self, arenaUniqueIds, callback):
        self._account.commandProxy.perform(CMD_GET_PLAYERS_FROM_BATTLES, arenaUniqueIds, [], callback)
