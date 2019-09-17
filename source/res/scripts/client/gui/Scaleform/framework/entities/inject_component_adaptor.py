# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/inject_component_adaptor.py
import logging
from frameworks.wulf import ViewStatus
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
_logger = logging.getLogger(__name__)

class InjectComponentAdaptor(BaseDAAPIComponent):
    __slots__ = ('__injectView',)

    def __init__(self):
        super(InjectComponentAdaptor, self).__init__()
        self.__injectView = None
        return

    def registerFlashComponent(self, component, alias, *args):
        _logger.warning('InjectComponentAdaptor %s does not support internal components', self.getAlias())

    def isFlashComponentRegistered(self, alias):
        return False

    def unregisterFlashComponent(self, alias):
        _logger.warning('InjectComponentAdaptor %s does not support internal components', self.getAlias())

    def setParentId(self, parentId):
        if self.__injectView:
            self.__injectView.setParentId(parentId)
        else:
            _logger.error("View for inject component doesn't exist")

    def _populate(self):
        super(InjectComponentAdaptor, self)._populate()
        self.__createInjectView()

    def _dispose(self):
        self.__destroyInjectView()
        super(InjectComponentAdaptor, self)._dispose()

    def _makeInjectView(self):
        raise NotImplementedError

    def __createInjectView(self):
        if self.__injectView is not None:
            _logger.error('Inject view %r is already created in component %s', self.__injectView, self.getAlias())
            return
        else:
            self.__injectView = self._makeInjectView()
            self.__injectView.onStatusChanged += self.__onStatusChanged
            self.__injectView.load()
            return

    def __destroyInjectView(self, wasAdded=True):
        if self.__injectView is None:
            return
        else:
            if wasAdded and self.flashObject is not None:
                self.flashObject.removeViewImpl(self.__injectView.uniqueID)
            self.__injectView.onStatusChanged -= self.__onStatusChanged
            self.__injectView.destroy()
            self.__injectView = None
            return

    def __addInjectView(self):
        if self.flashObject is not None:
            if not self.flashObject.addViewImpl(self.__injectView.uniqueID):
                _logger.error('Inject view can not be added to component %s', self.getAlias())
                self.__destroyInjectView(wasAdded=False)
        else:
            _logger.error('GFxValue is not created for %s', self.getAlias())
        return

    def __onStatusChanged(self, state):
        if state == ViewStatus.LOADED:
            self.__addInjectView()
        elif state == ViewStatus.DESTROYED:
            self.__destroyInjectView()
