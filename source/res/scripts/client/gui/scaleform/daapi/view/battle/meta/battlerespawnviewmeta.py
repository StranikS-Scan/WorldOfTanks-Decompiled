# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/meta/BattleRespawnViewMeta.py
from gui.Scaleform.daapi.view.battle.meta.BattleComponentMeta import BattleComponentMeta

class BattleRespawnViewMeta(BattleComponentMeta):

    def py_vehicleSelected(self, vehicleID):
        raise NotImplementedError

    def onPostmortemBtnClickS(self):
        raise NotImplementedError

    def as_updateRespawnViewS(self, vehicleName, slotsStatesData):
        if self._flashObject is not None:
            self._flashObject.as_updateRespawnView(vehicleName, slotsStatesData)
        return

    def as_showRespawnViewS(self, vehicleName, slotsStatesData):
        if self._flashObject is not None:
            self._flashObject.as_showRespawnView(vehicleName, slotsStatesData)
        return

    def as_hideRespawnViewS(self):
        if self._flashObject is not None:
            self._flashObject.as_hideRespawnView()
        return

    def as_respawnViewUpdateTimerS(self, mainTimer, slots):
        if self._flashObject is not None:
            self._flashObject.as_respawnViewUpdateTimer(mainTimer, slots)
        return

    def as_initializeS(self, mainData, slots, helpText):
        if self._flashObject is not None:
            self._flashObject.as_initialize(mainData, slots, helpText)
        return

    def as_showGasAtackMode(self):
        if self._flashObject is not None:
            self._flashObject.as_showGasAtackMode()
        return
