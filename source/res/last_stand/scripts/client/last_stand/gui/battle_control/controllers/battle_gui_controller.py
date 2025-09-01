# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/controllers/battle_gui_controller.py
import typing
from Event import Event
from last_stand.gui.battle_control.controllers.battle_gui_controller_base import LSBattleGUIControllerBase
from LSArenaPhasesComponent import LSArenaPhasesComponent

class LSBattleGoal(object):
    UNKNOWN = None
    DESTROY_ENEMIES = 'last_stand.destroyEnemies'
    STOP_CONVOY = 'last_stand.stopConvoy'
    CONVOY_DESTROYED_ENEMIES_LEFT = 'last_stand.convoyDestroyedEnemiesLeft'
    WAVE_FINISHED = 'last_stand.waveFinished'
    LAST_WAVE_FINISHED = 'last_stand.lastWaveFinished'


class LSBattleGUIController(LSBattleGUIControllerBase):
    MAX_UI_CONVOY_PROGRESS = 100
    _BATTLE_GOALS_WITHOUT_TIMER = [LSBattleGoal.WAVE_FINISHED, LSBattleGoal.LAST_WAVE_FINISHED]

    def __init__(self):
        super(LSBattleGUIController, self).__init__()
        self.onEnemiesInfoChanged = Event(self._eManager)
        self.onHealthBreakpointsChanged = Event(self._eManager)
        self.onEnemiesStatusChanged = Event(self._eManager)
        self.onConvoyStatusChanged = Event(self._eManager)
        self.onConvoyHealthChanged = Event(self._eManager)
        self.onConvoyDistanceIndicatorChanged = Event(self._eManager)
        self._enemiesInfo = {}
        self._healthBreakpoints = []
        self._enemiesStatus = []
        self._convoyStatus = None
        self._convoyDestroyed = False
        return

    def getEnemiesInfo(self):
        return self._enemiesInfo

    def updateEnemiesInfo(self, enemiesInfo):
        self._enemiesInfo = enemiesInfo
        self.onEnemiesInfoChanged(self._enemiesInfo)

    def updateConvoyStatus(self, convoyStatus):
        self._convoyStatus = convoyStatus
        if convoyStatus and all((data['isDead'] for data in convoyStatus)):
            self._convoyStatus = None
            self._convoyDestroyed = True
        self.onConvoyStatusChanged(convoyStatus)
        return

    def updateConvoyDistanceIndicator(self, value):
        self.onConvoyDistanceIndicatorChanged(value)

    def updateConvoyHealth(self, value):
        self.onConvoyHealthChanged(value)

    def updateHealthBreakpoints(self, healthBreakpoints):
        self._healthBreakpoints = []
        if self._enemiesInfo.get('totalHealth', 0) > 0:
            self._healthBreakpoints = [ round(float(value) / self._enemiesInfo['totalHealth'], 2) for value in healthBreakpoints ]
        self.onHealthBreakpointsChanged(self._healthBreakpoints)

    def updateEnemiesStatus(self, enemiesStatus):
        self._enemiesStatus = enemiesStatus
        self.onEnemiesStatusChanged(self._enemiesStatus)

    def _getRelevantGoal(self):
        if not self._getAliveAllyVehicles() or self._enemiesInfo.get('totalEnemies', 0) <= 0:
            return LSBattleGoal.UNKNOWN
        if self._convoyDestroyed and self._enemiesInfo.get('aliveEnemies', 0) > 0:
            return LSBattleGoal.CONVOY_DESTROYED_ENEMIES_LEFT
        if self._convoyStatus:
            return LSBattleGoal.STOP_CONVOY
        if self._enemiesInfo.get('aliveEnemies', 0):
            return LSBattleGoal.DESTROY_ENEMIES
        component = LSArenaPhasesComponent.getInstance()
        return LSBattleGoal.LAST_WAVE_FINISHED if component and component.isLastPhase() else LSBattleGoal.WAVE_FINISHED

    def _getHintParams(self):
        return {'num': self._enemiesInfo.get('aliveEnemies', 0)}

    def _removeBattleCommunicationMarkers(self, goal):
        if goal != LSBattleGoal.WAVE_FINISHED:
            return
        else:
            advChatCmp = getattr(self.guiSessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
            if advChatCmp:
                advChatCmp.cleanup()
            return
