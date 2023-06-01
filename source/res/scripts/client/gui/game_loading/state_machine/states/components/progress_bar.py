# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/components/progress_bar.py
import typing
from frameworks.state_machine import StateFlags
import game_loading_bindings
from gui.game_loading import loggers
from gui.game_loading.state_machine.states.base import BaseTickingState
from gui.game_loading.state_machine.states.handlers.milestones import ProgressBarMilestonesHandler
if typing.TYPE_CHECKING:
    from frameworks.state_machine import StateEvent
    from gui.game_loading.preferences import GameLoadingPreferences
    from gui.game_loading.state_machine.models import ProgressSettingsModel, LoadingMilestoneModel
_logger = loggers.getStatesLogger()

class ProgressBarStateComponent(BaseTickingState):
    __slots__ = ('_ticks', '_progress', '_progressLimit', '_progressMax', '_settings', '_preferences')

    def __init__(self, stateID, settings, preferences=None, flags=StateFlags.UNDEFINED, isSelfTicking=False, onCompleteEvent=None):
        super(ProgressBarStateComponent, self).__init__(stateID=stateID, flags=flags, isSelfTicking=isSelfTicking, onCompleteEvent=onCompleteEvent)
        self._settings = settings
        self._preferences = preferences
        if self._preferences is None or self._preferences.getLoadingMax(self.getStateID()) is None:
            self._progressMax = self._calcProgressMax(self._settings.ticksInProgress)
        else:
            self._progressMax = self._preferences.getLoadingMax(self.getStateID())
        self._setInitialProgress()
        return

    def _onExited(self):
        super(ProgressBarStateComponent, self)._onExited()
        progressMax = self._calcProgressMax(self._ticks)
        self._saveProgressMax(progressMax)
        self._setInitialProgress()
        _logger.debug('[%s] max progress saved: %s.', self, self._progressMax)

    def _saveProgressMax(self, progressMax):
        self._progressMax = progressMax
        if self._preferences is not None:
            self._preferences.setLoadingMax(self.getStateID(), progressMax)
        return

    def _setInitialProgress(self):
        self._progress = self._calcProgress(self._settings.startPercent)
        self._progressLimit = self._calcProgress(self._settings.limitPercent)
        self._ticks = 0

    def _task(self):
        self._increaseTicks()
        if not self._isLimitReached():
            self._increaseProgress()
        return self._settings.minTickTimeSec

    def _increaseTicks(self):
        self._ticks += 1

    def _increaseProgress(self):
        progress = self._progress + 1
        self._setProgress(progress)

    def _isLimitReached(self):
        return self._progress >= self._progressLimit or self._progress >= self._progressMax

    def _setProgress(self, progress):
        self._progress = progress
        game_loading_bindings.setProgress(int(self._progress), int(self._progressMax))

    def _calcProgress(self, percent):
        return self._progressMax * percent / 100

    def _calcProgressMax(self, ticks):
        return ticks * 100.0 / (self._settings.limitPercent - self._settings.startPercent)


class MilestoneProgressBarStateComponent(ProgressBarStateComponent):
    __slots__ = ('_milestonesHandler', '_milestone', '_milestoneLimit', '_retainMilestones')

    def __init__(self, settings, preferences, milestonesSettings, stateID, flags=StateFlags.UNDEFINED, isSelfTicking=False, onCompleteEvent=None):
        super(MilestoneProgressBarStateComponent, self).__init__(settings=settings, preferences=preferences, stateID=stateID, flags=flags, isSelfTicking=isSelfTicking, onCompleteEvent=onCompleteEvent)
        self._milestone = None
        self._milestonesHandler = ProgressBarMilestonesHandler(milestonesSettings=milestonesSettings)
        self._retainMilestones = False
        return

    def setRetainMilestones(self, value):
        self._retainMilestones = value

    def _onEntered(self):
        super(MilestoneProgressBarStateComponent, self)._onEntered()
        self._milestonesHandler.onMilestoneReached += self._onMilestoneReached
        self._milestonesHandler.onMilestoneTypeChanged += self._onMilestoneTypeChanged
        if not self._retainMilestones:
            self._milestone = None
            self._milestonesHandler.init()
        elif self._milestone is not None:
            self._onMilestoneReached(self._milestone)
        self._milestonesHandler.start()
        return

    def _onExited(self):
        super(MilestoneProgressBarStateComponent, self)._onExited()
        self._milestonesHandler.stop()
        self._milestonesHandler.onMilestoneReached -= self._onMilestoneReached
        self._milestonesHandler.onMilestoneTypeChanged -= self._onMilestoneTypeChanged

    def _onMilestoneReached(self, newMilestone):
        _logger.debug('[%s] Milestone reached: %s. New progress limit:  %s.', self, newMilestone.name, newMilestone.percent)
        newMilestoneLimit = self._calcProgress(newMilestone.percent)
        prevMilestoneLimit = self._getMilestoneLimit()
        if newMilestone.forceApply:
            self._setProgress(progress=newMilestoneLimit)
        elif prevMilestoneLimit is not None and self._progress < prevMilestoneLimit:
            self._setProgress(progress=prevMilestoneLimit)
        self._milestone = newMilestone
        return

    def _onMilestoneTypeChanged(self, newMilestone):
        _logger.debug('[%s] Milestone type changed: %s. New progress limit:  %s.', self, newMilestone.name, newMilestone.percent)
        self._milestone = newMilestone

    def _getMilestoneLimit(self):
        return self._calcProgress(self._milestone.percent) if self._milestone else None

    def _isLimitReached(self):
        milestoneLimit = self._getMilestoneLimit()
        isMilestoneLimitReached = milestoneLimit is not None and self._progress >= milestoneLimit
        return super(MilestoneProgressBarStateComponent, self)._isLimitReached() or isMilestoneLimitReached
