# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/stats_exchange/commander_data.py
import typing
import RTSShared
from helpers import dependency
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Union
    from RTSShared import AnyVehicleCommanderData, OwnVehicleCommanderData

class RTSCommanderDataComponent(broker.VehicleComponent):
    __slots__ = ('__isAttached', '__hasCommanderData', '__health', '__maxHealth', '__manner', '__order')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RTSCommanderDataComponent, self).__init__()
        self.__isAttached = False
        self.__hasCommanderData = False
        self.__health = 0
        self.__maxHealth = 0
        self.__manner = 0
        self.__order = 0

    def clear(self):
        self.__isAttached = False
        self.__hasCommanderData = False
        self.__health = 0
        self.__maxHealth = 0
        self.__manner = 0
        self.__order = 0
        super(RTSCommanderDataComponent, self).clear()

    def get(self, forced=False):
        data = super(RTSCommanderDataComponent, self).get()
        del data['isEnemy']
        data.update({'isAttached': self.__isAttached,
         'hasCommanderData': self.__hasCommanderData,
         'health': self.__health,
         'maxHealth': self.__maxHealth,
         'manner': self.__manner,
         'order': self.__order})
        return data

    def addVehicleCommanderData(self, commanderData, isAttached):
        self.__isAttached = isAttached
        if commanderData is None:
            return
        else:
            self.__hasCommanderData = commanderData.commanderVehicleID > 0
            if not commanderData.isOwn:
                return
            self.__health = commanderData.health
            self.__maxHealth = commanderData.maxHealth
            orderData = commanderData.orderData
            if orderData is None:
                return
            order = orderData.order
            self.__manner = RTSShared.getMannerOrDefault(commanderData)
            self.__order = order.value if order is not None else 0
            return


class RTSCommanderDataExchangeBlock(broker.ExchangeBlock):

    def addTotalStats(self, stats):
        pass

    def addSortIDs(self, arenaDP, *flags):
        pass
