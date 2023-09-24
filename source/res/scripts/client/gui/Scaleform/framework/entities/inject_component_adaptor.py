# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/inject_component_adaptor.py
import logging
import typing
from functools import wraps
from gui.Scaleform.daapi.view.meta.InjectComponentMeta import InjectComponentMeta
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from frameworks.wulf import ViewStatus, ViewFlags
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, Window
_logger = logging.getLogger(__name__)

def hasAliveInject(deadUnexpected=False):

    def decorator(method):

        @wraps(method)
        def wrapper(injectAdapor, *args, **kwargs):
            if injectAdapor.getInjectView() is not None:
                method(injectAdapor, *args, **kwargs)
            elif deadUnexpected:
                _logger.warning('unexpected call on adaptor %s without alive content', injectAdapor)
            return

        return wrapper

    return decorator


class InjectComponentAdaptor(InjectComponentMeta):
    __slots__ = ('__injected', '__view')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(InjectComponentAdaptor, self).__init__()
        self.__view = None
        return

    def registerFlashComponent(self, component, alias, *args):
        _logger.warning('InjectComponentAdaptor %s does not support internal components', self.getAlias())

    def isFlashComponentRegistered(self, alias):
        return False

    def unregisterFlashComponent(self, alias):
        _logger.warning('InjectComponentAdaptor %s does not support internal components', self.getAlias())

    def getInjectView(self):
        return self.__view

    @property
    def _injectView(self):
        return self.__view

    def _populate(self):
        super(InjectComponentAdaptor, self)._populate()
        self._onPopulate()

    def _onPopulate(self):
        self._createInjectView()

    def _dispose(self):
        self._destroyInjected()
        super(InjectComponentAdaptor, self)._dispose()

    def _makeInjectView(self, *args):
        raise NotImplementedError

    def _addInjectContentListeners(self):
        pass

    def _removeInjectContentListeners(self):
        pass

    def _createInjectView(self, *args):
        if not self._isDAAPIInited():
            _logger.warning('GFxValue is not created for %s', self.getAlias())
            return
        elif self.__view is not None:
            _logger.error('View %r is already created in component %s', self.__view, self.getAlias())
            return
        else:
            self.__view = self._makeInjectView(*args)
            if self.__view.viewFlags != ViewFlags.VIEW:
                _logger.error('View %r with flags %r is not supported to be injected. %r. ViewFlags.VIEW is the only supported.', self.__view, self.__view.viewFlags, self.getAlias())
                return
            self.__view.onStatusChanged += self.__onViewStatusChanged
            self._addInjectContentListeners()
            placeId = self.__view.uniqueID
            mainWindow = self.__gui.windowsManager.getMainWindow()
            mainView = mainWindow.content
            mainView.addChild(placeId, self.__view, loadImmediately=True)
            self.as_setPlaceIdS(placeId)
            return

    def _destroyInjected(self):
        if self.__view is not None:
            self._removeInjectContentListeners()
            self.__view.onStatusChanged -= self.__onViewStatusChanged
            mainWindow = self.__gui.windowsManager.getMainWindow()
            mainView = mainWindow.content
            placeId = self.__view.uniqueID
            mainView.removeChild(placeId, destroy=True)
            self.__view = None
            self.as_setPlaceIdS(0)
        return

    def __onViewStatusChanged(self, status):
        if status == ViewStatus.DESTROYED and self.__view is not None:
            _logger.info('Inject component was destroyed: %s', self.getAlias())
            self.__view = None
            self.as_setPlaceIdS(0)
        return
