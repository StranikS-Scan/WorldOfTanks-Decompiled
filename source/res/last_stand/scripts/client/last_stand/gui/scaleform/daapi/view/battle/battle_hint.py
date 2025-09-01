# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/battle_hint.py
import copy
import BattleReplay
import typing
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID, LS_BATTLE_HINTS_QUEUE_ID
from last_stand.gui.scaleform.daapi.view.meta.BattleHintMeta import BattleHintMeta
from last_stand.gui.scaleform.daapi.view.meta.BattleHintProgressDefenceMeta import BattleHintProgressDefenceMeta
from last_stand.gui.scaleform.daapi.view.meta.BattleHintProgressConvoyMeta import BattleHintProgressConvoyMeta
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class BattleHint(BattleHintComponent, BattleHintMeta):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleHint, self).__init__(battleHintsQueueParams=LS_BATTLE_HINTS_QUEUE_ID)

    @property
    def lsBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def _populate(self):
        super(BattleHint, self)._populate()
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onBattleGoalChanged += self._onBattleGoalChanged

    def _dispose(self):
        super(BattleHint, self)._dispose()
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onBattleGoalChanged -= self._onBattleGoalChanged
        if BattleReplay.g_replayCtrl.isPlaying:
            self._hideHint()

    def _showHint(self, model, params):
        vo = model.createVO(params)
        if vo:
            self.as_showHintS(vo)

    def _hideHint(self):
        self.as_hideHintS()

    def _cancelFadeOut(self):
        self.as_cancelFadeOutS()

    def _onBattleGoalChanged(self, goalName):
        self.as_clearPinnableHintS()


class ProgressBarMixin(BattleHint):
    DEAD_ENEMY_STATUS_POSTFIX = '_dead'
    DEFAULT_ENEMY_STATUS = {'role': 'unknown',
     'isDead': False}
    STATUS_SORTING_ORDER = ['boss',
     'alpha',
     'charger',
     'heavyTank',
     'hunter',
     'mediumTank',
     'sentry',
     'turret',
     'AT-SPG',
     'bomber_alpha',
     'bomber',
     'catcher',
     'detonator',
     'ripper',
     'runner',
     'lightTank',
     'SPG',
     'unknown']

    def _getEnemiesInfo(self):
        return self.lsBattleGuiCtrl.getEnemiesInfo() if self.lsBattleGuiCtrl else {}

    def _formatEnemiesStatus(self, enemiesStatus):
        enemiesStatusFull = copy.deepcopy(enemiesStatus)
        missingStatusCount = self._getEnemiesInfo().get('totalEnemies', 0) - len(enemiesStatusFull)
        if missingStatusCount > 0:
            enemiesStatusFull.extend([self.DEFAULT_ENEMY_STATUS] * missingStatusCount)
        enemiesStatusFull = sorted(enemiesStatusFull, key=lambda status: (status['isDead'], self.STATUS_SORTING_ORDER.index(status['role'])))
        return [ (status['role'] + self.DEAD_ENEMY_STATUS_POSTFIX if status['isDead'] else status['role']) for status in enemiesStatusFull ]


