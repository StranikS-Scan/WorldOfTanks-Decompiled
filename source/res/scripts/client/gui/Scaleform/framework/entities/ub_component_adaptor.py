# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/ub_component_adaptor.py
import logging
from frameworks.wulf import ViewStatus
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
_logger = logging.getLogger(__name__)

class UnboundComponentAdaptor(BaseDAAPIComponent):
    __slots__ = ('__unbound',)

    def __init__(self):
        super(UnboundComponentAdaptor, self).__init__()
        self.__unbound = None
        return

    def registerFlashComponent(self, component, alias, *args):
        _logger.warning('UnboundComponentAdaptor %s does not support internal components', self.getAlias())

    def isFlashComponentRegistered(self, alias):
        return False

    def unregisterFlashComponent(self, alias):
        _logger.warning('UnboundComponentAdaptor %s does not support internal components', self.getAlias())

    def _populate(self):
        super(UnboundComponentAdaptor, self)._populate()
        self.__createUnboundView()

    def _dispose(self):
        self.__destroyUnboundView()
        super(UnboundComponentAdaptor, self)._dispose()

    def _makeUnboundView(self):
        raise NotImplementedError

    def __createUnboundView(self):
        if self.__unbound is not None:
            _logger.error('Unbound view %d is already created in component %s', self.__unbound.layoutID, self.getAlias())
            return
        else:
            self.__unbound = self._makeUnboundView()
            self.__unbound.onStatusChanged += self.__onStatusChanged
            self.__unbound.load()
            return

    def __destroyUnboundView(self, wasAdded=True):
        if self.__unbound is None:
            return
        else:
            if wasAdded and self.flashObject is not None:
                self.flashObject.removeUnboundView(self.__unbound.layoutID)
            self.__unbound.onStatusChanged -= self.__onStatusChanged
            self.__unbound.destroy()
            self.__unbound = None
            return

    def __addUnboundView(self):
        if self.flashObject is not None:
            if not self.flashObject.addUnboundView(self.__unbound.layoutID):
                _logger.error('Unbound view can not be added to component %s', self.getAlias())
                self.__destroyUnboundView(wasAdded=False)
        else:
            _logger.error('GFxValue is not created for %s', self.getAlias())
        return

    def __onStatusChanged(self, state):
        if state == ViewStatus.LOADED:
            self.__addUnboundView()
        elif state == ViewStatus.DESTROYED:
            self.__destroyUnboundView()
