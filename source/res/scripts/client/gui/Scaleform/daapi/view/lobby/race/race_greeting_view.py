# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/race/race_greeting_view.py
import logging
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.race.race_greeting_view_model import RaceGreetingViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController, IRacingEventController
from skeletons.gui.app_loader import IAppLoader
from gui.marathon.racing_event import RacingEvent, RacingEventAddPath
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
_logger = logging.getLogger(__name__)

class RaceGreetingInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return RaceGreetingView()


class RaceGreetingView(ViewImpl):
    _racingEventController = dependency.descriptor(IRacingEventController)
    _appLoader = dependency.descriptor(IAppLoader)
    _marathonEventsController = dependency.descriptor(IMarathonEventsController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(RaceGreetingView, self).__init__(R.views.lobby.race.race_greeting_view.RaceGreetingView(), ViewFlags.COMPONENT, RaceGreetingViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(RaceGreetingView, self).getViewModel()

    def _initialize(self):
        super(RaceGreetingView, self)._initialize()
        self.viewModel.onUserProgressionOpen += self.__onUserProgressionOpen
        self.viewModel.onRaceInfoOpen += self.__onRaceInfoOpen

    def _finalize(self):
        super(RaceGreetingView, self)._finalize()
        self.viewModel.onUserProgressionOpen -= self.__onUserProgressionOpen
        self.viewModel.onRaceInfoOpen -= self.__onRaceInfoOpen

    def __onUserProgressionOpen(self):
        self.__navigateTo(RacingEventAddPath.PROGRESS)

    def __onRaceInfoOpen(self):
        self.__navigateTo(RacingEventAddPath.INFO)

    def __navigateTo(self, racingEventAddPath):
        marathonEvent = self._marathonEventsController.getMarathon(RacingEvent.RACING_MARATHON_PREFIX)
        marathonEvent.setAdditionalPath(racingEventAddPath)
        app = self._appLoader.getApp()
        cm = app.containerManager
        viewKey = ViewKey(VIEW_ALIAS.LOBBY_MISSIONS)
        missionPage = cm.getViewByKey(viewKey)
        if missionPage is not None:
            missonView = missionPage.currentTab
            if missonView is not None:
                missonView.reload(missonView.setUnboundInjVisible)
        return
