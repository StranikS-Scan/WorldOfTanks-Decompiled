# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/race/racing_widget_cmp.py
import logging
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.race.race_widget_tooltip_model import RaceWidgetTooltipModel
from gui.impl.gen.view_models.views.race.racing_widget_view_model import RacingWidgetViewModel
from gui.impl.pub import ViewImpl
from gui.marathon.racing_event import RacingEvent
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from gui.marathon.marathon_constants import MARATHON_STATE
from helpers import dependency, time_utils
from skeletons.gui.game_control import IMarathonEventsController, IRacingEventController
_logger = logging.getLogger(__name__)
_COOLDOWN_UPDATE_TIMEOUT = 1
_UNDEF_VALUE_STR = '...'

class RacingWidgetComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return RacingWidgetView()


class RacingWidgetView(ViewImpl):
    _racingEventController = dependency.descriptor(IRacingEventController)
    _marathonEventsController = dependency.descriptor(IMarathonEventsController)
    __slots__ = ('__secondsNotifier',)

    def __init__(self, *args, **kwargs):
        super(RacingWidgetView, self).__init__(R.views.lobby.race.racing_widget_cmp.RacingWidgetCmp(), ViewFlags.COMPONENT, RacingWidgetViewModel, *args, **kwargs)
        self.__secondsNotifier = None
        return

    @property
    def viewModel(self):
        return super(RacingWidgetView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return RaceWidgetTooltip() if event.contentID == R.views.lobby.race.racing_widget_cmp.RaceWidgetTooltip() else super(RacingWidgetView, self).createToolTipContent(event=event, contentID=contentID)

    def _initialize(self):
        super(RacingWidgetView, self)._initialize()
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self._racingEventController.onNumRacingAttemptsChanged += self.__onNumRacingAttemptsChanged
        self._racingEventController.onMaxNumRacingAttemptsChanged += self.__onMaxNumRacingAttemptsChanged
        self.__secondsNotifier = PeriodicNotifier(self.__getNotificationDelta, self.__updateCooldown, (_COOLDOWN_UPDATE_TIMEOUT,))
        self.__secondsNotifier.startNotification()
        self.__updateModel()

    def _finalize(self):
        super(RacingWidgetView, self)._finalize()
        self._racingEventController.onMaxNumRacingAttemptsChanged -= self.__onMaxNumRacingAttemptsChanged
        self._racingEventController.onNumRacingAttemptsChanged -= self.__onNumRacingAttemptsChanged
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        self.__secondsNotifier.stopNotification()
        self.__secondsNotifier.clear()

    def __updateModel(self):
        with self.getViewModel().transaction() as model:
            maxAttempts = self._racingEventController.getMaxNumRacingAttempts()
            model.setTotalCount(str(maxAttempts) if maxAttempts != -1 else _UNDEF_VALUE_STR)
            model.setAvailableCount(str(self._racingEventController.getNumRacingAttempts()))
            self.__updateCooldown(model)

    def __onWidgetClick(self):
        if self._marathonEventsController.isAnyActive():
            showMissionsMarathon(marathonPrefix=RacingEvent.RACING_MARATHON_PREFIX)

    def __getNotificationDelta(self):
        return _COOLDOWN_UPDATE_TIMEOUT

    def __updateCooldown(self, model=None):
        if not self._racingEventController.isCooldown():
            return
        else:
            countdown = self._racingEventController.getCooldownCountdown()
            countdownStr = time_utils.getTillTimeString(countdown, '#festival:race/hangar/status/timeLeft')
            if model is not None:
                model.setTimeout(countdownStr)
            else:
                with self.getViewModel().transaction() as mdl:
                    mdl.setTimeout(countdownStr)
            return

    def __onNumRacingAttemptsChanged(self, _):
        self.__updateModel()

    def __onMaxNumRacingAttemptsChanged(self, _):
        self.__updateModel()


class RaceWidgetTooltip(ViewImpl):
    _marathonEventsController = dependency.descriptor(IMarathonEventsController)
    __slots__ = ()

    def __init__(self):
        super(RaceWidgetTooltip, self).__init__(R.views.lobby.race.racing_widget_cmp.RaceWidgetTooltip(), ViewFlags.COMPONENT, RaceWidgetTooltipModel)

    @property
    def viewModel(self):
        return super(RaceWidgetTooltip, self).getViewModel()

    def _initialize(self):
        super(RaceWidgetTooltip, self)._initialize()
        primaryMarathon = self._marathonEventsController.getMarathon(RacingEvent.RACING_MARATHON_PREFIX)
        if primaryMarathon is not None:
            remainingTime = primaryMarathon.getRemainingTime()
            with self.getViewModel().transaction() as model:
                model.setIsEventStarted(primaryMarathon.getState() == MARATHON_STATE.IN_PROGRESS)
                model.setIsEventFinished(primaryMarathon.getState() == MARATHON_STATE.FINISHED)
                model.setDays(remainingTime)
        return
