# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/Trainings.py
from adisp import adisp_process
from constants import PREBATTLE_TYPE
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.trainings.trainings_list_base import TrainingsListBase
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES
from gui.Scaleform.genConsts.MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES import MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.training.legacy.ctx import JoinTrainingCtx
from gui.prb_control.entities.training.legacy.ctx import TrainingSettingsCtx
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.events import ChannelCarouselEvent
from messenger.ext import channel_num_gen
from messenger.ext.channel_num_gen import SPECIAL_CLIENT_WINDOWS

class Trainings(TrainingsListBase):

    def _populate(self):
        super(Trainings, self)._populate()
        if self.prbDispatcher:
            funcState = self.prbDispatcher.getFunctionalState()
            if not funcState.isInLegacy(PREBATTLE_TYPE.TRAINING):
                g_eventDispatcher.removeTrainingFromCarousel()
                return
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self._createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__updateWindowOpenState(True)

    def _dispose(self):
        self.removeListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self._createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        window = self.app.containerManager.getView(WindowLayer.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY})
        if window is not None:
            window.destroy()
        self.__updateWindowOpenState(False)
        super(Trainings, self)._dispose()
        return

    def _getViewData(self):
        return {'title': backport.text(R.strings.menu.training.title()),
         'descr': backport.text(R.strings.menu.training.description()),
         'battleTypeID': BATTLE_TYPES.TRAINING}

    @adisp_process
    def joinTrainingRequest(self, prbID):
        yield self.prbDispatcher.join(JoinTrainingCtx(prbID, waitingID='prebattle/join'))

    def createTrainingRequest(self):
        settings = TrainingSettingsCtx()
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY), ctx={'isCreateRequest': True,
         'settings': settings}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateWindowOpenState(self, flag):
        g_eventBus.handleEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.ON_WINDOW_CHANGE_OPEN_STATE, channel_num_gen.getClientID4SpecialWindow(SPECIAL_CLIENT_WINDOWS.TRAINING_LIST), MESSENGER_CHANNEL_CAROUSEL_ITEM_TYPES.CHANNEL_CAROUSEL_ITEM_TYPE_PREBATTLE, flag), scope=EVENT_BUS_SCOPE.LOBBY)
