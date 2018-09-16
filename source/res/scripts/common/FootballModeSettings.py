# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/FootballModeSettings.py
from debug_utils import LOG_DEBUG_DEV
import Math

class FootballModeEvents(object):
    SPAWN_BALL = 'SpawnBall'
    REMOVE_BALL = 'RemoveBall'
    GOAL = 'Goal'
    ASSIST_GOAL = 'AssetGoal'
    STOLE_BALL = 'StoleBall'


class FootballMode:

    def __init__(self, events):
        self.events = events


class FootballModeSettings:
    OVERTIME_BATTLE_DURATION = 235
    OVERTIME_BALL_IDLE = 10
    OVERTIME_PREBATTLE_DURATION = 15

    def __init__(self):
        LOG_DEBUG_DEV('FootballModeSettings for football')
        self.__ballSpawnPoint = [0, 0, 0]
        self.__fieldPosition = [0, 0, 0]
        self.__cellModel = ''
        self.__cellPosition = Math.Vector3(0, 0, 0)

    @property
    def getBallSpawnPoint(self):
        return self.__ballSpawnPoint

    @property
    def getFieldPosition(self):
        return self.__fieldPosition

    @property
    def cellModel(self):
        return self.__cellModel

    @property
    def cellPosition(self):
        return self.__cellPosition

    def setBallSpawnPoint(self, position):
        LOG_DEBUG_DEV('[FOOTBALL_MODE_SETTINGS] setBallSpawnPoint: ', position)
        self.__ballSpawnPoint = position

    def setFieldPosition(self, pos):
        LOG_DEBUG_DEV('[FOOTBALL_MODE_SETTINGS] setFieldPosition: ', pos)
        self.__fieldPosition = pos

    def setCellModel(self, path):
        LOG_DEBUG_DEV('[FOOTBALL_MODE_SETTINGS] setCellMode: ', path)
        self.__cellModel = path

    def setCellPosition(self, position):
        LOG_DEBUG_DEV('[FOOTBALL_MODE_SETTINGS] setCellPosition: ', position)
        self.__cellPosition = position
