# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/battle_context_hints/sixth_sense_hint_inject_component.py
import logging
from gui.Scaleform.daapi.view.meta.SixthSenseContextHintMeta import SixthSenseContextHintMeta
from gui.impl.battle.battle_page.battle_context_hints.sixth_sense_context_hint_view import SixthSenseContextHintView
_logger = logging.getLogger(__name__)

class SixthSenseHintInjectComponent(SixthSenseContextHintMeta):

    def _onPopulate(self):
        _logger.debug('[BATTLE_CONTEXT_INTS] SixthSenseHintInjectComponent._onPopulate')
        self._createInjectView(SixthSenseContextHintView)

    def showHint(self, *args):
        _logger.debug('[BATTLE_CONTEXT_INTS] SixthSenseHintInjectComponent.showHint')
        self.setVisibility(True)

    def hideHint(self):
        self.setVisibility(False)
        _logger.debug('[BATTLE_CONTEXT_INTS] SixthSenseHintInjectComponent.hideHint')

    def setVisibility(self, visible):
        self.as_setVisibilityS(visible)
