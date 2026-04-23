# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/meta/BattleHintProgressConvoyMeta.py
from last_stand.gui.scaleform.daapi.view.meta.BattleHintProgressDefenceMeta import BattleHintProgressDefenceMeta

class BattleHintProgressConvoyMeta(BattleHintProgressDefenceMeta):

    def as_setConvoyVehiclesStatusS(self, states):
        return self.flashObject.as_setConvoyVehiclesStatus(states) if self._isDAAPIInited() else None
