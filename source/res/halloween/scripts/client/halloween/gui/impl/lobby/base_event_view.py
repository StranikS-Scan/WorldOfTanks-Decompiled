# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/base_event_view.py
import HWAccountSettings
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from halloween.gui.game_control.halloween_progress_controller import Phase
from halloween.gui.impl.gen.view_models.views.lobby.common.phase_item_model import PhaseStatus
from halloween.hw_constants import PhaseState, AccountSettingsKeys
from halloween.skeletons.gui.game_event_controller import IHalloweenProgressController
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
from halloween.gui.impl.gen.view_models.views.lobby.common.base_view_model import BaseViewModel
STATUS_MAP = {PhaseState.ACTIVE: PhaseStatus.ACTIVE,
 PhaseState.LOCK: PhaseStatus.LOCKED,
 PhaseState.OUT_OF_DATE: PhaseStatus.OVERDUE}

def isNewIntro(phase):
    viewedIntro = HWAccountSettings.getSettings(AccountSettingsKeys.VIEWED_WITHES_INTRO)
    return phase and phase.phaseIndex not in viewedIntro and not phase.isLock()


def isNewOutro(phase):
    viewedOutro = HWAccountSettings.getSettings(AccountSettingsKeys.VIEWED_WITHES_OUTRO)
    return phase and phase.phaseIndex not in viewedOutro and not phase.isLock() and phase.hasPlayerTmanBonus()


class BaseEventView(ViewImpl, IGlobalListener):
    DESTROY_ON_EVENT_DISABLED = True
    _eventController = dependency.descriptor(IEventBattlesController)
    _hwController = dependency.descriptor(IHalloweenProgressController)

    @property
    def viewModel(self):
        return super(BaseEventView, self).getViewModel()

    def onPrbEntitySwitched(self):
        if not self._eventController.isEventPrbActive() or self._hwController.isPostPhase():
            self._onClose()

    def _subscribe(self):
        self.viewModel.onClose += self._onClose
        self._hwController.onChangeActivePhase += self._onChangeActivePhase
        self._hwController.onQuestsUpdated += self._onQuestUpdated
        self._hwController.onSyncCompleted += self._onSyncCompleted
        self._eventController.onEventDisabled += self._onEventDisabled
        super(BaseEventView, self)._subscribe()

    def _unsubscribe(self):
        self.viewModel.onClose -= self._onClose
        self._hwController.onChangeActivePhase -= self._onChangeActivePhase
        self._hwController.onQuestsUpdated -= self._onQuestUpdated
        self._hwController.onSyncCompleted -= self._onSyncCompleted
        self._eventController.onEventDisabled -= self._onEventDisabled
        super(BaseEventView, self)._unsubscribe()

    def _onLoading(self, *args, **kwargs):
        super(BaseEventView, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()
        self._fillViewModel()

    def _finalize(self):
        self.stopGlobalListening()
        super(BaseEventView, self)._finalize()

    def _onEventDisabled(self):
        self._onClose()

    def _onChangeActivePhase(self, _):
        self._fillViewModel()

    def _onSyncCompleted(self):
        self._fillViewModel()

    def _onQuestUpdated(self):
        self._fillViewModel()

    def _onClose(self):
        self.destroyWindow()

    def _fillViewModel(self):
        with self.viewModel.transaction() as model:
            phase = self._hwController.phasesHalloween.getActivePhase()
            if phase is None:
                return
            model.setSelectedPhase(phase.phaseIndex)
            self._fillPhase(model.phase, phase)
        return

    def _fillPhase(self, phaseModel, phase):
        phaseModel.setPhase(phase.phaseIndex)
        phaseModel.setStartDate(phase.getStartTime())
        phaseModel.setEndDate(phase.getTimeLeftToFinish() if phase.isActive() else phase.getFinishTime())
        phaseModel.setStatus(STATUS_MAP.get(phase.getState(), PhaseStatus.LOCKED))
