# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/navigation_view_impl.py
import logging
import typing
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment import getViews
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher, g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showDetachmentViewById, showAssignDetachmentToVehicleView
from gui.hangar_cameras.hangar_camera_switch_mixin import HangarCameraSwitchMixin
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
if typing.TYPE_CHECKING:
    from gui.prb_control.items import PlayerUnitInfo
_logger = logging.getLogger(__name__)

class NavigationViewImpl(ViewImpl, HangarCameraSwitchMixin):
    __slots__ = ('_views', '_topMenuVisibility', '_navigationViewSettings')
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    _CLOSE_IN_PREBATTLE = False
    _DISABLE_CAMERA_MOVEMENT = False

    def __init__(self, settings, topMenuVisibility=False, ctx=None):
        super(NavigationViewImpl, self).__init__(settings)
        self._views = getViews()
        self._topMenuVisibility = topMenuVisibility
        if ctx is None:
            ctx = {}
        self.__fillNavigationSettings(ctx)
        return

    @property
    def viewModel(self):
        return super(NavigationViewImpl, self).getViewModel()

    def isParamsEqual(self, ctx):
        return True

    @property
    def _currentViewId(self):
        return self._navigationViewSettings.getViewId()

    def _initialize(self):
        super(NavigationViewImpl, self)._initialize()
        state = HeaderMenuVisibilityState.ALL if self._topMenuVisibility is True else HeaderMenuVisibilityState.NOTHING
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), scope=EVENT_BUS_SCOPE.LOBBY)
        if self._DISABLE_CAMERA_MOVEMENT:
            self.disableCamera()
        self._addListeners()

    def _finalize(self):
        super(NavigationViewImpl, self)._finalize()
        self._removeListeners()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)
        if self._DISABLE_CAMERA_MOVEMENT:
            self.restoreCamera()

    def _initModel(self, vm):
        vm.setCurrentViewId(self._currentViewId)
        if self._navigationViewSettings.getPreviousViewSettings():
            previousViewId = self._navigationViewSettings.getPreviousViewSettings().getViewId()
            vm.setPreviousViewId(previousViewId)

    def _onLoading(self, *args, **kwargs):
        super(NavigationViewImpl, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self._initModel(model)

    def _onLoadPage(self, args=None):
        if args is None:
            self._onClose()
        else:
            self._showDetachmentView(args['viewId'], args)
        return

    def _onClose(self):
        self.__goToHangar()

    def _onBackUntil(self, viewId):
        currentViewSettings = self._navigationViewSettings
        while currentViewSettings.getViewId() is not viewId:
            currentViewSettings = currentViewSettings.getPreviousViewSettings()
            if currentViewSettings is None:
                self._onClose()
                return

        showDetachmentViewById(viewId, currentViewSettings.getViewContextSettings(), currentViewSettings.getPreviousViewSettings())
        return

    def _onBack(self):
        navigationViewSettings = self._navigationViewSettings.getPreviousViewSettings()
        if navigationViewSettings is None:
            return self._onClose()
        else:
            viewId = navigationViewSettings.getViewId()
            viewContextSettings = navigationViewSettings.getViewContextSettings()
            if viewId is NavigationViewModel.ASSIGN_TO_VEHICLE or viewId is NavigationViewModel.NO_DETACHMENT:
                vehicleInvId = viewContextSettings['vehicleInvID']
                showAssignDetachmentToVehicleView(vehicleInvId)
            else:
                showDetachmentViewById(viewId, viewContextSettings, navigationViewSettings.getPreviousViewSettings())
            return

    def _showDetachmentView(self, viewId, viewContextSettings):
        showDetachmentViewById(viewId, viewContextSettings, self._navigationViewSettings)

    def _addListeners(self):
        self.viewModel.onClose += self._onClose
        self.viewModel.onLoadPage += self._onLoadPage
        self.viewModel.onBack += self._onBack
        self.__platoonCtrl.onMembersUpdate += self.__updateMembersHandler

    def _removeListeners(self):
        self.viewModel.onClose -= self._onClose
        self.viewModel.onLoadPage -= self._onLoadPage
        self.viewModel.onBack -= self._onBack
        self.__platoonCtrl.onMembersUpdate -= self.__updateMembersHandler

    def __goToHangar(self):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)
        event_dispatcher.showHangar()

    def __updateMembersHandler(self):
        playerInfo = self.__platoonCtrl.getPlayerInfo()
        if self._CLOSE_IN_PREBATTLE and playerInfo and playerInfo.isReady and not playerInfo.isInQueue():
            self._onClose()

    def __fillNavigationSettings(self, ctx):
        settings = ctx.get('navigationViewSettings', None)
        self._navigationViewSettings = settings
        return
