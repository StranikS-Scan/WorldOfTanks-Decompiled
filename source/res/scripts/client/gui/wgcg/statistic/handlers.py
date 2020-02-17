# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/statistic/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class StatisticRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.PLAYER_STATISTIC: self.__getPlayerStatistic,
         WebRequestDataType.PLAYER_VEHICLE_STATISTIC: self.__getVehicleStatistic}
        return handlers

    def __getPlayerStatistic(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('data_profile', 'get_player_statistic'), player_id=ctx.getPlayerID(), battle_type=ctx.getbattleType())

    def __getVehicleStatistic(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('data_profile', 'get_player_vehicle_statistic'), player_id=ctx.getPlayerID(), battle_type=ctx.getbattleType(), vehicle_CD=ctx.getVehicleCD())
