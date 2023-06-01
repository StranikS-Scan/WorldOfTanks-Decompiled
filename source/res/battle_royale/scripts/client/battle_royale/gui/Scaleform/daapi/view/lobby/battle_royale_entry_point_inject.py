# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/battle_royale_entry_point_inject.py
from battle_royale.gui.impl.lobby.views.battle_royale_entry_point import BattleRoyaleEntryPoint
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.ResizableEntryPointMeta import ResizableEntryPointMeta

class BattleRoyaleEntryPointInject(ResizableEntryPointMeta):

    def isSingle(self, value):
        if self.__view:
            self.__view.setIsSingle(value)

    def _makeInjectView(self):
        self.__view = BattleRoyaleEntryPoint(flags=ViewFlags.COMPONENT)
        return self.__view
