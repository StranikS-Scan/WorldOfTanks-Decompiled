# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/battle_context_hints/hint_inject_component.py
import logging
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
_logger = logging.getLogger(__name__)

class HintInjectComponent(InjectComponentAdaptor):

    def _populate(self):
        super(HintInjectComponent, self)._populate()
        self.hideHint()

    def _onPopulate(self):
        raise NotImplementedError

    def setInjectView(self, viewClass):
        if not isinstance(self.getInjectView(), viewClass):
            self._destroyInjected()
            self._createInjectView(viewClass)

    def showHint(self, *args):
        raise NotImplementedError

    def hideHint(self):
        raise NotImplementedError

    def _makeInjectView(self, viewClass):
        _logger.debug('[BATTLE_CONTEXT_INTS] HintInjectComponent._makeInjectView componentClass=%s', viewClass)
        return viewClass()
