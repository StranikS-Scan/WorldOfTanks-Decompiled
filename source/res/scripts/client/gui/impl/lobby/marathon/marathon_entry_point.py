# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/marathon/marathon_entry_point.py
import time
from adisp import process
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.marathon.marathon_entry_point_model import MarathonEntryPointModel
from gui.marathon.marathon_constants import MarathonState
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController
from skeletons.gui.server_events import IEventsCache
from helpers.time_utils import ONE_DAY, ONE_HOUR
from gui.impl import backport
_MARATHON_PREFIX = 'moon_marathon'

@dependency.replace_none_kwargs(marathonsCtrl=IMarathonEventsController)
def isMarathonEntryPointAvailable(marathonsCtrl=None):
    marathonEvent = marathonsCtrl.getMarathon(_MARATHON_PREFIX)
    return marathonEvent is not None and not marathonEvent.isRewardObtained()


class MarathonEntryPoint(ViewImpl):
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.marathon.EntryPoint())
        settings.flags = flags
        settings.model = MarathonEntryPointModel()
        super(MarathonEntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MarathonEntryPoint, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(MarathonEntryPoint, self)._initialize(*args, **kwargs)
        self.viewModel.onClick += self.__onClick
        self._marathonsCtrl.onFlagUpdateNotify += self.__updateViewModel
        self._marathonsCtrl.onMarathonDataChanged += self.__onDataChanged

    def _finalize(self):
        super(MarathonEntryPoint, self)._finalize()
        self.viewModel.onClick -= self.__onClick
        self._marathonsCtrl.onFlagUpdateNotify -= self.__updateViewModel
        self._marathonsCtrl.onMarathonDataChanged -= self.__onDataChanged

    def _onLoading(self, *args, **kwargs):
        super(MarathonEntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __onDataChanged(self, marathonPrefix):
        if marathonPrefix == _MARATHON_PREFIX:
            self.__updateViewModel()

    def __updateViewModel(self):
        if isMarathonEntryPointAvailable():
            marathonEvent = self._marathonsCtrl.getMarathon(_MARATHON_PREFIX)
            with self.viewModel.transaction() as tx:
                state = marathonEvent.getState()
                currentPhase, _ = marathonEvent.getMarathonProgress()
                timeTillNextState = marathonEvent.getClosestStatusUpdateTime()
                if state in MarathonState.DISABLED_STATE:
                    state = MarathonEntryPointModel.STATE_MARATHON_DISABLED
                tx.setState(state)
                tx.setTimeTillNextState(timeTillNextState)
                tx.setFormattedTimeTillNextState(self.__getFormattedTillTimeString(timeTillNextState, marathonEvent))
                tx.setCurrentPhase(currentPhase)
                tx.setRewardObtained(marathonEvent.isRewardObtained())
                tx.setDiscount(marathonEvent.getMarathonDiscount())
        else:
            self.destroy()

    def __onClick(self):
        marathonEvent = self._marathonsCtrl.getMarathon(_MARATHON_PREFIX)
        if marathonEvent is None:
            return
        elif marathonEvent.isRewardObtained() or marathonEvent.getState() != MarathonState.FINISHED:
            showMissionsMarathon(marathonEvent.prefix)
            return
        else:
            self.__purchasePackage(marathonEvent)
            return

    @process
    def __purchasePackage(self, marathonEvent):
        url = yield marathonEvent.getMarathonVehicleUrl()
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, url=url))

    def __getFormattedTillTimeString(self, timeValue, marathonEvent):
        gmtime = time.gmtime(timeValue)
        if timeValue >= ONE_DAY:
            text = backport.text(marathonEvent.entryTooltip.daysShort, value=str(gmtime.tm_yday))
        elif timeValue >= ONE_HOUR:
            text = backport.text(marathonEvent.entryTooltip.hoursShort, value=str(gmtime.tm_hour + 1))
        else:
            text = backport.text(marathonEvent.entryTooltip.minutesShort, value=str(gmtime.tm_min + 1))
        return text
