# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/inject_component_adaptor.py
import logging
from frameworks.wulf import WindowSettings, Window, WindowStatus
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
_logger = logging.getLogger(__name__)

class InjectComponentAdaptor(BaseDAAPIComponent):
    __slots__ = ('__injected',)

    @property
    def _injectView(self):
        return self.__injected.content if self.__injected else None

    def __init__(self):
        super(InjectComponentAdaptor, self).__init__()
        self.__injected = None
        return

    def registerFlashComponent(self, component, alias, *args):
        _logger.warning('InjectComponentAdaptor %s does not support internal components', self.getAlias())

    def isFlashComponentRegistered(self, alias):
        return False

    def unregisterFlashComponent(self, alias):
        _logger.warning('InjectComponentAdaptor %s does not support internal components', self.getAlias())

    def _populate(self):
        super(InjectComponentAdaptor, self)._populate()
        self.__createInjectView()

    def _dispose(self):
        self.__destroyInjected()
        super(InjectComponentAdaptor, self)._dispose()

    def _makeInjectView(self):
        raise NotImplementedError

    def __createInjectView(self):
        if self.__injected is not None:
            _logger.error('Inject view %r is already created in component %s', self.__injected.content, self.getAlias())
            return
        else:
            view = self._makeInjectView()
            settings = WindowSettings()
            settings.content = view
            self.__injected = Window(settings)
            self.__injected.onStatusChanged += self.__onStatusChanged
            self.__injected.load()
            return

    def __destroyInjected(self, wasAdded=True):
        if self.__injected is None:
            return
        else:
            if wasAdded and self.flashObject is not None:
                self.flashObject.removeViewImpl(self.__injected.content.uniqueID)
            self.__injected.onStatusChanged -= self.__onStatusChanged
            self.__injected.destroy()
            self.__injected = None
            return

    def __addInjectView(self):
        if self.flashObject is not None:
            if not self.flashObject.addViewImpl(self.__injected.content.uniqueID):
                _logger.error('Inject view can not be added to component %s', self.getAlias())
                self.__destroyInjected(wasAdded=False)
        else:
            _logger.error('GFxValue is not created for %s', self.getAlias())
        return

    def __onStatusChanged(self, state):
        if state == WindowStatus.LOADED:
            self.__addInjectView()
        elif state == WindowStatus.DESTROYING:
            self.__destroyInjected()
