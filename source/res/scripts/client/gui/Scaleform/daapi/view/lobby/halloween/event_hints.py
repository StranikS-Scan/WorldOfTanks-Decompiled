# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/halloween/event_hints.py
from gui.Scaleform.daapi.view.lobby.missions.linked_set.linkedset_hints import BaseHintsView
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getHalloweenBonuses

class HalloweenHintsView(BaseHintsView):

    def _getFormatter(self):
        return getHalloweenBonuses
