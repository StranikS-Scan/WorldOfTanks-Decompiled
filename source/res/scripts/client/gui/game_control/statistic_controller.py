# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/statistic_controller.py
import logging
from adisp import process
from gui.wgcg.statistic.contexts import PlayerStatisticCtx
from helpers import dependency
from skeletons.gui.game_control import IWebStatisticsController
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)

class StatisticController(IWebStatisticsController):
    __webController = dependency.descriptor(IWebController)

    def __init__(self):
        super(StatisticController, self).__init__()

    def getStatisticData(self, playerID, battleType):
        result = dict()
        result['battlesCount'] = -1
        result['lossesCount'] = -1
        result['winsCount'] = -1
        result['hitsEfficiency'] = -1
        result['maxXP'] = -1
        result['avgXP'] = -1
        result['maxXPByVehicle'] = '--'
        result['avgDamage'] = -1
        result['maxDestroyed'] = -1
        result['maxDestroyedByVehicle'] = '--'
        result['marksOfMasteryText'] = ''
        result['significantAchievements'] = None
        result['nearestAchievements'] = None
        result['globalRating'] = -1
        result['isWTR'] = True
        return result

    def getVehicleData(self, playerID, vehicleCD, battleType):
        return {}

    def __isByServerSwitchEnabled(self):
        pass

    @process
    def __fetchInfo(self):
        response = yield self.__webController.sendRequest(ctx=PlayerStatisticCtx(None, None))
        if response.isSuccess():
            data = (response.getData() or {}).get('data', {})
        else:
            _logger.warning('Unable to fetch statistic info. Code: %s.', response.getCode())
        return
