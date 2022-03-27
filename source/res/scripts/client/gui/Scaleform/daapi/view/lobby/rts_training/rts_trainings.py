# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rts_training/rts_trainings.py
from adisp import process
from constants import PREBATTLE_TYPE
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.trainings.trainings_list_base import TrainingsListBase
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.rts_battles_training.ctx import JoinRtsTrainingCtx
from gui.prb_control.entities.rts_battles_training.ctx import RtsTrainingSettingsCtx
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.impl import backport
from gui.impl.gen import R

class RtsTrainings(TrainingsListBase):

    def _populate(self):
        super(RtsTrainings, self)._populate()
        if self.prbDispatcher:
            funcState = self.prbDispatcher.getFunctionalState()
            if not funcState.isInLegacy(PREBATTLE_TYPE.RTS_TRAINING):
                g_eventDispatcher.removeTrainingFromCarousel()
                return
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self._createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self._createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        window = self.app.containerManager.getView(WindowLayer.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.RTS_TRAINING_SETTINGS_WINDOW_PY})
        if window is not None:
            window.destroy()
        super(RtsTrainings, self)._dispose()
        return

    def _getViewData(self):
        return {'title': backport.text(R.strings.menu.training.title()),
         'descr': backport.text(R.strings.menu.training.description()),
         'battleTypeID': BATTLE_TYPES.RTS_TRAINING}

    @process
    def joinTrainingRequest(self, prbID):
        yield self.prbDispatcher.join(JoinRtsTrainingCtx(prbID, waitingID='prebattle/join'))

    def createTrainingRequest(self):
        settings = RtsTrainingSettingsCtx()
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.RTS_TRAINING_SETTINGS_WINDOW_PY), ctx={'isCreateRequest': True,
         'settings': settings}), scope=EVENT_BUS_SCOPE.LOBBY)
