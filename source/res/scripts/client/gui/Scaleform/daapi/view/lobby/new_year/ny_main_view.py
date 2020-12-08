# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/new_year/ny_main_view.py
import logging
from functools import partial
import typing
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.meta.NYMainViewMeta import NYMainViewMeta
from gui.Scaleform.genConsts.NY_CONSTS import NY_CONSTS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.new_year.navigation import ViewTypes, NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.shared.events import LobbyHeaderMenuEvent
from helpers import dependency, uniprof
from new_year.custom_selectable_logic import PianoSelectableLogic, IciclesSelectableLogic
from skeletons.new_year import INewYearController, ITalismanSceneController, ICelebritySceneController
if typing.TYPE_CHECKING:
    from hangar_selectable_objects import HangarSelectableLogic
    from gui.shared.event_dispatcher import NYViewCtx
_logger = logging.getLogger(__name__)

class _ViewStatus(object):
    OPENED = 0
    CLOSED = 1
    SWITCHING = 2


class NYMainView(NYMainViewMeta):
    _nyController = dependency.descriptor(INewYearController)
    _talismanCtrl = dependency.descriptor(ITalismanSceneController)
    _celebrityController = dependency.descriptor(ICelebritySceneController)

    def __init__(self, ctx):
        super(NYMainView, self).__init__()
        self.__selectableLogic = ()
        self.__ctx = ctx
        self.__onSwitchViewCallback = None
        self.__viewStatus = _ViewStatus.CLOSED
        return

    @property
    def isViewOpened(self):
        return self.__viewStatus == _ViewStatus.OPENED

    def onEscPress(self):
        if self._talismanCtrl.isInPreview():
            return
        if self._celebrityController.isInChallengeView and not self._celebrityController.isChallengeVisited:
            self._celebrityController.onExitIntroScreen()
            return
        NewYearNavigation.closeMainView()

    def onSwitchView(self):
        self.__viewStatus = _ViewStatus.OPENED
        if self.__onSwitchViewCallback is not None:
            self.__onSwitchViewCallback()
            self.__onSwitchViewCallback = None
        return

    def registerFlashComponent(self, component, alias, *args, **kwargs):
        super(NYMainView, self).registerFlashComponent(component, alias, ctx=self.__ctx)

    @uniprof.regionDecorator(label='ny.mainView', scope='enter')
    def _populate(self):
        super(NYMainView, self)._populate()
        self.__selectableLogic = (PianoSelectableLogic(), IciclesSelectableLogic())
        for selectableLogic in self.__selectableLogic:
            selectableLogic.init()

        g_eventBus.addListener(events.NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)
        self._nyController.onStateChanged += self.__onStateChanged
        NewYearSoundsManager.setHangarPlaceGarage()
        if self.__ctx is not None:
            self.__switchInjectComponent(self.__ctx.viewParams)
        else:
            _logger.error('Missing viewContext for NewYear MainView.')
        return

    @uniprof.regionDecorator(label='ny.mainView', scope='exit')
    def _dispose(self):
        self.__viewStatus = _ViewStatus.CLOSED
        self.__onSwitchViewCallback = None
        for selectableLogic in self.__selectableLogic:
            selectableLogic.fini()

        self.__selectableLogic = ()
        g_eventBus.removeListener(events.NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self._nyController.onStateChanged -= self.__onStateChanged
        super(NYMainView, self)._dispose()
        NewYearNavigation.clearCache()
        return

    def __onPreSwitchViewEvent(self, event):
        ctx = event.ctx
        viewParams = ctx.viewParams
        self.__onSwitchViewCallback = self.__getViewSwitchCallback(ctx)
        if self.__isViewAlreadySelected(viewParams):
            self.onSwitchView()
        else:
            self.__switchInjectComponent(viewParams)
        self.__ctx = ctx

    def __switchInjectComponent(self, viewParams):
        viewType = viewParams.type
        injectType = NY_CONSTS.NY_MAIN_GF_INJECT if viewType == ViewTypes.GAMEFACE else NY_CONSTS.NY_MAIN_UB_INJECT
        self.__viewStatus = _ViewStatus.SWITCHING
        self.as_switchViewS(injectType)

    def __isViewAlreadySelected(self, viewParams):
        return False if self.__ctx is None else self.__ctx.viewParams == viewParams

    def __onStateChanged(self):
        if not self._nyController.isEnabled():
            if not self.app.fadeManager.isInFade():
                self.onEscPress()
            else:
                showHangar()

    @staticmethod
    def __getViewSwitchCallback(ctx):
        event = events.NewYearEvent(events.NewYearEvent.ON_SWITCH_VIEW, ctx=ctx)
        return partial(g_eventBus.handleEvent, event=event, scope=EVENT_BUS_SCOPE.LOBBY)
