# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_entry_point.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.RankedBattlesEntryPointMeta import RankedBattlesEntryPointMeta
from gui.impl.lobby.ranked.ranked_entry_point import RankedEntryPoint

class RankedBattlesEntryPoint(RankedBattlesEntryPointMeta):

    def _makeInjectView(self):
        self.__view = RankedEntryPoint(flags=ViewFlags.COMPONENT)
        return self.__view
