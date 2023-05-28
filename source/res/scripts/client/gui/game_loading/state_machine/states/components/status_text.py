# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/components/status_text.py
import typing
import game_loading_bindings
from frameworks.state_machine import StateFlags, StateEvent
from gui.game_loading import loggers
from gui.game_loading.resources.consts import MilestonesTypes, Milestones
from gui.game_loading.state_machine.models import LoadingMilestoneModel
from gui.game_loading.state_machine.states.base import BaseViewResourcesTickingState, BaseTickingState
from gui.game_loading.state_machine.states.handlers.milestones import StatusTextMilestonesHandler
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.models import StatusTextModel
_logger = loggers.getStatesLogger()

class StatusTextStateComponent(BaseViewResourcesTickingState):
    __slots__ = ()

    def _view(self, resource):
        game_loading_bindings.setStatusText(resource.text)


class MilestoneStatusTextStateComponent(BaseTickingState):
    __slots__ = ('_milestonesHandler', '_milestone', '_retainMilestones')

    def __init__(self, stateID, milestonesSettings, flags=StateFlags.UNDEFINED, isSelfTicking=False, onCompleteEvent=None):
        super(MilestoneStatusTextStateComponent, self).__init__(stateID=stateID, flags=flags, isSelfTicking=isSelfTicking, onCompleteEvent=onCompleteEvent)
        self._milestonesHandler = StatusTextMilestonesHandler(milestonesSettings=milestonesSettings)
        self._milestone = self._milestonesHandler.getCurrentMilestone()
        self._retainMilestones = False
        _logger.debug('[%s] Apply default milestone: %s. Status: %s.', self, self._milestone.name, self._milestone.status.text)

    def setRetainMilestones(self, value):
        self._retainMilestones = value

    def _onEntered(self):
        super(MilestoneStatusTextStateComponent, self)._onEntered()
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
        super(MilestoneStatusTextStateComponent, self)._onExited()
        self._milestonesHandler.stop()
        self._milestonesHandler.onMilestoneReached -= self._onMilestoneReached
        self._milestonesHandler.onMilestoneTypeChanged -= self._onMilestoneTypeChanged

    def _onMilestoneReached(self, newMilestone):
        _logger.debug('[%s] Milestone reached: %s. New text status:  %s.', self, newMilestone.name, newMilestone.status.text)
        self._milestone = newMilestone
        if newMilestone.forceApply:
            self._setStatus(newMilestone.status.text)

    def _onMilestoneTypeChanged(self, newMilestone):
        _logger.debug('[%s] Milestone type changed: %s. New text status:  %s.', self, newMilestone.name, newMilestone.status.text)
        self._milestone = newMilestone

    def _task(self):
        self._setStatus(self._milestone.status.text)
        return self._milestone.status.minShowTimeSec

    @staticmethod
    def _setStatus(newStatus):
        if newStatus:
            game_loading_bindings.setStatusText(newStatus)
