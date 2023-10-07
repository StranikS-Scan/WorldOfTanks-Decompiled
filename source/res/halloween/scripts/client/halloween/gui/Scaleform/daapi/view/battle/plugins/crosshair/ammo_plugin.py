# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/plugins/crosshair/ammo_plugin.py
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AmmoPlugin
SHELL_INF = -999

class HalloweenAmmoPlugin(AmmoPlugin):

    def _setAmmoStock(self, quantity, quantityInClip, isLow, clipState, clipReloaded=False):
        self._parentObj.as_setAmmoStockS(SHELL_INF, quantityInClip, isLow, clipState, clipReloaded)
