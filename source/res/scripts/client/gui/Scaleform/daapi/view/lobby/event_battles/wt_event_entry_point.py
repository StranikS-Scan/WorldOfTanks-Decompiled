# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_battles/wt_event_entry_point.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.meta.WTEventEntryPointMeta import WTEventEntryPointMeta
from gui.impl.lobby.wt_event.wt_event_entry_point import WTEventEntryPoint

class WTEventBattlesEntryPoint(WTEventEntryPointMeta):

    def _makeInjectView(self):
        return WTEventEntryPoint(flags=ViewFlags.COMPONENT)
