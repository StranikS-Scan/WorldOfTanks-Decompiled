# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/curtain/curtain_view.py
import typing
from bootcamp.Bootcamp import g_bootcamp
from frameworks.wulf import ViewSettings
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.curtain.curtain_view_model import CurtainViewModel, CurtainStateEnum
from gui.impl.lobby.account_completion.curtain.curtain_base_sub_view import CurtainBaseSubView
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogFlags
from gui.impl.pub.lobby_window import LobbyWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IOverlayController, IBootcampController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearTutorialController
if typing.TYPE_CHECKING:
    from typing import Optional, Type, Dict
_DYN_ACCESSOR = R.views.lobby.account_completion.CurtainView

class CurtainView(ViewImpl, IGlobalListener):
    __slots__ = ('_subViews', '_activeSubView')
    _overlay = dependency.descriptor(IOverlayController)
    _nyTutorController = dependency.descriptor(INewYearTutorialController)

    def __init__(self):
        settings = ViewSettings(_DYN_ACCESSOR())
        settings.model = CurtainViewModel()
        super(CurtainView, self).__init__(settings)
        self._subViews = dict()
        self._activeSubView = None
        return

    @property
    def viewModel(self):
        return super(CurtainView, self).getViewModel()

    @property
    def activeSubView(self):
        return self._activeSubView

    def _onLoading(self, *args, **kwargs):
        super(CurtainView, self)._onLoading(*args, **kwargs)
        self.viewModel.setState(CurtainStateEnum.CLOSED)

    def _onLoaded(self, *args, **kwargs):
        super(CurtainView, self)._onLoaded(*args, **kwargs)
        self.startGlobalListening()
        self.viewModel.onStateTransitionComplete += self._stateTransitionCompleteHandler
        self.viewModel.onMoveSpace += self._moveSpaceHandler
        self._overlay.setOverlayState(True)

    def _finalize(self):
        self.viewModel.onStateTransitionComplete -= self._stateTransitionCompleteHandler
        self.viewModel.onMoveSpace -= self._moveSpaceHandler
        self.stopGlobalListening()
        self._subViews.clear()
        if self._activeSubView:
            self._deactivateSubView(self._activeSubView)
            self._activeSubView = None
        self._overlay.setOverlayState(False)
        self._nyTutorController.overlayStateChanged()
        super(CurtainView, self)._finalize()
        return

    def setActiveSubView(self, subViewClass, *args, **kwargs):
        if isinstance(self._activeSubView, subViewClass):
            return
        else:
            instance = self._subViews.get(subViewClass)
            if instance is None:
                instance = self._subViews[subViewClass] = subViewClass()
                self.setChildView(instance.layoutID, instance)
            self._activateSubView(instance, *args, **kwargs)
            return

    def onUnitFlagsChanged(self, flags, timeLeft):
        if flags.isInQueue():
            self.close()

    def close(self):
        if self.viewModel.getState() == CurtainStateEnum.HIDDEN:
            self.viewModel.setState(CurtainStateEnum.CLOSED)
            self.destroyWindow()
        else:
            self.viewModel.setState(CurtainStateEnum.CLOSING)

    def hide(self):
        self.viewModel.setState(CurtainStateEnum.HIDING)
        if self._activeSubView:
            self._activeSubView.hide()

    def reveal(self):
        self.viewModel.setState(CurtainStateEnum.REVEALING)
        if self._activeSubView:
            self._activeSubView.reveal()

    def _activateSubView(self, subView, *args, **kwargs):
        if self._activeSubView == subView:
            return
        if self._activeSubView:
            self._deactivateSubView(self._activeSubView)
        if not subView:
            return
        subView.activate(*args, **kwargs)
        subView.onWaitingChanged += self._waitingChangedHandler
        self._waitingChangedHandler(subView.isWaitingVisible, subView.waitingMsgResID)
        if self.viewModel.getState() in (CurtainStateEnum.HIDING, CurtainStateEnum.HIDDEN):
            subView.reveal()
        self._activeSubView = subView
        self.viewModel.setCurrentSubViewID(subView.layoutID)
        currentState = self.viewModel.getState()
        if currentState == CurtainStateEnum.CLOSED:
            self.viewModel.setState(CurtainStateEnum.OPENING)
        if currentState == CurtainStateEnum.HIDDEN:
            self.viewModel.setState(CurtainStateEnum.REVEALING)

    def _deactivateSubView(self, subView):
        subView.deactivate()
        if self._activeSubView == subView:
            subView.onWaitingChanged -= self._waitingChangedHandler
            self._activeSubView = None
        return

    def _stateTransitionCompleteHandler(self):
        currentState = self.viewModel.getState()
        if currentState == CurtainStateEnum.OPENING:
            self.viewModel.setState(CurtainStateEnum.OPENED)
        elif currentState == CurtainStateEnum.CLOSING:
            self.viewModel.setState(CurtainStateEnum.CLOSED)
            self.destroyWindow()
        elif currentState == CurtainStateEnum.HIDING:
            self.viewModel.setState(CurtainStateEnum.HIDDEN)
        elif currentState == CurtainStateEnum.REVEALING:
            self.viewModel.setState(CurtainStateEnum.OPENED)

    def _waitingChangedHandler(self, isVisible, msgResID=R.invalid()):
        with self.viewModel.transaction() as model:
            model.setIsWaiting(isVisible)
            model.setWaitingText(msgResID)

    @staticmethod
    def _moveSpaceHandler(args=None):
        if args is None:
            return
        else:
            ctx = {'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            return


class BootcampCurtainView(CurtainView):
    _itemsCache = dependency.descriptor(IItemsCache)

    def _onLoaded(self, *args, **kwargs):
        super(BootcampCurtainView, self)._onLoaded(*args, **kwargs)
        invVehs = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
        if not invVehs:
            g_bootcamp.previewNation(g_bootcamp.nation)


class CurtainWindow(LobbyWindow):
    __slots__ = ()
    guiLoader = dependency.descriptor(IGuiLoader)
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        view = BootcampCurtainView() if self.bootcampController.isInBootcampAccount() else CurtainView()
        super(CurtainWindow, self).__init__(wndFlags=DialogFlags.TOP_FULLSCREEN_WINDOW, content=view)

    @property
    def content(self):
        return super(CurtainWindow, self).content

    def setSubView(self, subViewClass, *args, **kwargs):
        self.content.setActiveSubView(subViewClass, *args, **kwargs)

    def close(self):
        self.content.close()

    def hide(self):
        self.content.hide()

    def reveal(self):
        self.content.reveal()

    @staticmethod
    def getOpenedCurtainView():
        return CurtainWindow.guiLoader.windowsManager.getViewByLayoutID(_DYN_ACCESSOR())

    @staticmethod
    def getInstance():
        view = CurtainWindow.getOpenedCurtainView()
        if view:
            return view.getParentWindow()
        window = CurtainWindow()
        window.load()
        return window

    @staticmethod
    def isOpened():
        return bool(CurtainWindow.getOpenedCurtainView())

    @staticmethod
    def getActiveSubView():
        curtainView = CurtainWindow.getOpenedCurtainView()
        return curtainView.activeSubView if curtainView else None
