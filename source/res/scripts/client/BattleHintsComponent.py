# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleHintsComponent.py
from BigWorld import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class BattleHintsComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def showHint(self, hintName, hintParams):
        battleHints = self.sessionProvider.dynamic.battleHints
        if battleHints:
            battleHints.showHint(hintName, {'param{}'.format(i):t for i, t in enumerate(hintParams, 1)})

    def hideHint(self, hintName):
        battleHints = self.sessionProvider.dynamic.battleHints
        if battleHints:
            battleHints.hideHint(hintName)
