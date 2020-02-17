# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/statistic/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class PlayerStatisticCtx(CommonWebRequestCtx):

    def __init__(self, playerID, battleType, **kwargs):
        super(PlayerStatisticCtx, self).__init__(**kwargs)
        self.__playerID = playerID
        self.__battleType = battleType

    def getBattleType(self):
        return self.__battleType

    def getPlayerID(self):
        return self.__playerID

    def getRequestType(self):
        return WebRequestDataType.PLAYER_STATISTIC

    def isAuthorizationRequired(self):
        return True

    def isCaching(self):
        return True


class VehicleStatisticCtx(CommonWebRequestCtx):

    def __init__(self, playerID, battleType, vehicleCD, **kwargs):
        super(VehicleStatisticCtx, self).__init__(**kwargs)
        self.__playerID = playerID
        self.__battleType = battleType
        self.__vehicleCD = vehicleCD

    def getPlayerID(self):
        return self.__playerID

    def getBattleType(self):
        return self.__battleType

    def getVehicleCD(self):
        return self.__vehicleCD

    def getRequestType(self):
        return WebRequestDataType.PLAYER_VEHICLE_STATISTIC

    def isAuthorizationRequired(self):
        return True

    def isCaching(self):
        return True
