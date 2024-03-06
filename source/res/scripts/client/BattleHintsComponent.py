# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleHintsComponent.py
import typing
import logging
from BigWorld import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.battle_hints.controller import BattleHintsController

class BattleHintsComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def showHint(self, hintName, hintParams, immediately=False):
        controller = self.sessionProvider.dynamic.battleHints
        if controller:
            controller.showHint(hintName=hintName, params={name:param for name, param in hintParams}, immediately=immediately)
        else:
            _logger.warning('No battle hints controller on show hint call.')

    def hideHint(self, hintName):
        controller = self.sessionProvider.dynamic.battleHints
        if controller:
            controller.hideHint(hintName=hintName)
        else:
            _logger.warning('No battle hints controller on hide hint call.')

    def removeHint(self, hintName, hide=False):
        controller = self.sessionProvider.dynamic.battleHints
        if controller:
            controller.removeHint(hintName=hintName, hide=hide)
        else:
            _logger.warning('No battle hints controller on remove hint call.')
