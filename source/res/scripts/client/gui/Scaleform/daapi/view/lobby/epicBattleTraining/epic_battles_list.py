# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattleTraining/epic_battles_list.py
from adisp import process
from constants import PREBATTLE_TYPE
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.trainings.trainings_list_base import TrainingsListBase
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.prb_control.entities.epic_battle_training.ctx import EpicTrainingSettingsCtx
from gui.prb_control.entities.epic_battle_training.ctx import JoinEpicBattleTrainingCtx
from gui.impl import backport
from gui.impl.gen import R

class EpicBattlesList(TrainingsListBase):

    def _populate(self):
        super(EpicBattlesList, self)._populate()
        funcState = self.prbDispatcher.getFunctionalState()
        if not funcState.isInLegacy(PREBATTLE_TYPE.EPIC_TRAINING):
            g_eventDispatcher.removeEpicTrainingFromCarousel()
            return
        self.addListener(events.TrainingSettingsEvent.UPDATE_EPIC_TRAINING_SETTINGS, self._createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(events.TrainingSettingsEvent.UPDATE_EPIC_TRAINING_SETTINGS, self._createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        window = self.app.containerManager.getView(WindowLayer.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.EPIC_TRAINING_SETTINGS_WINDOW_PY})
        if window is not None:
            window.destroy()
        super(EpicBattlesList, self)._dispose()
        return

    def _getViewData(self):
        return {'title': backport.text(R.strings.menu.epicTraining.title()),
         'descr': backport.text(R.strings.menu.training.description()),
         'battleTypeID': BATTLE_TYPES.EPIC_TRAINING}

    @process
    def joinTrainingRequest(self, prbID):
        yield self.prbDispatcher.join(JoinEpicBattleTrainingCtx(prbID, waitingID='prebattle/join'))

    def createTrainingRequest(self):
        settings = EpicTrainingSettingsCtx()
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.EPIC_TRAINING_SETTINGS_WINDOW_PY), ctx={'isCreateRequest': True,
         'settings': settings}), scope=EVENT_BUS_SCOPE.LOBBY)
