# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/base_overlay_view.py
import BigWorld
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen.view_models.views.lobby.account_completion.common.curtain_template_model import CurtainTemplateModel
from gui.impl.lobby.account_completion.base_view import BaseView
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.game_control import ISteamRegistrationOverlay
_CLOSING_ANIMATION_TIME = 0.5

class BaseOverlayView(BaseView, IGlobalListener):
    __slots__ = ('_fadeAnimation', '_callbackID')
    _overlay = dependency.descriptor(ISteamRegistrationOverlay)

    def __init__(self, settings, fadeAnimation=False):
        super(BaseOverlayView, self).__init__(settings)
        self._fadeAnimation = fadeAnimation
        self._callbackID = None
        return

    @property
    def viewModel(self):
        return super(BaseOverlayView, self).getViewModel()

    def destroyWindow(self, offOverlay=True):
        if self._callbackID is not None:
            BigWorld.cancelCallback(self._callbackID)
            self._callbackID = None
        if offOverlay:
            self._overlay.setOverlayState(False)
        super(BaseOverlayView, self).destroyWindow()
        return

    def onUnitFlagsChanged(self, flags, timeLeft):
        if flags.isInQueue():
            self._onCancel()

    def _initialize(self, *args, **kwargs):
        self.startGlobalListening()
        if not self._fadeAnimation:
            self._overlay.setOverlayState(True)
        super(BaseOverlayView, self)._initialize(*args, **kwargs)

    def _finalize(self):
        super(BaseOverlayView, self)._finalize()
        self.stopGlobalListening()

    def _addListeners(self):
        super(BaseOverlayView, self)._addListeners()
        self.viewModel.onMoveSpace += self._onMoveSpace

    def _removeListeners(self):
        self.viewModel.onMoveSpace -= self._onMoveSpace
        super(BaseOverlayView, self)._removeListeners()

    def _fillModel(self, model):
        super(BaseOverlayView, self)._fillModel(model)
        self._setAnimationToModel(model, isFade=self._fadeAnimation, isShow=True)

    def _setAnimation(self, isFade=True, isShow=True):
        with self.viewModel.transaction() as model:
            self._setAnimationToModel(model, isFade=isFade, isShow=isShow)

    @staticmethod
    def _setAnimationToModel(model, isFade=True, isShow=True):
        model.setIsFade(isFade)
        model.setIsShow(isShow)

    def _onCancel(self):
        if self._callbackID is None:
            self._setAnimation(isFade=False, isShow=False)
            self._overlay.setOverlayState(False)
            self._callbackID = BigWorld.callback(_CLOSING_ANIMATION_TIME, self._onCancelCallback)
        return

    def _onCancelCallback(self):
        self._callbackID = None
        self.destroyWindow(False)
        return

    @staticmethod
    def _onMoveSpace(args=None):
        if args is None:
            return
        else:
            ctx = {'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            return
