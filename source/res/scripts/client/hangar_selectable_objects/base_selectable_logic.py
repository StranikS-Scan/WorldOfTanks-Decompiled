# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_selectable_objects/base_selectable_logic.py
import logging
import weakref
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from .interfaces import ISelectableLogic, ISelectableLogicCallback
_logger = logging.getLogger(__name__)

class BaseSelectableLogic(ISelectableLogic):
    __slots__ = ('__callbackRef',)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(BaseSelectableLogic, self).__init__()
        self.__callbackRef = None
        return

    def init(self, callback=None):
        if isinstance(callback, ISelectableLogicCallback):
            self.__callbackRef = weakref.ref(callback)
        elif callback is not None:
            _logger.warning('Callback must be an instance of the ISelectableLogicCallback.')
        self._hangarSpace.onMouseEnter += self._onMouseEnter
        self._hangarSpace.onMouseExit += self._onMouseExit
        self._hangarSpace.onMouseDown += self._onMouseDown
        self._hangarSpace.onMouseUp += self._onMouseUp
        self._hangarSpace.onNotifyCursorOver3dScene += self._onNotifyCursorOver3dScene
        return

    def fini(self):
        self.__callbackRef = None
        self._hangarSpace.onMouseEnter -= self._onMouseEnter
        self._hangarSpace.onMouseExit -= self._onMouseExit
        self._hangarSpace.onMouseDown -= self._onMouseDown
        self._hangarSpace.onMouseUp -= self._onMouseUp
        self._hangarSpace.onNotifyCursorOver3dScene -= self._onNotifyCursorOver3dScene
        return

    def _onNotifyCursorOver3dScene(self, isCursorOver3dScene):
        pass

    def _onMouseEnter(self, entity):
        pass

    def _onMouseExit(self, entity):
        pass

    def _onMouseDown(self):
        pass

    def _onMouseUp(self):
        pass

    def _filterEntity(self, entity):
        return True

    def _callbackMethodCall(self, methodName, *args, **kwargs):
        if self.__callbackRef is None:
            return
        else:
            callback = self.__callbackRef()
            if callback is None:
                return
            try:
                return getattr(callback, methodName)(*args, **kwargs)
            except AttributeError:
                pass

            return
