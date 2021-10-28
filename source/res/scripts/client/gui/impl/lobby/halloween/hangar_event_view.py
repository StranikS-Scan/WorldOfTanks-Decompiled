# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/hangar_event_view.py
from gui.impl.pub import ViewImpl
from gui.impl.lobby.halloween.event_helpers import isEvent
from gui.prb_control.entities.maps_training.pre_queue.entity import MapsTrainingEntity
from gui.shared.event_dispatcher import showHangar
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from CurrentVehicle import g_currentPreviewVehicle
from gui.prb_control.entities.epic_battle_training.entity import EpicBattleTrainingIntroEntity
from gui.prb_control.entities.training.legacy.entity import TrainingIntroEntity

class HangarEventView(ViewImpl, IGlobalListener):

    def __init__(self, settings):
        super(HangarEventView, self).__init__(settings)
        self.startGlobalListening()

    def _onLoading(self):
        super(HangarEventView, self)._onLoading()
        self.updateHeaderMenu(HeaderMenuVisibilityState.NOTHING)

    def _finalize(self):
        self.stopGlobalListening()
        self.updateHeaderMenu(HeaderMenuVisibilityState.ALL)
        super(HangarEventView, self)._finalize()

    def onPrbEntitySwitched(self):
        if not isinstance(self.prbEntity, (EpicBattleTrainingIntroEntity, TrainingIntroEntity)):
            showHangar()
        if not isEvent() and g_currentPreviewVehicle.isPresent():
            g_currentPreviewVehicle.selectNoVehicle()

    def updateHeaderMenu(self, state):
        if isinstance(self.prbEntity, MapsTrainingEntity):
            return
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), scope=EVENT_BUS_SCOPE.LOBBY)
