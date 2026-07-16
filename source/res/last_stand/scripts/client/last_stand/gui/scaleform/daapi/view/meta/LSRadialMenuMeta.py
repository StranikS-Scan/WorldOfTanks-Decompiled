# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/meta/LSRadialMenuMeta.py
from gui.Scaleform.daapi.view.battle.shared.radial_menu import RadialMenu

class LSRadialMenuMeta(RadialMenu):

    def as_setObeliskEnabledS(self, value):
        return self.flashObject.as_setObeliskEnabled(value) if self._isDAAPIInited() else None
