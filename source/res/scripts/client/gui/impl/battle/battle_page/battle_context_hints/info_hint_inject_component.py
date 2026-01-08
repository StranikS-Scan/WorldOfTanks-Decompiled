# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/battle_context_hints/info_hint_inject_component.py
import logging
from gui.Scaleform.daapi.view.meta.InfoBattleContextHintMeta import InfoBattleContextHintMeta
from gui.impl.battle.battle_page.battle_context_hints.info_battle_context_hint_view import InfoBattleContextHintView
_logger = logging.getLogger(__name__)

class InfoHintInjectComponent(InfoBattleContextHintMeta):

    def _onPopulate(self):
        _logger.debug('[BATTLE_CONTEXT_INTS] InfoHintInjectComponent._onPopulate')
        self._createInjectView(InfoBattleContextHintView)

    def showHint(self, *args):
        _logger.debug('[BATTLE_CONTEXT_INTS] InfoHintInjectComponent.showHint')
        self.setVisibility(True)

    def hideHint(self):
        self.setVisibility(False)
        _logger.debug('[BATTLE_CONTEXT_INTS] InfoHintInjectComponent.hideHint')

    def setVisibility(self, visible):
        self.as_setVisibilityS(visible)