class DefenceProgressBarBattleHint(ProgressBarMixin, BattleHintProgressDefenceMeta):

    def _populate(self):
        super(DefenceProgressBarBattleHint, self)._populate()
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onEnemiesInfoChanged += self._onEnemiesInfoChanged
            self.lsBattleGuiCtrl.onHealthBreakpointsChanged += self._onHealthBreakpointsChanged
            self.lsBattleGuiCtrl.onEnemiesStatusChanged += self._onEnemiesStatusChanged
        if self.guiSessionProvider.isReplayPlaying:
            self.as_handleAsReplayS()

    def _dispose(self):
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onEnemiesInfoChanged -= self._onEnemiesInfoChanged
            self.lsBattleGuiCtrl.onHealthBreakpointsChanged -= self._onHealthBreakpointsChanged
            self.lsBattleGuiCtrl.onEnemiesStatusChanged -= self._onEnemiesStatusChanged
        super(DefenceProgressBarBattleHint, self)._dispose()

    def _hideHint(self):
        super(DefenceProgressBarBattleHint, self)._hideHint()
        self._updateProgressBar(self._getEnemiesInfo())

    def _normalizeProgressValue(self, currentValue, maxValue):
        return round(float(maxValue - currentValue) / float(maxValue), 2) * 100 if maxValue > 0 else 0

    def _updateProgressBar(self, enemiesInfo):
        enemiesAlive = enemiesInfo.get('aliveEnemies', 0)
        currentHealth = enemiesInfo.get('currentHealth', 0)
        totalHealth = enemiesInfo.get('totalHealth', 0)
        lostHealth = max(0, totalHealth - currentHealth)
        normalizedProgressValue = self._normalizeProgressValue(lostHealth, totalHealth)
        self.as_updateProgressS(enemiesAlive, normalizedProgressValue, currentHealth)

    def _onEnemiesInfoChanged(self, enemiesInfo):
        self._updateProgressBar(enemiesInfo)

    def _onHealthBreakpointsChanged(self, healthBreakpoints):
        self.as_updateHealthPointsS(healthBreakpoints)

    def _onEnemiesStatusChanged(self, enemiesStatus):
        enemiesStatusList = self._formatEnemiesStatus(enemiesStatus)
        self.as_updateVehiclesS(enemiesStatusList)


class ConvoyProgressBarBattleHint(ProgressBarMixin, BattleHintProgressConvoyMeta):

    def __init__(self):
        super(ConvoyProgressBarBattleHint, self).__init__()
        self._convoyDistanceIndicator = None
        self._convoyHealth = None
        self._convoyStatus = None
        return

    def _populate(self):
        super(ConvoyProgressBarBattleHint, self)._populate()
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onConvoyStatusChanged += self._onConvoyStatusChanged
            self.lsBattleGuiCtrl.onConvoyDistanceIndicatorChanged += self._onConvoyDistanceIndicatorChanged
            self.lsBattleGuiCtrl.onConvoyHealthChanged += self._onConvoyHealthChanged
            self.lsBattleGuiCtrl.onEnemiesStatusChanged += self._onEnemiesStatusChanged
        if self.guiSessionProvider.isReplayPlaying:
            self.as_handleAsReplayS()

    def _dispose(self):
        if self.lsBattleGuiCtrl:
            self.lsBattleGuiCtrl.onConvoyStatusChanged -= self._onConvoyStatusChanged
            self.lsBattleGuiCtrl.onConvoyDistanceIndicatorChanged -= self._onConvoyDistanceIndicatorChanged
            self.lsBattleGuiCtrl.onConvoyHealthChanged -= self._onConvoyHealthChanged
            self.lsBattleGuiCtrl.onEnemiesStatusChanged -= self._onEnemiesStatusChanged
        super(ConvoyProgressBarBattleHint, self)._dispose()

    def _onConvoyHealthChanged(self, health):
        self._convoyHealth = health
        if (self._convoyStatus and self._convoyDistanceIndicator) is not None:
            self.as_updateProgressS(self.lsBattleGuiCtrl.MAX_UI_CONVOY_PROGRESS, self._convoyDistanceIndicator, self._convoyHealth)
        return

    def _onConvoyDistanceIndicatorChanged(self, distanceIndicator):
        self._convoyDistanceIndicator = distanceIndicator
        if (self._convoyStatus and self._convoyHealth) is not None:
            self.as_updateProgressS(self.lsBattleGuiCtrl.MAX_UI_CONVOY_PROGRESS, self._convoyDistanceIndicator, self._convoyHealth)
        return

    def _onConvoyStatusChanged(self, convoyStatus):
        if convoyStatus:
            self._convoyStatus = convoyStatus
            self.as_setConvoyVehiclesStatusS([ not vehicleInfo['isDead'] for vehicleInfo in convoyStatus ])

    def _onEnemiesStatusChanged(self, enemiesStatus):
        enemiesStatusList = self._formatEnemiesStatus(enemiesStatus)
        self.as_updateVehiclesS(enemiesStatusList)
